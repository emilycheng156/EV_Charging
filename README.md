# ⚡ EV Charging Demand & Forecast Dashboard

A compact end-to-end analytics project analyzing EV charging behavior and generating short-term demand forecasts across five major U.S. cities. The final result is an interactive Tableau dashboard supported by BigQuery SQL models and a Python SARIMAX forecasting pipeline.
##
📌 Project Summary

Processed 1,320 EV charging sessions across Chicago, Houston, Los Angeles, New York, and San Francisco.

Engineered daily features including sessions, temperature, energy consumed, and revenue.

Built city-level SARIMAX models to forecast 7 days of future charging demand.

Loaded forecast outputs into BigQuery and visualized results in Tableau.

Created a clean, blue-themed dashboard with KPIs, forecasts, and behavioral insights.
##

🔍 Key Insights

Demand Patterns: Mid-week charging is more consistent; weekends show noticeable dips.

Weather Impact: Temperature has a mild positive effect on daily charging volume, especially in colder cities.

City Variation: LA and SF show stable activity; Chicago and NY are more sensitive to temperature shifts.

Forecast Accuracy: SARIMAX captures short-term patterns well, with expanding uncertainty further out.
##

🛠 Tech Stack

Python: Pandas, Statsmodels (SARIMAX)

SQL: BigQuery for data modeling + aggregated views

Visualization: Tableau dashboard

Tools: VS Code
##

🚀 Pipeline Overview

Clean raw CSV session data.

Upload to BigQuery → create daily aggregated table.

Run forecast_to_bq.py to produce next 7-day forecasts.

Load forecasts back into BigQuery (forecasts_daily).

Connect Tableau to BigQuery → build forecast + behavior visualizations.
##

📊 Dashboard Features

KPI metrics (sessions, energy delivered, revenue)

Forecasted daily demand with confidence bands

Calendar heatmap of charging activity

Temperature vs. Sessions scatterplot

City/date filters for interactive exploration
##
📈 What I Learned

Building a Python → SQL → Tableau analytics pipeline

Designing short-term time-series forecasting models

Modeling environmental behavior (temperature effects)

Creating clean, user-friendly dashboards

Structuring SQL data models for BI dashboards
##
🔮 Future Improvements

Longer-term forecasting (Prophet / XGBoost / LSTM)

Geospatial map of city-level charging behavior

Charger-type utilization analysis

Real-time refresh pipeline
