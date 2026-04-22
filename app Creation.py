import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Data Storytelling AI", layout="wide")
st.title("📊 Data Storytelling AI Assistant")
st.markdown("Upload your dataset, and AI will analyze and explain the insights!")

# Groq API key
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

def get_ai_insight(prompt):
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": "You are a helpful data analyst assistant."},
                         {"role": "user", "content": prompt}],
            "max_tokens": 500, "temperature": 0.7
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=60)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Read file
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Optional: remove completely empty rows (only if user wants)
    if st.checkbox("Remove completely blank rows (if any)"):
        before = df.shape[0]
        df = df.dropna(how='all')
        st.info(f"Removed {before - df.shape[0]} empty rows.")
    
    st.success(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head(10))
    
    # Auto column detection
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    st.subheader("🧠 Auto Column Detection")
    st.write(f"**Numerical columns:** {num_cols}")
    st.write(f"**Categorical columns:** {cat_cols}")
    
    if num_cols:
        st.subheader("📈 Statistical Summary")
        st.dataframe(df[num_cols].describe())
    
    # Simple static charts (optional)
    with st.expander("Show basic static charts"):
        if num_cols:
            for col in num_cols[:2]:
                fig, ax = plt.subplots()
                df[col].hist(bins=10, edgecolor='black', ax=ax)
                ax.set_xlabel(col)
                st.pyplot(fig)
        if cat_cols:
            for col in cat_cols[:2]:
                fig, ax = plt.subplots()
                df[col].value_counts().head(5).plot(kind='bar', ax=ax)
                ax.set_xlabel(col)
                st.pyplot(fig)
    
    # AI Insights
    st.header("🤖 AI Insights & Storytelling")
    with st.spinner("AI analyzing..."):
        insights_prompt = f"Dataset: {df.shape[0]} rows, {df.shape[1]} columns. Numerical: {num_cols}. Categorical: {cat_cols}. Provide 3 key business insights in bullet points."
        st.subheader("💡 Key Insights")
        st.write(get_ai_insight(insights_prompt))
        
        story_prompt = f"Write a short business story (4-5 sentences) based on this dataset: {df.head(3).to_dict()}"
        st.subheader("📖 Data Story")
        st.write(get_ai_insight(story_prompt))
        
        rec_prompt = f"Suggest 3 actionable business recommendations based on this data: {df.describe().to_dict() if num_cols else 'No numerical data'}"
        st.subheader("🎯 Recommendations")
        st.write(get_ai_insight(rec_prompt))
    
    # ========== INTERACTIVE DASHBOARD ==========
    st.header("📊 Interactive Dashboard")
    st.markdown("Use filters, change chart types, and export data.")
    
    # Create a copy for dashboard
    dashboard_df = df.copy()
    
    # Sidebar filters (slicers)
    with st.sidebar:
        st.markdown("### 🎛️ Dashboard Filters")
        
        # Date filter if any date-like column exists
        date_cols = [col for col in dashboard_df.columns if 'date' in col.lower() or dashboard_df[col].dtype == 'datetime64[ns]']
        if date_cols:
            selected_date = st.selectbox("Select Date Column", date_cols)
            if selected_date:
                min_d = dashboard_df[selected_date].min()
                max_d = dashboard_df[selected_date].max()
                date_range = st.date_input("Date Range", [min_d, max_d], min_value=min_d, max_value=max_d)
                if len(date_range) == 2:
                    dashboard_df = dashboard_df[(dashboard_df[selected_date] >= pd.to_datetime(date_range[0])) & 
                                               (dashboard_df[selected_date] <= pd.to_datetime(date_range[1]))]
        
        # Categorical filters (first 3)
        for col in cat_cols[:3]:
            unique_vals = dashboard_df[col].dropna().unique().tolist()
            selected_vals = st.multiselect(f"Filter {col}", unique_vals, default=unique_vals)
            if selected_vals:
                dashboard_df = dashboard_df[dashboard_df[col].isin(selected_vals)]
        
        # Numerical range filters (first 2)
        for col in num_cols[:2]:
            low, high = float(dashboard_df[col].min()), float(dashboard_df[col].max())
            range_vals = st.slider(f"{col} range", low, high, (low, high))
            dashboard_df = dashboard_df[(dashboard_df[col] >= range_vals[0]) & (dashboard_df[col] <= range_vals[1])]
        
        st.markdown(f"**Rows after filters:** {dashboard_df.shape[0]}")
    
    # KPIs (Key Performance Indicators)
    if num_cols:
        st.subheader("📌 Key Performance Indicators (KPIs)")
        kpi_cols = st.columns(min(4, len(num_cols)))
        for i, col in enumerate(num_cols[:4]):
            kpi_cols[i].metric(label=col, value=f"{dashboard_df[col].mean():,.2f}", delta=f"Min: {dashboard_df[col].min():,.2f}")
    
    # Dynamic chart creation
    st.subheader("📈 Create Your Own Chart")
    col1, col2 = st.columns(2)
    with col1:
        chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"])
    with col2:
        if chart_type != "Histogram":
            x_axis = st.selectbox("X-axis", dashboard_df.columns)
            y_axis = st.selectbox("Y-axis", num_cols if num_cols else dashboard_df.columns)
        else:
            hist_col = st.selectbox("Column for Histogram", num_cols if num_cols else dashboard_df.columns)
    
    fig = None
    if chart_type == "Bar Chart" and x_axis and y_axis:
        fig = px.bar(dashboard_df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
    elif chart_type == "Line Chart" and x_axis and y_axis:
        fig = px.line(dashboard_df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
    elif chart_type == "Scatter Plot" and x_axis and y_axis:
        fig = px.scatter(dashboard_df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
    elif chart_type == "Histogram" and hist_col:
        fig = px.histogram(dashboard_df, x=hist_col, title=f"Distribution of {hist_col}")
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select all required columns to generate chart.")
    
    # Data table and export
    st.subheader("📋 Filtered Data (Preview)")
    st.dataframe(dashboard_df.head(100))
    
    st.subheader("💾 Export Data for Power BI / Tableau")
    csv_data = dashboard_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Data as CSV", csv_data, "dashboard_data.csv", "text/csv")
    
    st.info("💡 You can now import this CSV into Power BI or Tableau to build advanced dashboards.")
    
else:
    st.info("👈 Please upload a CSV or Excel file to begin")
