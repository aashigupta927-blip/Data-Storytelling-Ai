# 📊 Data Storytelling AI Assistant

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.0-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/Groq-API-orange.svg)](https://groq.com)
[![Deployed](https://img.shields.io/badge/Deployed-Streamlit%20Cloud-brightgreen)](https://data-storytelling-ai-5fxuee8jse2ugtxvyto5xc.streamlit.app)

**Turn raw data into decisions – automatically.**  
Upload any CSV/Excel file and let AI analyze, visualize, and explain insights in plain English.  
No coding, no manual chart selection. Built as part of my **ALGONIVE Internship Task**.

🔗 **Live Demo:**  
https://data-storytelling-ai-5fxuee8jse2ugtxvyto5xc.streamlit.app

---

## ✨ Features

| Feature | Description |
|--------|------------|
| 📁 **Smart Upload** | Accepts CSV / Excel files (up to 200MB) |
| 🧠 **Auto Column Detection** | Identifies numerical, categorical & date columns |
| 📈 **Statistical Summary** | Mean, median, min, max, standard deviation |
| 📊 **Auto Visualizations** | Histograms, bar charts, correlation heatmap, plus interactive charts |
| 💡 **AI Insights** | 5–6 key business insights in bullet points |
| 📖 **Storytelling Mode** | Detailed narrative report (6–8 sentences) |
| 🎯 **Recommendations** | 5 actionable business suggestions |
| 🎛️ **Interactive Dashboard** | Slicers, KPIs, dynamic charts, data export |
| 💾 **Export** | Download cleaned CSV for Power BI / Tableau |

> **No manual chart selection. No coding. Just upload and get insights.**

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Frontend & Backend** | Streamlit |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn, Plotly |
| **AI / LLM** | Groq API (Llama 3.3 70B) |
| **Language** | Python 3.10+ |
| **Deployment** | Streamlit Cloud |

---

## 🚀 How It Works (User View)

1. Open the app link in any browser  
2. Upload your CSV or Excel file  
3. The app automatically:
   - Shows data preview & column types  
   - Displays statistical summary  
   - Generates charts  
   - Creates AI insights, story & recommendations  
   - Opens an interactive dashboard  

4. Read insights in plain English 🎯

---

## 📦 Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/data-storytelling-ai.git
cd data-storytelling-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add Groq API Key
mkdir .streamlit
echo "GROQ_API_KEY='gsk_xxxx'" > .streamlit/secrets.toml

# 5. Run app
streamlit run app.py

🤝 Contributing

Suggestions and feedback are welcome.
Feel free to open an issue or fork the repo.

📞 Connect with Me

I’m actively looking for Data Analyst Intern roles.
Let’s connect!

🙏 Acknowledgements
ALGONIVE – Internship task inspiration
Groq – Free LLM API
Streamlit – App development framework
DeepSeek AI – Debugging support
📄 License

This project is licensed under the MIT License.

<div align="center">

⭐ If you like this project, please star the repository! ⭐

</div> ```
