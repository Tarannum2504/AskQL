# 🤖 AskQL: Production-Grade AI Data Analyst

AskQL is a powerful, AI-native analytics platform that transforms natural language questions into accurate SQL queries and stunning visualizations. Built with **Google Gemini 1.5/2.5 Flash**, it provides a seamless "talk to your data" experience with a focus on security, reliability, and explainability.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=flat-square&logo=google-gemini&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## 🌟 Key Features

- **Natural Language to SQL**: Convert complex English questions into optimized SQLite queries instantly.
- **Dynamic Schema Mapping**: Automatically detects columns, data types, and sample data from any uploaded CSV or Excel file.
- **SQL Safety Layer**: A robust validation engine blocks destructive commands (DROP, DELETE, UPDATE) and ensures read-only access.
- **Self-Correction Loop**: If a query fails, the AI automatically analyzes the error and self-corrects the SQL in real-time.
- **Interactive Visualizations**: Powered by **Plotly**, featuring an AI-suggested chart type with a manual override dropdown (Bar, Line, Pie, Scatter, Histogram).
- **Confidence Scoring**: Transparent "High/Medium/Low" confidence levels for every query, with built-in ambiguity detection.

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Premium UI/UX with Glassmorphism)
- **Intelligence**: Google Generative AI (Gemini API)
- **Database**: SQLite (In-memory)
- **Visuals**: Plotly Interactive Charts
- **Parsing**: SQLParse & Pandas

## 🚀 Getting Started

### 1. Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/Tarannum2504/AskQL.git
cd AskQL
pip install -r requirements.txt
```

### 2. Configuration

Create a `.streamlit/secrets.toml` file in the root directory and add your Google Gemini API Key:

```toml
GEMINI_API_KEY = "your_api_key_here"
```

### 3. Launch the App

```bash
streamlit run app.py
```

## 💡 Example Queries

- *"Show me the top 10 rows by revenue."*
- *"What is the average age of passengers who survived?"*
- *"Count entries grouped by category and show a bar chart."*
- *"List all records where the status is 'Pending' and age is above 30."*

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

Built with ❤️ by Tarannum2504
