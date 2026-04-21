# 📊 Data Storytelling AI Assistant

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/Groq-API-orange.svg)](https://groq.com)

**Turn raw data into decisions – automatically.**  
Upload any CSV/Excel file and let AI analyze, visualize, and explain insights in plain English. No coding, no manual chart selection. Built as part of my **ALGONIVE Internship Task**.

🔗 **Live Demo:** [https://data-storytelling-ai.streamlit.app](https://data-storytelling-ai.streamlit.app) *(replace with your actual link)*

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📁 **Smart Upload** | Accepts CSV / Excel files (up to 200MB) |
| 🧠 **Auto Column Detection** | Identifies numerical, categorical & date columns |
| 📈 **Statistical Summary** | Mean, median, min, max, standard deviation |
| 📊 **Auto Visualizations** | Histograms, bar charts, correlation heatmap |
| 💡 **AI Insights** | 3 key business insights in bullet points |
| 📖 **Storytelling Mode** | Narrative report (4-5 sentences) |
| 🎯 **Recommendations** | Actionable business suggestions |

> **No manual chart selection. No coding. Just upload and get insights.**

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Frontend & Backend** | Streamlit |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn |
| **AI / LLM** | Groq API (free tier) – Llama 3.3 70B |
| **Language** | Python 3.10+ |
| **Deployment** | Streamlit Cloud |

---

## 🚀 How It Works (User View)

1. Open the app link in any browser.
2. Click **"Upload CSV or Excel file"** and select your dataset.
3. The app automatically:
   - Shows data preview & column types
   - Displays statistical summary
   - Generates charts (histograms, bar charts, heatmap)
   - Calls AI to produce insights, a story, and recommendations
4. Read the results – all in plain English.

---

## 📦 Local Installation

Want to run this on your own machine? Follow these steps:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/data-storytelling-ai.git
cd data-storytelling-ai

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your Groq API key
mkdir .streamlit
echo "GROQ_API_KEY = 'gsk_xxxx'" > .streamlit/secrets.toml

# 5. Run the app
streamlit run app.py
