import streamlit as st
import pandas as pd
import sqlite3
import re
import plotly.express as px
import plotly.graph_objects as go
import time
from askql_engine.schema_mapper import extract_schema
from askql_engine.llm_client import LLMClient
from askql_engine.visualization_engine import generate_visualization

# --- Page Configuration ---
st.set_page_config(
    page_title="AskQL",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AI-Native Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f111a 0%, #171b26 50%, #0d1117 100%);
        color: #e2e8f0;
    }
    
    /* Header Styling */
    .header-container {
        padding: 2.5rem 0 1.5rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        gap: 15px;
        animation: fadeInDown 0.6s ease-out;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 4px 12px rgba(168, 192, 255, 0.3);
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: 6px;
        letter-spacing: 0.5px;
    }
    
    /* Context Cards - Glassmorphism */
    .context-card {
        background: rgba(22, 27, 34, 0.4);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }
    
    .context-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
        border-color: rgba(168, 192, 255, 0.2);
    }
    
    .card-title {
        color: #a8c0ff;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* File Uploader styling */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(255,255,255,0.02) !important;
        border: 2px dashed rgba(168, 192, 255, 0.3) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #a8c0ff !important;
        background: rgba(168, 192, 255, 0.05) !important;
    }
    
    /* SQL Code Box */
    .sql-code {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 3px solid #3f2b96;
        border-radius: 8px;
        padding: 1.2rem;
        font-family: 'Fira Code', 'Courier New', Courier, monospace;
        font-size: 0.95rem;
        color: #6ee7b7;
        overflow-x: auto;
    }
    
    /* AI Explanation */
    .ai-explanation {
        color: #cbd5e1;
        font-size: 1.05rem;
        line-height: 1.6;
        border-left: 3px solid #a8c0ff;
        padding-left: 1.2rem;
        margin-top: 1.5rem;
        background: linear-gradient(90deg, rgba(168,192,255,0.05) 0%, transparent 100%);
        border-radius: 0 8px 8px 0;
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    
    /* Inputs & Buttons */
    .stTextInput>div>div>input {
        background: rgba(0, 0, 0, 0.2) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #a8c0ff !important;
        box-shadow: 0 0 0 4px rgba(168, 192, 255, 0.15) !important;
        background: rgba(0, 0, 0, 0.4) !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #3f2b96 0%, #a8c0ff 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(63, 43, 150, 0.4);
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(63, 43, 150, 0.6);
        background: linear-gradient(135deg, #4f36bc 0%, #c1d2ff 100%);
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; text-shadow: 0 0 10px rgba(168, 192, 255, 0.5); }
        50% { opacity: 0.6; text-shadow: none; }
    }
    
    .thinking-pulse {
        animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        color: #a8c0ff;
        font-weight: 500;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.1rem;
    }
    
    /* Custom SVG Icons */
    .svg-icon {
        width: 20px;
        height: 20px;
        stroke: currentColor;
        stroke-width: 2.2;
        fill: none;
        stroke-linecap: round;
        stroke-linejoin: round;
    }
    
    .footer {
        text-align: center;
        padding: 40px;
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 300;
    }
    
    /* KPI Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #e2e8f0 !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a8c0ff !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    div[data-testid="metric-container"] {
        background: rgba(22, 27, 34, 0.4);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: rgba(168, 192, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- SVG Icons ---
ICON_FILE = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
ICON_CODE = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M16 18l6-6-6-6M8 6l-6 6 6 6"></path></svg>'
ICON_CHART = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>'
ICON_TABLE = '<svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><path d="M3 9h18M9 21V9"></path></svg>'
ICON_REFRESH = '<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="1 4 1 10 7 10"></polyline><polyline points="23 20 23 14 17 14"></polyline><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path></svg>'
ICON_SEARCH = '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>'

# --- Database Management ---
def load_data_to_sqlite(df):
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    df.to_sql('data_table', conn, index=False, if_exists='replace')
    return conn

# --- Session State ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""

# --- UI Components ---
def header():
    st.markdown(f"""
    <div class="header-container">
        <div>
            <h1 class="header-title" style="background: linear-gradient(90deg, #a8c0ff 0%, #3f2b96 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AskQL</h1>
            <div class="header-subtitle"><i>Just ask. We query</i></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def footer():
    st.markdown("""
    <div class="footer">
        Built with Antigravity AI | UI/UX Pro Max Edition
    </div>
    """, unsafe_allow_html=True)

# --- App Execution ---
header()

# Sidebar
with st.sidebar:
    st.markdown(f"<div style='display:flex; align-items:center; gap:8px; margin-bottom: 2rem;'>{ICON_FILE} <b>Workspace</b></div>", unsafe_allow_html=True)
    
    try:
        default_api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        default_api_key = ""
        
    api_key = st.text_input("Gemini API Key", value=default_api_key, type="password", placeholder="Enter your Gemini API Key")
    st.markdown("<p style='font-size:0.8rem; color:#8b949e;'>Required for AI Query Engine</p>", unsafe_allow_html=True)
    
    if st.button("Reset Session", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("<p style='color:#8b949e; font-size:0.85rem; font-weight:600; text-transform:uppercase;'>Query History</p>", unsafe_allow_html=True)
    for q in st.session_state.history[::-1][:5]:
        st.markdown(f"<div style='color:#c9d1d9; font-size:0.9rem; margin-bottom:8px;'>• {q}</div>", unsafe_allow_html=True)

# Main Content
col_main, _ = st.columns([1, 0.01])

with col_main:
    # 1. Upload Section
    st.markdown('<div class="context-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">{ICON_FILE} Dataset</div>', unsafe_allow_html=True)
    
    st.markdown("<p style='color:#a8c0ff; font-size:0.95rem; margin-bottom: 10px;'>Drag and drop your CSV or Excel file here:</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Data File", type=["csv", "xlsx", "xls"], label_visibility="collapsed")
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            conn = load_data_to_sqlite(df)
            schema_str = extract_schema(df)
            
            # --- Dataset Overview KPIs ---
            kpi_cols = st.columns(3)
            with kpi_cols[0]:
                st.metric("Total Rows", f"{len(df):,}")
            with kpi_cols[1]:
                st.metric("Total Columns", f"{len(df.columns):,}")
            with kpi_cols[2]:
                st.metric("Missing Values", f"{df.isnull().sum().sum():,}")
                
            with st.expander("Preview Dataset"):
                st.dataframe(df.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Error loading file: {e}")
            uploaded_file = None
            
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        # 2. Query Section
        st.markdown('<div class="context-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{ICON_SEARCH} Ask Your Data</div>', unsafe_allow_html=True)
        
        # Example Buttons
        example_cols = st.columns(3)
        examples = ["Show top 5 rows", f"Average of {df.columns[0]}", f"Count entries by {df.columns[-1]}"]
        
        for i, ex in enumerate(examples):
            if example_cols[i].button(ex, key=f"ex_{i}"):
                st.session_state.current_query = ex

        user_input = st.text_input("Enter your question...", value=st.session_state.current_query, placeholder="e.g. Which category has the highest sum?")
        
        if st.button("Generate Insights"):
            if user_input:
                if user_input not in st.session_state.history:
                    st.session_state.history.append(user_input)
                
                if not api_key:
                    st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
                    st.stop()
                    
                # Check if this is the exact same query we just ran
                if user_input == st.session_state.get("last_query") and "last_result" in st.session_state:
                    pass # We already have the results in st.session_state.last_result
                else:
                    think_placeholder = st.empty()
                    think_placeholder.markdown(f'<div class="thinking-pulse">{ICON_SEARCH} AI is analyzing data and generating safe SQL...</div>', unsafe_allow_html=True)
                    
                    llm_client = LLMClient(api_key)
                    chat_history_str = "\\n".join(st.session_state.history[:-1])
                    
                    result_df, llm_response, error_msg = llm_client.execute_with_retry(
                        conn, schema_str, chat_history_str, user_input
                    )
                    
                    think_placeholder.empty()
                    
                    if llm_response and (llm_response.get("confidence") == "LOW" or llm_response.get("clarification_question")):
                        st.warning(f"**Clarification Needed:** {llm_response.get('clarification_question')}")
                        st.stop()
                        
                    if error_msg:
                        st.error(f"Error: {error_msg}")
                        st.stop()
                        
                    # Store in session state for interactive rendering
                    st.session_state.last_query = user_input
                    st.session_state.last_result = {
                        "df": result_df,
                        "sql": llm_response.get("sql"),
                        "explanation": llm_response.get("explanation"),
                        "confidence": llm_response.get("confidence"),
                        "query_type": llm_response.get("query_type"),
                        "suggested_chart": llm_response.get("suggested_chart"),
                        "x_axis": llm_response.get("x_axis"),
                        "y_axis": llm_response.get("y_axis")
                    }

        # --- Render Output from Session State ---
        if "last_result" in st.session_state:
            res = st.session_state.last_result
            result_df = res["df"]
            sql = res["sql"]
            explanation = res["explanation"]
            confidence = res["confidence"]
            q_type = res["query_type"]
            
            # 3. Output Section
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.markdown('<div class="context-card" style="margin-top:1rem;">', unsafe_allow_html=True)
                st.markdown(f'<div class="card-title">{ICON_CODE} Generated SQL &nbsp; <span style="background:rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem;">{confidence} CONFIDENCE</span> <span style="background:rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem;">{q_type}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="sql-code">{sql}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ai-explanation">{explanation}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with res_col2:
                st.markdown('<div class="context-card" style="margin-top:1rem;">', unsafe_allow_html=True)
                st.markdown(f'<div class="card-title">{ICON_TABLE} Results</div>', unsafe_allow_html=True)
                try:
                    # --- Result-Specific KPIs ---
                    res_num_cols = result_df.select_dtypes(include=['number']).columns.tolist()
                    if res_num_cols and len(result_df) > 0:
                        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
                        res_kpi_cols = st.columns(min(3, len(res_num_cols) + 1))
                        with res_kpi_cols[0]:
                            st.metric("Returned Rows", f"{len(result_df):,}")
                        for i, col in enumerate(res_num_cols[:2]):
                            val = result_df[col].sum() if "count" in sql.lower() or "sum" in sql.lower() else result_df[col].mean()
                            val_formatted = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
                            label = f"Total {col}" if "sum" in sql.lower() or "count" in sql.lower() else f"Avg {col}"
                            with res_kpi_cols[i+1]:
                                st.metric(label, val_formatted)
                    
                    st.dataframe(result_df, use_container_width=True)
                except Exception as e:
                    st.error(f"Render Error: {e}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 4. Visualization Section
            if result_df is not None and not result_df.empty and len(result_df) > 0:
                st.markdown('<div class="context-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="card-title">{ICON_CHART} Interactive Visualization</div>', unsafe_allow_html=True)
                
                chart_options = ["bar", "line", "pie", "scatter", "histogram"]
                default_idx = chart_options.index(res["suggested_chart"].lower()) if res.get("suggested_chart") and res.get("suggested_chart").lower() in chart_options else 0
                
                selected_chart = st.selectbox("Select Chart Type", chart_options, index=default_idx)
                st.markdown("<p style='font-size:0.8rem; color:#8b949e;'>You can change the chart type using the dropdown above without re-running the AI.</p>", unsafe_allow_html=True)
                
                fig = generate_visualization(result_df, selected_chart, res.get("x_axis"), res.get("y_axis"))
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No suitable visualization available for this data shape with the selected chart type.")
                    
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

footer()
