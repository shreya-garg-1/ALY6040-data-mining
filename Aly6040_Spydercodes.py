import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("mayo_clinic_performance_data.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df.dropna(subset=["Date"])

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Data")
locations = st.sidebar.multiselect("Select Location(s):", options=df["Location"].unique(), default=df["Location"].unique())
departments = st.sidebar.multiselect("Select Department(s):", options=df["Department"].unique(), default=df["Department"].unique())
date_range = st.sidebar.date_input("Select Date Range:", [df["Date"].min(), df["Date"].max()])

# Apply filters
filtered_df = df[
    (df["Location"].isin(locations)) &
    (df["Department"].isin(departments)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

# Page Title
st.title("🏥 Mayo Clinic Operational Dashboard")
st.markdown("A real-time overview of patient care and service performance across departments.")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📌 Department Insights", "📋 Data Preview"])

with tab1:
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Wait Time (min)", f"{filtered_df['Avg_Wait_Time_Min'].mean():.1f}")
    col2.metric("Avg Treatment Cost ($)", f"${filtered_df['Avg_Treatment_Cost_USD'].mean():,.2f}")
    col3.metric("Patient Satisfaction", f"{filtered_df['Patient_Satisfaction_Score'].mean():.2f} / 5")
    col4.metric("Appointments Available", f"{filtered_df['Appointments_Available'].sum()}")

    # Line chart - Wait time trend
    wait_trend = filtered_df.groupby("Date")["Avg_Wait_Time_Min"].mean().reset_index()
    wait_trend.sort_values("Date", inplace=True)
    fig_wait = px.line(wait_trend, x="Date", y="Avg_Wait_Time_Min", title="📈 Average Wait Time Over Time")
    st.plotly_chart(fig_wait)

    # Bar chart - Avg cost by department
    cost_by_dept = filtered_df.groupby("Department")["Avg_Treatment_Cost_USD"].mean().reset_index()
    fig_cost = px.bar(cost_by_dept, x="Department", y="Avg_Treatment_Cost_USD", title="💰 Avg Treatment Cost by Department", text_auto=True)
    st.plotly_chart(fig_cost)

    # Pie chart - Appointments by location
    appointments_by_loc = filtered_df.groupby("Location")["Appointments_Available"].sum().reset_index()
    fig_pie = px.pie(appointments_by_loc, values="Appointments_Available", names="Location", title="📊 Appointments Distribution by Location")
    st.plotly_chart(fig_pie)

with tab2:
    # Satisfaction by department
    satisfaction = filtered_df.groupby("Department")["Patient_Satisfaction_Score"].mean().reset_index()
    fig_satis = px.bar(satisfaction, x="Department", y="Patient_Satisfaction_Score", title="⭐ Avg Satisfaction by Department", text_auto=True)
    st.plotly_chart(fig_satis)

    # Inventory-style heatmap for Appointments Available
    pivot = filtered_df.pivot_table(index="Location", columns="Department", values="Appointments_Available", aggfunc="sum")
    st.subheader("🗺 Appointments Heatmap by Location and Department")
    st.dataframe(pivot.style.background_gradient(cmap="Blues"))

with tab3:
    st.subheader("📋 Filtered Data Preview")
    st.dataframe(filtered_df.head(50))
    st.download_button(
        label="📥 Download Filtered Data",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="Mayo_Filtered_Data.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption("Developed for ALY6040 Assignment 4 | Mayo Clinic Performance Dashboard")
