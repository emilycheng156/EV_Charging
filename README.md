⚡ EV Charging Demand & Forecast Dashboard

A full end-to-end analytics project combining SQL, Python forecasting, and Tableau

📌 Overview

This project analyzes electric vehicle (EV) charging behavior across five major U.S. cities and builds a complete analytics workflow, including:

Data ingestion & cleaning

Feature engineering & aggregation

Time-series forecasting using SARIMAX

BigQuery SQL modeling

Interactive Tableau dashboard

Behavioral, temporal, and environmental insights

The final deliverable is a modern, blue-themed Tableau dashboard with KPIs, forecasting visualizations, and behavior analysis.

🎯 Goals

Understand EV charging usage patterns across different cities

Explore how weather (especially temperature) impacts charging demand

Build a short-term demand forecasting model

Create operational dashboards for real-time monitoring and planning

Demonstrate a full analytics workflow suitable for real-world data roles

🧠 Key Findings

Total Sessions: 1,320

Total Energy Delivered: 53,474 kWh

Charging Revenue: $29,767.78

Weekday Behavior: Stable mid-week activity with weekend drops

Temperature Relationship: Slight positive correlation; colder cities show larger variability

Forecasting: City-level SARIMAX model predicts 7-day demand with confidence intervals

City Differences:

LA & SF: stable patterns

Chicago & NY: strong weather sensitivity

Houston: moderate, sometimes spiky usage

🛠 Tech Stack
Layer	Tools
Data Storage	Google BigQuery
Modeling & Feature Engineering	Python, Pandas, Statsmodels
Forecasting	SARIMAX
Visualization	Tableau
Scripting	VS Code / Jupyter
🗂 Project Structure
📁 ev-charging-dashboard
│
├── ev_charging_patterns.csv        # Raw dataset
├── forecast_to_bq.py               # Python script: model → BQ upload
├── EV_Dashboard.pptx               # Project slides & summary
└── README.md                       # Documentation (this file)

🔮 Forecasting Pipeline (Python → BigQuery)

The script forecast_to_bq.py:

Loads cleaned daily session data from BigQuery

Builds a SARIMAX model per city

Generates 7-day ahead forecasts

Includes upper/lower prediction intervals

Uploads results back into BigQuery as forecasts_daily

This enables Tableau to pull live predictions for visualization.

🧩 SQL Modeling (BigQuery)

The SQL layer prepares the data for analysis:

Staging Tables: raw loading

Cleaned Tables: converted timestamps, standardized text

Daily Aggregations: sessions, energy, temperature

Forecast Views: joins actual + predicted demand

Dashboard Views: pre-aggregated metrics for Tableau

This creates a robust analytics warehouse similar to modern data stacks.

📊 Tableau Dashboard

The dashboard includes:

✔ KPI Summary

Total sessions

Total energy delivered

Revenue

Dynamic city/date filters

✔ Forecast Visualization

Actual vs predicted sessions

7-day forecast window

Shaded confidence intervals

✔ Behavioral Analysis

Temperature vs Sessions scatterplot

Calendar heatmap of daily activity

Cross-city comparisons

✔ Clean Modern Layout

Blue theme

Minimal clutter

Interactive filters

Clear visual storytelling

💡 What I Learned

Time-series forecasting using SARIMAX

BigQuery SQL view modeling + feature engineering

Tableau dashboard design principles

Environmental behavior analysis

How to combine SQL + Python + Tableau into one cohesive product

Communicating data insights visually & professionally

🚀 Future Enhancements

Longer-range forecasting (Prophet, XGBoost, LSTM)

Real-time streaming data (Pub/Sub)

Geospatial map of charging stations

Charger-level peak demand analysis

User segmentation (clustering commuter vs traveler)

Predictive maintenance using operational data

📎 Project Deliverables

📊 Tableau Dashboard (screenshots or link)

🧮 Forecasting Script (forecast_to_bq.py)

🗄 SQL Data Model (views, aggregations)

🎞 Presentation: EV_Dashboard.pptx
