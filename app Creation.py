import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import plotly.express as px
import plotly.graph_objects as go

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Data Storytelling AI", layout="wide")

# ========== CUSTOM CSS FOR AESTHETIC DESIGN ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        background: linear-gradient(135deg, #f8faff 0%, #f0f4fe 100%);
        border-radius: 32px;
        padding: 2rem 2rem;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: #ffffffdd;
        backdrop-filter: blur(10px);
        border-right: 1px solid #e2e8f0;
        border-radius: 0 20px 20px 0;
        box-shadow: 4px 0 12px rgba(0,0,0,0.02);
    }
    
    .section-header {
        background: linear-gradient(90deg, #ffffff, #f0f4fe);
        padding: 12px 16px;
        border-radius: 16px;
        margin: 24px 0 16px;
        border-left: 5px solid #4a6cf7;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .section-header h3 {
        margin: 0;
        font-weight: 600;
        color: #1f2a4e;
    }
    
    .kpi-card {
        background-color: white;
        padding: 16px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        transition: transform 0.2s;
        border: 1px solid #eef2ff;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }
    .kpi-label {
        font-size: 0.9rem;
        font-weight: 500;
        color: #4a5568;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3a6e;
        margin-top: 6px;
    }
    
    .stButton button {
        background-color: #4a6cf7;
        color: white;
        border-radius: 40px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        border: none;
        transition: 0.2s;
    }
    .stButton button:hover {
        background-color: #3b5bdb;
        transform: scale(1.02);
    }
    
    .dataframe {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# Helper for section headers with stickers
def section_header(title, icon):
    st.markdown(f"<div class='section-header'><h3>{icon} {title}</h3></div>", unsafe_allow_html=True)

# ========== APP TITLE WITH STICKER ==========
st.markdown("<h1 style='text-align: center; font-weight: 700; background: linear-gradient(120deg, #2d3a6e, #4a6cf7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>📊 Data Storytelling AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4a5568; margin-bottom: 2rem;'>🚀 Upload your dataset, and AI will analyze and explain the insights!</p>", unsafe_allow_html=True)

# ========== GROQ API ==========
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

def get_ai_insight(prompt):
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": "You are a helpful data analyst assistant."},
                         {"role": "user", "content": prompt}],
            "max_tokens": 800,
            "temperature": 0.7
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=60)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# ========== FILE UPLOAD ==========
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    cleaned_df = df.copy()
    
    st.success("✅ File uploaded successfully!")
    
    # ========== DATA PRESENTATION ==========
    section_header("Data Presentation", "🔍")
    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    
    # ========== DATA SUMMARY ==========
    section_header("Data Summary", "📋")
    st.write(f"**Rows:** {df.shape[0]}  |  **Columns:** {df.shape[1]}")
    
    # ========== COLUMN ANALYSIS ==========
    section_header("Column Analysis", "🧠")
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Numerical columns ({len(num_cols)})**")
        st.write(num_cols if num_cols else "None")
    with col2:
        st.markdown(f"**Categorical columns ({len(cat_cols)})**")
        st.write(cat_cols if cat_cols else "None")
    
    # ========== STATISTICS SUMMARY ==========
    if num_cols:
        section_header("Statistics Summary", "📈")
        st.dataframe(df[num_cols].describe(), use_container_width=True)
    
    # ========== BASIC STATIC CHARTS ==========
    with st.expander("📉 Show basic static charts"):
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
    
    # ========== AI STORYTELLING ==========
    section_header("AI Storytelling", "🤖")
    with st.spinner("AI is thinking..."):
        data_summary = f"""
        Dataset has {df.shape[0]} rows and {df.shape[1]} columns.
        Numerical columns: {num_cols if num_cols else 'None'}
        Categorical columns: {cat_cols if cat_cols else 'None'}
        Sample data (first 5 rows): {df.head(5).to_dict()}
        """
        
        insights_prompt = f"Based on this data: {data_summary}. Provide 5 to 6 key business insights in bullet points."
        st.markdown("#### 💡 Key Insights")
        st.write(get_ai_insight(insights_prompt))
        
        story_prompt = f"Based on this dataset: {data_summary}. Write a detailed, well-structured business story (6-8 sentences) that highlights trends, patterns, and actionable takeaways."
        st.markdown("#### 📖 Data Story")
        st.write(get_ai_insight(story_prompt))
        
        rec_prompt = f"Based on this data: {data_summary}. Suggest 5 actionable business recommendations, numbered 1 to 5."
        st.markdown("#### 🎯 Recommendations")
        st.write(get_ai_insight(rec_prompt))
    
    # ========== INTERACTIVE DASHBOARD ==========
    section_header("Interactive Dashboard", "📊")
    st.markdown("Use the sidebar filters to explore data dynamically.")
    
    dashboard_df = df.copy()
    
    # ========== SIDEBAR FILTERS ==========
    with st.sidebar:
        st.markdown("### 🎛️ Dashboard Controls")
        if cat_cols:
            cat_slicer = st.selectbox("Filter by Category", ["None"] + cat_cols)
            if cat_slicer != "None":
                unique_vals = dashboard_df[cat_slicer].dropna().unique().tolist()
                selected_vals = st.multiselect(f"Select {cat_slicer}", unique_vals, default=unique_vals)
                if selected_vals:
                    dashboard_df = dashboard_df[dashboard_df[cat_slicer].isin(selected_vals)]
        
        if num_cols:
            num_slicer = st.selectbox("Filter by Numerical Range", ["None"] + num_cols)
            if num_slicer != "None":
                min_val = float(dashboard_df[num_slicer].min())
                max_val = float(dashboard_df[num_slicer].max())
                range_vals = st.slider(f"Range for {num_slicer}", min_val, max_val, (min_val, max_val))
                dashboard_df = dashboard_df[(dashboard_df[num_slicer] >= range_vals[0]) & (dashboard_df[num_slicer] <= range_vals[1])]
        
        st.markdown(f"**Rows after filter:** {dashboard_df.shape[0]}")
    
    # ========== KPIs ==========
    st.subheader("📌 Key Performance Indicators (KPIs)")
    if num_cols:
        kpi_columns = num_cols[:4]
        cols_kpi = st.columns(len(kpi_columns))
        for i, col in enumerate(kpi_columns):
            if col in dashboard_df.columns:
                avg_val = dashboard_df[col].mean()
                with cols_kpi[i]:
                    st.markdown(f"""
                    <div class='kpi-card'>
                        <div class='kpi-label'>{col}</div>
                        <div class='kpi-value'>{avg_val:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No numerical columns for KPIs.")
    
    # ========== CHARTS ==========
    st.subheader("📈 Interactive Charts")
    
    # Row 1: Bar + Donut
    if cat_cols and num_cols:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📊 Bar Chart**")
            bar_cat = st.selectbox("Bar - Category", cat_cols, key="bar_cat")
            bar_num = st.selectbox("Bar - Value", num_cols, key="bar_num")
            if bar_cat and bar_num:
                agg_bar = dashboard_df.groupby(bar_cat)[bar_num].mean().reset_index()
                fig_bar = px.bar(agg_bar, x=bar_cat, y=bar_num, title=f"Average {bar_num} by {bar_cat}")
                fig_bar.update_layout(plot_bgcolor='#f8faff', paper_bgcolor='#f8faff', margin=dict(t=40, b=20))
                st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            st.markdown("**🍩 Donut Chart**")
            pie_cat = st.selectbox("Category for Donut", cat_cols, key="pie_cat")
            if pie_cat:
                pie_data = dashboard_df[pie_cat].value_counts().reset_index()
                pie_data.columns = [pie_cat, 'count']
                fig_pie = px.pie(pie_data, names=pie_cat, values='count', hole=0.4, title=f"Distribution of {pie_cat}")
                fig_pie.update_layout(plot_bgcolor='#f8faff', paper_bgcolor='#f8faff')
                st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Need categorical and numerical columns for bar/donut charts.")
    
    # Row 2: Line + Funnel
    if num_cols:
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**📈 Line Chart**")
            line_x = st.selectbox("X axis (any column)", dashboard_df.columns, key="line_x")
            line_y = st.selectbox("Y axis (numerical)", [c for c in num_cols if c in dashboard_df.columns], key="line_y")
            if line_x and line_y:
                try:
                    sorted_df = dashboard_df.sort_values(by=line_x)
                    fig_line = px.line(sorted_df, x=line_x, y=line_y, title=f"{line_y} vs {line_x}")
                    fig_line.update_layout(plot_bgcolor='#f8faff', paper_bgcolor='#f8faff')
                    st.plotly_chart(fig_line, use_container_width=True)
                except:
                    st.warning("Could not create line chart. Try a different X column.")
        with col4:
            if cat_cols and num_cols:
                st.markdown("**📊 Funnel Chart**")
                funnel_stage = st.selectbox("Stage (Category)", cat_cols, key="funnel_cat")
                funnel_value = st.selectbox("Value (Numerical)", num_cols, key="funnel_val")
                if funnel_stage and funnel_value:
                    funnel_df = dashboard_df.groupby(funnel_stage)[funnel_value].sum().reset_index()
                    fig_funnel = px.funnel(funnel_df, x=funnel_value, y=funnel_stage, title=f"Funnel: {funnel_value} by {funnel_stage}")
                    fig_funnel.update_layout(plot_bgcolor='#f8faff', paper_bgcolor='#f8faff')
                    st.plotly_chart(fig_funnel, use_container_width=True)
            else:
                st.info("Need one categorical and one numerical column for funnel chart.")
    else:
        st.info("No numerical columns for charts.")
    
    # ========== DATA TABLE & EXPORT ==========
    st.subheader("📋 Filtered Data (Preview)")
    st.dataframe(dashboard_df.head(100), use_container_width=True)
    
    csv_cleaned = cleaned_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Cleaned Data CSV", csv_cleaned, "cleaned_data.csv", "text/csv")
    
    st.info("💡 You can import the downloaded CSV into Power BI or Tableau for advanced dashboards.")
else:
    st.info("👈 Please upload a CSV or Excel file to begin")
