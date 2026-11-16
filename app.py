
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Usage Analytics Dashboard",
    page_icon="🤖",
    layout="wide"
)

# ==========================================
# 2. LOAD DATA
# ==========================================

@st.cache_data
def load_data():
    df = pd.read_csv("Data.csv")

    # Clean AI Tool
    df["AI_Tool"] = (
        df["AI_Tool"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    # Standardize AI Tool names
    tool_map = {
        "chatgpt": "ChatGPT",
        "chat gpt": "ChatGPT",
        "google gemini": "Google Gemini",
        "gemini": "Google Gemini",
        "microsoft copilot": "Microsoft Copilot",
        "copilot": "Microsoft Copilot",
        "claude": "Claude",
        "perplexity ai": "Perplexity AI",
        "grammarly": "Grammarly",
        "meta ai": "Meta AI",
        "deepseek": "DeepSeek",
        "nan": "Unknown"
    }

    df["AI_Tool"] = df["AI_Tool"].apply(
        lambda x: tool_map.get(x.lower(), x)
    )

    # Clean numeric columns
    numeric_columns = [
        "Age",
        "Monthly_Income",
        "Monthly_AI_Cost",
        "AI_Usage_Hours_Per_Day",
        "Productivity_Score",
        "Accuracy_Rating",
        "Satisfaction_Score",
        "Time_Saved_Hours_Per_Week",
        "Work_or_Study_Hours_Per_Day"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.extract(
                r"(-?\d+\.?\d*)"
            )[0],
            errors="coerce"
        )

    # Clean categorical columns
    for col in ["User_Type", "Country", "Gender",
                "Education_Level", "Profession",
                "AI_Purpose", "Would_Recommend"]:
        df[col] = (
            df[col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    return df


df = load_data()

# ==========================================
# 3. DASHBOARD TITLE
# ==========================================

st.title("🤖 AI Usage Analytics Dashboard")

st.markdown(
    "### Understanding AI adoption, expenditure and productivity"
)

st.caption(
    "Interactive business intelligence dashboard "
    "developed using Python, Pandas, Streamlit and Plotly."
)

st.divider()

# ==========================================
# 4. SIDEBAR FILTERS
# ==========================================

st.sidebar.title("Dashboard Filters")

user_types = st.sidebar.multiselect(
    "Select User Type",
    sorted(df["User_Type"].unique()),
    default=sorted(df["User_Type"].unique())
)

countries = st.sidebar.multiselect(
    "Select Country",
    sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique())
)

tools = st.sidebar.multiselect(
    "Select AI Tool",
    sorted(df["AI_Tool"].unique()),
    default=sorted(df["AI_Tool"].unique())
)

# Apply filters
filtered_df = df[
    (df["User_Type"].isin(user_types)) &
    (df["Country"].isin(countries)) &
    (df["AI_Tool"].isin(tools))
].copy()

# ==========================================
# 5. KPI CALCULATIONS
# ==========================================

total_users = len(filtered_df)

avg_usage = filtered_df[
    "AI_Usage_Hours_Per_Day"
].mean()

avg_productivity = filtered_df[
    "Productivity_Score"
].mean()

avg_cost = filtered_df[
    "Monthly_AI_Cost"
].mean()

avg_time_saved = filtered_df[
    "Time_Saved_Hours_Per_Week"
].mean()

# ==========================================
# 6. DISPLAY KPI CARDS
# ==========================================

st.subheader("Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Users", f"{total_users:,}")

col2.metric(
    "Avg AI Usage",
    f"{avg_usage:.2f} hrs/day" if pd.notna(avg_usage) else "N/A"
)

col3.metric(
    "Avg Productivity",
    f"{avg_productivity:.2f}/10" if pd.notna(avg_productivity) else "N/A"
)

col4.metric(
    "Avg Monthly AI Cost",
    f"${avg_cost:,.2f}" if pd.notna(avg_cost) else "N/A"
)

col5.metric(
    "Avg Time Saved",
    f"{avg_time_saved:.2f} hrs/week"
    if pd.notna(avg_time_saved) else "N/A"
)

st.divider()

# ==========================================
# 7. AI TOOL POPULARITY
# ==========================================

st.subheader("AI Tool Adoption Analysis")

tool_counts = (
    filtered_df["AI_Tool"]
    .value_counts()
    .reset_index()
)

tool_counts.columns = ["AI_Tool", "Users"]

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        tool_counts,
        x="AI_Tool",
        y="Users",
        color="AI_Tool",
        title="Most Popular AI Tools",
        text="Users"
    )

    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.pie(
        tool_counts,
        names="AI_Tool",
        values="Users",
        title="AI Tool Usage Distribution",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 8. STUDENT VS PROFESSIONAL ANALYSIS
# ==========================================

st.subheader("Student vs Professional Analysis")

user_analysis = (
    filtered_df.groupby("User_Type")
    .agg(
        Total_Users=("User_ID", "count"),
        Average_AI_Usage=("AI_Usage_Hours_Per_Day", "mean"),
        Average_Productivity=("Productivity_Score", "mean"),
        Average_Time_Saved=("Time_Saved_Hours_Per_Week", "mean")
    )
    .reset_index()
)

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        user_analysis,
        x="User_Type",
        y="Total_Users",
        color="User_Type",
        title="Users by Category",
        text="Total_Users"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        user_analysis,
        x="User_Type",
        y="Average_AI_Usage",
        color="User_Type",
        title="Average Daily AI Usage",
        text_auto=".2f"
    )

    st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    user_analysis.round(2),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 9. AI SPENDING ANALYSIS
# ==========================================

st.subheader("AI Spending Analysis")

col1, col2 = st.columns(2)

with col1:
    spending = (
        filtered_df.groupby("AI_Tool")["Monthly_AI_Cost"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        spending,
        x="AI_Tool",
        y="Monthly_AI_Cost",
        color="AI_Tool",
        title="Average Monthly AI Cost by Tool"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    purpose_cost = (
        filtered_df.groupby("AI_Purpose")["Monthly_AI_Cost"]
        .mean()
        .reset_index()
        .sort_values("Monthly_AI_Cost", ascending=False)
    )

    fig = px.bar(
        purpose_cost,
        x="AI_Purpose",
        y="Monthly_AI_Cost",
        title="Average AI Cost by Purpose"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 10. PRODUCTIVITY ANALYSIS
# ==========================================

st.subheader("Productivity and Time Savings")

col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(
        filtered_df,
        x="AI_Usage_Hours_Per_Day",
        y="Productivity_Score",
        color="User_Type",
        hover_data=["AI_Tool", "Profession"],
        title="AI Usage vs Productivity"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        user_analysis,
        x="User_Type",
        y="Average_Time_Saved",
        color="User_Type",
        title="Average Weekly Time Saved",
        text_auto=".2f"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 11. AI PURPOSE ANALYSIS
# ==========================================

st.subheader("Why Are People Using AI?")

purpose_counts = (
    filtered_df["AI_Purpose"]
    .value_counts()
    .reset_index()
)

purpose_counts.columns = ["AI_Purpose", "Users"]

fig = px.bar(
    purpose_counts,
    x="AI_Purpose",
    y="Users",
    color="AI_Purpose",
    title="AI Usage by Purpose",
    text="Users"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 12. SATISFACTION AND RECOMMENDATION
# ==========================================

st.subheader("Customer Satisfaction Analysis")

col1, col2 = st.columns(2)

with col1:
    satisfaction = (
        filtered_df["Satisfaction_Score"]
        .mean()
    )

    st.metric(
        "Average Satisfaction Score",
        f"{satisfaction:.2f}/10"
        if pd.notna(satisfaction) else "N/A"
    )

with col2:
    recommendation = (
        filtered_df["Would_Recommend"]
        .value_counts()
        .reset_index()
    )

    recommendation.columns = ["Response", "Users"]

    fig = px.pie(
        recommendation,
        names="Response",
        values="Users",
        title="Would Users Recommend AI?"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 13. AUTOMATIC BUSINESS INSIGHTS
# ==========================================

st.subheader("Business Insights")

if not filtered_df.empty:

    popular_tool = filtered_df["AI_Tool"].mode().iloc[0]

    highest_usage_type = (
        user_analysis.dropna(subset=["Average_AI_Usage"])
        .sort_values("Average_AI_Usage", ascending=False)
    )

    st.success(
        f"Most popular AI tool in the selected data: {popular_tool}"
    )

    if not highest_usage_type.empty:
        st.info(
            f"{highest_usage_type.iloc[0]['User_Type']} users "
            f"have the highest average daily AI usage."
        )

    if pd.notna(avg_time_saved):
        st.info(
            f"Users save an average of {avg_time_saved:.2f} "
            "hours per week according to the dataset."
        )

else:
    st.warning("No records match the selected filters.")

# ==========================================
# 14. DATA TABLE AND DOWNLOAD
# ==========================================

st.subheader("Detailed User Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv_data,
    file_name="ai_usage_analysis.csv",
    mime="text/csv"
)

# ==========================================
# 15. FOOTER
# ==========================================

st.divider()

st.caption(
    "AI Usage Analytics Dashboard | "
    "Built with Python, Pandas, Streamlit and Plotly"
)
