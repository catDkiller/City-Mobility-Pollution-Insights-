import streamlit as st
import pandas as pd
import numpy as np

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="🚦 City Mobility & Pollution Insights", layout="wide")

# =============================
# SAMPLE LOCAL DATASET
# (Replace with your actual df after testing)
# =============================
data = {
    "Record_ID": range(1, 11),
    "Timestamp": pd.date_range(start="2025-01-01", periods=10, freq="H"),
    "City": ["Delhi", "Mumbai", "Delhi", "Chennai", "Delhi", "Kolkata", "Mumbai", "Chennai", "Delhi", "Kolkata"],
    "Camera_ID": np.random.randint(100, 999, 10),
    "Road_Type": ["Highway","Main Road","Street","Street","Highway","Main Road","Street","Highway","Street","Main Road"],
    "Direction": ["North","South","East","West","North","East","South","West","North","East"],
    "Vehicle_Type": ["Car","Bike","Truck","Bicycle","Car","Truck","Bike","Car","Bicycle","Truck"],
    "Speed_KMPH": np.random.randint(10, 100, 10),
    "Road_Occupancy_Percent": np.random.randint(20, 90, 10),
    "Congestion_Index": np.random.randint(10, 100, 10),
    "Travel_Delay_Minutes": np.random.randint(1, 30, 10),
    "Weather_Condition": ["Rain","Fog","Clear","Rain","Fog","Clear","Clear","Rain","Fog","Clear"],
    "Incident_Type": ["Accident","None","None","Construction","None","Accident","None","None","Construction","None"],
    "Fine_Issued": np.random.choice([0,1], 10),
    "License_Plate": ["DL01A1234","MH02B5678","DL03C1111","TN09X3333","DL07K9876","WB02Q2222","MH09G5555","TN07L4444","DL08M7777","WB01Z8888"]
}

df = pd.DataFrame(data)

# =============================
# CLEANING & FEATURE ENGINEERING
# (Your original code)
# =============================
str_cols = df.select_dtypes(include=['object']).columns
df[str_cols] = df[str_cols].apply(lambda x: x.str.strip().str.title())

df['License_Plate'] = df['License_Plate'].str.upper()
df['Incident_Type'] = df['Incident_Type'].str.replace(r'[^A-Za-Z ]','', regex=True)

df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
df['Hour'] = df['Timestamp'].dt.hour
df['Day'] = df['Timestamp'].dt.day_name()
df['Month'] = df['Timestamp'].dt.month_name()

df['Peak_Hour'] = df['Hour'].apply(lambda h: 'Peak' if h in range(8,12) or h in range(17,21) else 'Off-Peak')

df['Weather_Condition'] = (
    df['Weather_Condition']
    .str.replace(r'(Rain|Rainy|Light Rain)+', 'Rain', regex=True)
    .str.replace(r'(Foggy|Mist|Haze)+', 'Fog', regex=True)
)

df['Vehicle_Type'] = df['Vehicle_Type'].replace({
    'Motorcycle':'Bike',
    'Cycle':'Bicycle',
    'Lorry':'Truck'
})

df['Speed_Category'] = pd.cut(
    df['Speed_KMPH'],
    bins=[0, 20, 40, 60, 120],
    labels=['Very Slow', 'Slow', 'Normal', 'Fast']
)

df['Is_Congested'] = df['Congestion_Index'].apply(lambda x: 1 if x >= 70 else 0)
df['Delay_Factor'] = df['Travel_Delay_Minutes'] / (df['Speed_KMPH'] + 1)

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("🔍 Filter Data")

city_filter = st.sidebar.multiselect("City", options=df["City"].unique(), default=df["City"].unique())
vehicle_filter = st.sidebar.multiselect("Vehicle Type", options=df["Vehicle_Type"].unique(), default=df["Vehicle_Type"].unique())
weather_filter = st.sidebar.multiselect("Weather", options=df["Weather_Condition"].unique(), default=df["Weather_Condition"].unique())
peak_filter = st.sidebar.radio("Hour Type", ["All", "Peak", "Off-Peak"])

filtered_df = df[
    (df["City"].isin(city_filter)) &
    (df["Vehicle_Type"].isin(vehicle_filter)) &
    (df["Weather_Condition"].isin(weather_filter))
]

if peak_filter != "All":
    filtered_df = filtered_df[filtered_df["Peak_Hour"] == peak_filter]

# =============================
# MAIN DASHBOARD
# =============================
st.title("🚦 City Mobility & Pollution Insights Platform")

st.subheader("📊 Filtered Data Preview")
st.dataframe(filtered_df, use_container_width=True)

# Key Stats
st.subheader("📈 Quick Stats")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Speed", f"{filtered_df['Speed_KMPH'].mean():.1f} km/h")
col2.metric("Avg Congestion", f"{filtered_df['Congestion_Index'].mean():.1f}")
col3.metric("Peak Hour Records", filtered_df[filtered_df["Peak_Hour"]=="Peak"].shape[0])
col4.metric("Incidents", filtered_df[filtered_df['Incident_Type']!="None"].shape[0])

# =============================
# CHARTS
# =============================
st.subheader("📉 Speed Distribution")
st.bar_chart(filtered_df["Speed_KMPH"])

st.subheader("🚗 Vehicle Count by Type")
st.bar_chart(filtered_df["Vehicle_Type"].value_counts())

st.subheader("🌧 Weather Impact")
st.bar_chart(filtered_df.groupby("Weather_Condition")["Congestion_Index"].mean())

