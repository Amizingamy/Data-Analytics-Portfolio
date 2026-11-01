"""
Live Earthquake Tracker
------------------------
Pulls real-time earthquake data from the USGS Earthquake API and
displays it as an interactive map + charts using Streamlit and Plotly.

Data source: https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/
No API key required.
"""

import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------
st.set_page_config(page_title="Live Earthquake Tracker", layout="wide")
st.title("🌍 Live Earthquake Tracker")
st.caption("Real-time earthquake data from the USGS Earthquake Hazards Program")

# ---------------------------------------------------------
# Time range selector -> maps to a USGS feed URL
# ---------------------------------------------------------
FEEDS = {
    "Past Hour": "all_hour",
    "Past Day": "all_day",
    "Past 7 Days": "all_week",
    "Past 30 Days": "all_month",
}

time_range = st.sidebar.selectbox("Time range", list(FEEDS.keys()), index=1)
min_magnitude = st.sidebar.slider("Minimum magnitude", 0.0, 8.0, 2.5, 0.1)

FEED_URL = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{FEEDS[time_range]}.geojson"


# ---------------------------------------------------------
# Fetch + clean data (cached so we don't hammer the API)
# ---------------------------------------------------------
@st.cache_data(ttl=300)  # refresh every 5 minutes
def load_data(url: str) -> pd.DataFrame:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    geojson = response.json()

    rows = []
    for feature in geojson["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]  # [lon, lat, depth]
        rows.append(
            {
                "place": props.get("place"),
                "magnitude": props.get("mag"),
                "time": pd.to_datetime(props.get("time"), unit="ms"),
                "longitude": coords[0],
                "latitude": coords[1],
                "depth_km": coords[2],
                "url": props.get("url"),
            }
        )

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["magnitude", "latitude", "longitude"])
    return df


try:
    df = load_data(FEED_URL)
except requests.exceptions.RequestException as e:
    st.error(f"Couldn't reach the USGS API right now: {e}")
    st.stop()

# Apply magnitude filter
df = df[df["magnitude"] >= min_magnitude].sort_values("time", ascending=False)

if df.empty:
    st.warning("No earthquakes match the current filters. Try lowering the minimum magnitude.")
    st.stop()

# ---------------------------------------------------------
# Top-line stats
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Earthquakes shown", len(df))
col2.metric("Strongest magnitude", f"{df['magnitude'].max():.1f}")
col3.metric("Average depth (km)", f"{df['depth_km'].mean():.1f}")

# ---------------------------------------------------------
# Map
# ---------------------------------------------------------
st.subheader("Map")
fig_map = px.scatter_map(
    df,
    lat="latitude",
    lon="longitude",
    size="magnitude",
    color="magnitude",
    color_continuous_scale="YlOrRd",
    size_max=25,
    zoom=1,
    hover_name="place",
    hover_data={"magnitude": True, "depth_km": True, "latitude": False, "longitude": False},
    map_style="carto-darkmatter",
    height=550,
)
fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig_map, width="stretch")

# ---------------------------------------------------------
# Magnitude over time
# ---------------------------------------------------------
st.subheader("Magnitude over time")
fig_scatter = px.scatter(
    df,
    x="time",
    y="magnitude",
    color="magnitude",
    color_continuous_scale="YlOrRd",
    hover_name="place",
)
st.plotly_chart(fig_scatter, width="stretch")

# ---------------------------------------------------------
# Raw data table
# ---------------------------------------------------------
with st.expander("See raw data"):
    st.dataframe(
        df[["time", "place", "magnitude", "depth_km", "url"]].reset_index(drop=True)
    )

st.caption("Data updates automatically every 5 minutes. Source: USGS Earthquake Hazards Program.")
