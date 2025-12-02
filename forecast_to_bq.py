#!/usr/bin/env python3
"""
EV Charging Forecasts → BigQuery
- Reads:   ev_forecast.v_city_daily_features
- Writes:  ev_forecast.forecasts_daily  (FLOATs for easy Arrow/BQ interop)
Usage:
  python forecast_to_bq.py --project YOUR_PROJECT_ID --dataset ev_forecast --horizon 7
Auth options:
  1) gcloud auth application-default login
  2) export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
"""

import os
import sys
import argparse
import warnings
from typing import List

import numpy as np
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# ---------- Config via CLI ----------
def parse_args():
    p = argparse.ArgumentParser(description="EV charging forecasts to BigQuery")
    p.add_argument("--project", required=True, help="GCP project id")
    p.add_argument("--dataset", default="ev_forecast", help="BigQuery dataset (default: ev_forecast)")
    p.add_argument("--table", default="forecasts_daily", help="Destination table name (default: forecasts_daily)")
    p.add_argument("--horizon", type=int, default=7, help="Forecast horizon in days (default: 7)")
    p.add_argument("--model_name", default="sarimax_city", help="Model label stored in output (default: sarimax_city)")
    return p.parse_args()


# ---------- BigQuery client ----------
def make_bq_client(project_id: str) -> bigquery.Client:
    key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path and os.path.exists(key_path):
        creds = service_account.Credentials.from_service_account_file(key_path)
        return bigquery.Client(project=project_id, credentials=creds)
    # Fallback to ADC (gcloud auth application-default login)
    return bigquery.Client(project=project_id)


# ---------- Forecast logic ----------
def forecast_city(df_city: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """
    df_city: index = datetime (daily freq), columns must include:
        sessions, is_weekend, ma7_sessions (filled)
    Returns DataFrame with columns [d (date), yhat, yhat_lower, yhat_upper]
    """
    y = df_city["sessions"].astype(float).fillna(0.0)
    X = df_city[["is_weekend", "ma7_sessions"]].astype(float)

    future_idx = pd.date_range(df_city.index.max() + pd.Timedelta(days=1),
                               periods=horizon, freq="D")

    # Build future exogenous features
    Xf = pd.DataFrame(index=future_idx)
    Xf["is_weekend"] = [1.0 if d.weekday() >= 5 else 0.0 for d in future_idx]
    Xf["ma7_sessions"] = float(y.tail(7).mean()) if len(y) >= 1 else 0.0

    # Fit SARIMAX; fall back to naive mean if it fails
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            m = SARIMAX(y, order=(0, 1, 1), seasonal_order=(0, 1, 1, 7),
                        exog=X, enforce_stationarity=True, enforce_invertibility=True)
            res = m.fit(disp=False)
        sf = res.get_forecast(steps=horizon, exog=Xf).summary_frame()
        sf = sf.rename(columns={"mean": "yhat", "mean_ci_lower": "yhat_lower", "mean_ci_upper": "yhat_upper"})
        sf.index.name = "dts"
        out = sf[["yhat", "yhat_lower", "yhat_upper"]].reset_index()
        out["d"] = pd.to_datetime(out["dts"]).dt.date
        out = out.drop(columns=["dts"])
    except Exception:
        # Naive fallback: 7-day mean with ±40% band
        ybar = float(y.tail(7).mean()) if len(y) > 0 else 0.0
        out = pd.DataFrame({
            "d": future_idx.date,
            "yhat": [ybar] * horizon,
            "yhat_lower": [max(0.0, 0.6 * ybar)] * horizon,
            "yhat_upper": [1.4 * ybar] * horizon
        })

    # Clip negatives (sessions can't be negative)
    for c in ["yhat", "yhat_lower", "yhat_upper"]:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0).clip(lower=0.0)
    return out


def main():
    args = parse_args()
    PROJECT, DATASET, TABLE = args.project, args.dataset, args.table
    H, MODEL = args.horizon, args.model_name

    client = make_bq_client(PROJECT)

    # Read features view
    sql = f"""
    SELECT *
    FROM `{PROJECT}.{DATASET}.v_city_daily_features`
    ORDER BY station_city, d
    """
    print("Downloading features from BigQuery...")
    cdf = client.query(sql).to_dataframe()
    if cdf.empty:
        print("No feature rows found. Check that upstream views have data.")
        sys.exit(0)

    # Prepare time index and fill features
    cdf["d"] = pd.to_datetime(cdf["d"], errors="coerce")
    cdf = cdf[cdf["d"].notna()].copy()
    results: List[pd.DataFrame] = []

    for city, g in cdf.groupby("station_city"):
        g = g.sort_values("d").set_index("d").asfreq("D")

        # fill required columns
        for col in ["sessions", "avg_temp_c", "is_weekend", "lag1_sessions", "lag7_sessions", "ma7_sessions"]:
            if col in g.columns:
                if col == "sessions":
                    g[col] = pd.to_numeric(g[col], errors="coerce").fillna(0.0)
                else:
                    g[col] = pd.to_numeric(g[col], errors="coerce").ffill().bfill()

        if len(g) < 14:
            # too little history, produce naive forecast anyway
            fc = forecast_city(g, H)
        else:
            fc = forecast_city(g, H)

        fc.insert(0, "city", str(city))
        fc["model"] = MODEL
        results.append(fc)

    if not results:
        print("No forecasts produced.")
        sys.exit(0)

    fc_all = pd.concat(results, ignore_index=True)

    # --- enforce clean dtypes before upload ---
    fc_all["city"] = fc_all["city"].astype(str)
    fc_all["model"] = fc_all["model"].astype(str)
    fc_all["d"] = pd.to_datetime(fc_all["d"], errors="coerce").dt.date

    for col in ["yhat", "yhat_lower", "yhat_upper"]:
        fc_all[col] = pd.to_numeric(fc_all[col], errors="coerce").astype(float).fillna(0.0)
    # ------------------------------------------

    # Create / overwrite destination table with FLOAT schema
    table_id = f"{PROJECT}.{DATASET}.{TABLE}"
    print(f"Writing {len(fc_all)} forecast rows to {table_id} ...")

    # Recreate table with known schema
    client.delete_table(table_id, not_found_ok=True)
    schema = [
        bigquery.SchemaField("city", "STRING"),
        bigquery.SchemaField("d", "DATE"),
        bigquery.SchemaField("yhat", "FLOAT64"),
        bigquery.SchemaField("yhat_lower", "FLOAT64"),
        bigquery.SchemaField("yhat_upper", "FLOAT64"),
        bigquery.SchemaField("model", "STRING"),
    ]
    client.create_table(bigquery.Table(table_id, schema=schema))

    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(fc_all, table_id, job_config=job_config).result()
    print("Done.")

    # Small sanity query
    chk = client.query(
        f"SELECT city, MIN(d) AS min_d, MAX(d) AS max_d, COUNT(*) AS rows "
        f"FROM `{table_id}` GROUP BY city ORDER BY city"
    ).to_dataframe()
    print(chk.to_string(index=False))


if __name__ == "__main__":
    # Quiet some noisy warnings from statsmodels on small samples
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    main()
