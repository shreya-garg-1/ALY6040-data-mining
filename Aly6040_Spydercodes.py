import streamlit as st
import pandas as pd
import plotly.express as px

# App title
st.set_page_config(page_title="Mayo Clinic Dashboard", layout="wide")
st.title("🏥 Mayo Clinic Operational Dashboard")
st.markdown("A real-time overview of patient care and service performance across departments.")

#Load data
def load_data():
    df = pd.read_csv("mayo_clinic_performance_data.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df.dropna(subset=["Date"])

# Load data function
@st.cache_data
def load_data(file):
    return pd.read_csv(file, parse_dates=['Date'])

# Main dashboard logic
    # Sidebar filters
    st.sidebar.title("🔎 Filters")
    selected_location = st.sidebar.multiselect("Select Location", df['Location'].unique(), default=df['Location'].unique())
    selected_department = st.sidebar.multiselect("Select Department", df['Department'].unique(), default=df['Department'].unique())
    selected_date = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])

    # Filtered data
    filtered_df = df[
        (df['Location'].isin(selected_location)) &
        (df['Department'].isin(selected_department)) &
        (df['Date'] >= pd.to_datetime(selected_date[0])) &
        (df['Date'] <= pd.to_datetime(selected_date[1]))
    ]

    # KPI Scorecards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Wait Time (min)", f"{filtered_df['Avg_Wait_Time_Min'].mean():.1f}")
    col2.metric("Avg Treatment Cost ($)", f"${filtered_df['Avg_Treatment_Cost_USD'].mean():,.2f}")
    col3.metric("Patient Satisfaction", f"{filtered_df['Patient_Satisfaction_Score'].mean():.2f} / 5")
    col4.metric("Appointments Available", f"{filtered_df['Appointments_Available'].sum()}")

    st.markdown("---")

    # Tabs for organizing content
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "🔍 Deep Dive"])

    with tab1:
        # Line Chart - Avg Wait Time Over Time
        fig_wait = px.line(
            filtered_df.groupby("Date")['Avg_Wait_Time_Min'].mean().reset_index(),
            x="Date", y="Avg_Wait_Time_Min", title="📈 Average Wait Time Over Time",
            labels={"Avg_Wait_Time_Min": "Wait Time (min)"}
        )
        st.plotly_chart(fig_wait, use_container_width=True)

        # Bar Chart - Treatment Cost by Department
        fig_cost = px.bar(
            filtered_df.groupby("Department")['Avg_Treatment_Cost_USD'].mean().reset_index(),
            x="Department", y="Avg_Treatment_Cost_USD", title="💰 Avg Treatment Cost by Department",
            labels={"Avg_Treatment_Cost_USD": "Cost (USD)"}
        )
        st.plotly_chart(fig_cost, use_container_width=True)

        # Pie Chart - Appointments Available by Location
        fig_appointments = px.pie(
            filtered_df.groupby("Location")['Appointments_Available'].sum().reset_index(),
            values='Appointments_Available', names='Location',
            title='📊 Appointments Distribution by Location'
        )
        st.plotly_chart(fig_appointments, use_container_width=True)

    with tab2:
        # Line Chart - Patient Satisfaction Over Time
        fig_satisfaction = px.line(
            filtered_df.groupby("Date")['Patient_Satisfaction_Score'].mean().reset_index(),
            x="Date", y="Patient_Satisfaction_Score", title="😊 Patient Satisfaction Over Time",
            labels={"Patient_Satisfaction_Score": "Satisfaction Score"}
        )
        st.plotly_chart(fig_satisfaction, use_container_width=True)

        # Bar Chart - Top 5 Departments by Appointments Available
        fig_top_departments = px.bar(
            filtered_df.groupby("Department")['Appointments_Available'].sum().sort_values(ascending=False).head(5).reset_index(),
            x="Department", y="Appointments_Available",
            title="🏥 Top 5 Departments by Appointment Availability"
        )
        st.plotly_chart(fig_top_departments, use_container_width=True)

    with tab3:
        # Heatmap-style pivot table
        st.subheader("🔥 Avg Wait Time by Department & Location")
        heatmap_data = filtered_df.pivot_table(
            values='Avg_Wait_Time_Min',
            index='Department',
            columns='Location',
            aggfunc='mean'
        )
        st.dataframe(heatmap_data.style.background_gradient(cmap='Reds'))

        # Data download
        st.download_button(
            label="⬇️ Download Filtered Data as CSV",
            data=filtered_df.to_csv(index=False),
            file_name='filtered_mayo_data.csv',
            mime='text/csv'
        )

    # Footer
    st.markdown("---")
    st.caption("Dashboard developed for Mayo Clinic performance monitoring. Built with ❤️ using Streamlit.")

  
