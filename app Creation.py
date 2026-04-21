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