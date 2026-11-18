# 🌍 Live Earthquake Tracker

A real-time dashboard that pulls live earthquake data from the [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/) and visualizes it on an interactive map.

**[Try the live app →](https://data-analytics-portfolio-6im4jotwqda9nprm4dutwd.streamlit.app/)**

## What it does

- Pulls real-time earthquake data worldwide (no API key required)
- Plots each earthquake on an interactive map, sized and colored by magnitude
- Lets you filter by time range (past hour to past 30 days) and minimum magnitude
- Shows a magnitude-over-time chart and a raw data table
- Auto-refreshes every 5 minutes

## How I built it

I used Python for the data pipeline (`requests` to pull the live feed, `pandas` to clean it), `Plotly` for the interactive map and charts, and `Streamlit` to turn it into a shareable web app.

## Tech stack

- Python
- Streamlit
- Plotly
- pandas
- USGS Earthquake API (GeoJSON feed)

## Running it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data source

[USGS Earthquake Hazards Program](https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/) — public, free, updated in near real-time.
