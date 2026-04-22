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

# Groq API key (ensure your secrets.toml has GROQ_API_KEY)
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

def get_ai_insight(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a helpful data analyst assistant. Provide concise, actionable insights."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# File upload
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Read file
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ========== DATA CLEANING & ERROR FIXING ==========
    st.subheader("🧹 Data Cleaning & Preprocessing")
    
    # 1. Remove completely blank rows
    before_rows = df.shape[0]
    df = df.dropna(how='all')
    after_rows = df.shape[0]
    if before_rows > after_rows:
        st.info(f"🗑️ Removed {before_rows - after_rows} completely blank row(s).")
    
    # 2. Detect and clean date columns
    date_columns = []
    for col in df.columns:
        try:
            if 'date' in col.lower() or 'time' in col.lower() or 'datetime' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
                date_columns.append(col)
            else:
                sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                if sample and any(sep in str(sample) for sep in ['-', '/', ':', ' ']) and len(str(sample)) > 6:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    date_columns.append(col)
        except:
            pass
    if date_columns:
        st.success(f"✅ Converted {len(date_columns)} column(s) to datetime: {date_columns}")
    
    # 3. Suggest columns to remove (constant, high missing, ID-like)
    constant_cols = [col for col in df.columns if df[col].nunique() == 1 and df[col].count() > 0]
    high_missing_cols = [col for col in df.columns if df[col].isnull().sum() / len(df) > 0.5]
    id_like_cols = [col for col in df.columns if any(id_word in col.lower() for id_word in ['id', 'key', 'index', 'slno'])]
    suggested_remove = list(set(constant_cols + high_missing_cols + id_like_cols))
    
    if suggested_remove:
        st.warning(f"📌 Suggested columns to remove: {suggested_remove}")
    
    cols_to_remove = st.multiselect("Select columns to remove (optional):", options=df.columns.tolist(), default=[c for c in suggested_remove if c in df.columns])
    if cols_to_remove:
        df = df.drop(columns=cols_to_remove)
        st.success(f"✅ Removed columns: {cols_to_remove}")
    
    # 4. Fix numeric columns (convert to numbers, coerce errors)
    for col in df.columns:
        if df[col].dtype == 'object':
            converted = pd.to_numeric(df[col], errors='coerce')
            if converted.notna().sum() > 0 and converted.isna().sum() < len(df):
                old_non_numeric = df[col].notna() & converted.isna()
                if old_non_numeric.any():
                    st.warning(f"⚠️ Column '{col}' had {old_non_numeric.sum()} non-numeric value(s). Converting to NaN.")
                    df[col] = converted
    
    # 5. Cap outliers (IQR method)
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = (df[col] < lower) | (df[col] > upper)
        if outliers.any():
            st.info(f"📊 Column '{col}' has {outliers.sum()} outlier(s). Capping them.")
            df[col] = df[col].clip(lower, upper)
    
    # 6. Standardize categorical columns
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    for col in cat_cols:
        df[col] = df[col].str.strip()
        df[col] = df[col].str.lower()
    
    # 7. Remove duplicate rows
    before_dup = df.shape[0]
    df = df.drop_duplicates()
    if before_dup > df.shape[0]:
        st.info(f"🗑️ Removed {before_dup - df.shape[0]} duplicate row(s).")
    
    # Final quality report
    st.subheader("📋 Data Quality Report")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", df.shape[0])
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isnull().sum().sum())
    
    if df.shape[0] == 0:
        st.error("❌ After cleaning, no data remains. Please upload a valid dataset.")
        st.stop()
    
    st.success("✨ Data cleaning completed!")
    # ========== END DATA CLEANING ==========

    st.success("✅ File uploaded successfully!")
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head(10))
    
    st.subheader("📋 Data Summary")
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    st.subheader("🧠 Auto Column Detection")
    st.write(f"**Numerical columns:** {num_cols}")
    st.write(f"**Categorical columns:** {cat_cols}")
    
    if num_cols:
        st.subheader("📈 Statistical Summary")
        st.dataframe(df[num_cols].describe())
    
    # Static visualizations (optional)
    st.subheader("📊 Auto-Generated Visualizations")
    if num_cols:
        for col in num_cols[:3]:
            st.write(f"**Distribution of {col}**")
            fig, ax = plt.subplots()
            df[col].hist(bins=10, edgecolor='black', ax=ax)
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
    
    if cat_cols:
        for col in cat_cols[:2]:
            st.write(f"**Top categories in {col}**")
            top_cats = df[col].value_counts().head(5)
            fig, ax = plt.subplots()
            top_cats.plot(kind='bar', ax=ax)
            ax.set_xlabel(col)
            ax.set_ylabel("Count")
            st.pyplot(fig)
    
    if len(num_cols) >= 2:
        st.subheader("🔥 Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(8, 6))
        corr = df[num_cols].corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    
    # ========== AI INSIGHTS SECTION ==========
    st.header("🤖 AI Insights & Storytelling")
    
    with st.spinner("AI is analyzing your data..."):
        insights_prompt = f"""
        Dataset: {df.shape[0]} rows, {df.shape[1]} columns.
        Numerical columns: {num_cols}
        Categorical columns: {cat_cols}
        Summary stats: {df[num_cols].mean().to_dict() if num_cols else 'None'}
        Provide 3 key business insights in bullet points.
        """
        ai_insights = get_ai_insight(insights_prompt)
        st.subheader("💡 Key Insights")
        st.write(ai_insights)
        
        story_prompt = f"Write a short business story (4-5 sentences) based on this dataset summary: {df.describe().to_dict() if num_cols else 'No numerical data'}"
        ai_story = get_ai_insight(story_prompt)
        st.subheader("📖 Data Story")
        st.write(ai_story)
        
        rec_prompt = f"Suggest 3 actionable business recommendations for a company based on this data: {df.head().to_dict()}"
        ai_recs = get_ai_insight(rec_prompt)
        st.subheader("🎯 Recommendations")
        st.write(ai_recs)
    
    # ========== INTERACTIVE DASHBOARD ==========
    st.header("📊 Interactive Dashboard")
    st.markdown("Create your own charts, apply filters, and export data for Power BI / Tableau.")
    
    dashboard_df = df.copy()
    
    # Sidebar filters
    st.sidebar.markdown("### 🎛️ Dashboard Filters")
    
    # Date filter
    date_cols = [col for col in dashboard_df.columns if 'date' in col.lower() or dashboard_df[col].dtype == 'datetime64[ns]']
    if date_cols:
        date_col = st.sidebar.selectbox("Select Date Column", date_cols)
        if date_col:
            min_date = dashboard_df[date_col].min()
            max_date = dashboard_df[date_col].max()
            date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
            if len(date_range) == 2:
                dashboard_df = dashboard_df[(dashboard_df[date_col] >= pd.to_datetime(date_range[0])) & 
                                           (dashboard_df[date_col] <= pd.to_datetime(date_range[1]))]
    
    # Categorical filters
    cat_cols = dashboard_df.select_dtypes(include=['object']).columns.tolist()
    for col in cat_cols[:3]:
        unique_vals = dashboard_df[col].dropna().unique().tolist()
        selected = st.sidebar.multiselect(f"Filter {col}", unique_vals, default=unique_vals)
        if selected:
            dashboard_df = dashboard_df[dashboard_df[col].isin(selected)]
    
    # Numerical range filters
    num_cols = dashboard_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    for col in num_cols[:2]:
        min_val = float(dashboard_df[col].min())
        max_val = float(dashboard_df[col].max())
        range_vals = st.sidebar.slider(f"Range for {col}", min_val, max_val, (min_val, max_val))
        dashboard_df = dashboard_df[(dashboard_df[col] >= range_vals[0]) & (dashboard_df[col] <= range_vals[1])]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Rows after filter:** {dashboard_df.shape[0]}")
    
    # KPIs
    st.subheader("📌 Key Performance Indicators (KPIs)")
    if num_cols:
        cols = st.columns(min(len(num_cols), 4))
        for i, col in enumerate(num_cols[:4]):
            with cols[i]:
                st.metric(label=col, value=f"{dashboard_df[col].mean():,.2f}", delta=f"Min: {dashboard_df[col].min():,.2f}")
    else:
        st.info("No numerical columns for KPIs.")
    
    # Dynamic charts
    st.subheader("📈 Create Your Own Chart")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"])
    with chart_col2:
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
        st.info("Select columns to generate chart.")
    
    # Data table and export
    st.subheader("📋 Filtered Data (Preview)")
    st.dataframe(dashboard_df.head(100))
    
    st.subheader("💾 Export Data for Power BI / Tableau")
    col_export1, col_export2 = st.columns(2)
    with col_export1:
        csv_filtered = dashboard_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Filtered Data (CSV)", csv_filtered, "filtered_data.csv", "text/csv")
    with col_export2:
        csv_full = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Cleaned Data (CSV)", csv_full, "full_cleaned_data.csv", "text/csv")
    
    st.info("💡 Tip: Download the CSV and import into Power BI / Tableau for advanced dashboards.")
    # ========== END DASHBOARD ==========

else:
    st.info("👈 Please upload a CSV or Excel file to begin")