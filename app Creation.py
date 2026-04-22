import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

st.set_page_config(page_title="Data Storytelling AI", layout="wide")
st.title("📊 Data Storytelling AI Assistant")
st.markdown("Upload your dataset, and AI will analyze and explain the insights!")

# Groq API key from secrets
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

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        # ========== DATA CLEANING & ERROR FIXING ==========
    st.subheader("🧹 Data Cleaning & Preprocessing")
    
    # 1. Remove completely blank rows (all NaN)
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
        st.success(f"✅ Converted {len(date_columns)} column(s) to datetime format: {date_columns}")
    
    # 3. Remove unnecessary columns (user selection)
    constant_cols = [col for col in df.columns if df[col].nunique() == 1 and df[col].count() > 0]
    high_missing_cols = [col for col in df.columns if df[col].isnull().sum() / len(df) > 0.5]
    id_like_cols = [col for col in df.columns if any(id_word in col.lower() for id_word in ['id', 'key', 'index', 'slno'])]
    suggested_remove = list(set(constant_cols + high_missing_cols + id_like_cols))
    
    if suggested_remove:
        st.warning(f"📌 Suggested columns to remove: {suggested_remove}")
    
    cols_to_remove = st.multiselect("Select columns you want to remove (optional):", options=df.columns.tolist(), default=[c for c in suggested_remove if c in df.columns])
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
    
    # 5. Cap outliers in numeric columns (IQR method)
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = (df[col] < lower) | (df[col] > upper)
        if outliers.any():
            st.info(f"📊 Column '{col}' has {outliers.sum()} outlier(s). Capping them.")
            df[col] = df[col].clip(lower, upper)
    
    # 6. Standardize categorical columns (strip, lowercase)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
        df[col] = df[col].str.lower()
    
    # 7. Remove duplicate rows
    before_dup = df.shape[0]
    df = df.drop_duplicates()
    if before_dup > df.shape[0]:
        st.info(f"🗑️ Removed {before_dup - df.shape[0]} duplicate row(s).")
    
    # 8. Final data quality report
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
    
    st.success("✨ Data cleaning & error fixing completed!")
    # ========== END OF CLEANING ==========
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
    
    # Visualizations
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
    
    # AI Section
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
else:
    st.info("👈 Please upload a CSV or Excel file to begin")