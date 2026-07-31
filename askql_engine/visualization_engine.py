import plotly.express as px
import pandas as pd
import streamlit as st

@st.cache_data
def generate_visualization(df: pd.DataFrame, chart_type: str, x_axis: str = None, y_axis: str = None):
    """
    Generates a Plotly figure with robust column detection, fallback logic,
    chart validation, and user interactivity support.
    """
    if df is None or df.empty:
        return None

    # --- 1. Handle single-column or scalar results ---
    if len(df.columns) == 1:
        col_name = df.columns[0]
        # If it's a single row, it's just a number/string, not really plottable as-is,
        # but we can fake a categorical dataframe for a bar chart
        if len(df) == 1:
            val = df.iloc[0, 0]
            df = pd.DataFrame({"Metric": [col_name], "Value": [val]})
        else:
            # Single column, multiple rows -> Histogram
            if pd.api.types.is_numeric_dtype(df[col_name]):
                chart_type = "histogram"
                x_axis = col_name
                y_axis = None

    # Normalize columns for matching
    df.columns = [str(c).strip() for c in df.columns]
    cols_lower = {c.lower(): c for c in df.columns}
    
    # Resolve X and Y from LLM (case-insensitive)
    real_x = cols_lower.get(str(x_axis).lower().strip()) if x_axis else None
    real_y = cols_lower.get(str(y_axis).lower().strip()) if y_axis else None

    # --- 2. Dynamic Type Detection ---
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()

    # --- 3. Fallback Axis Selection ---
    if not real_x and categorical_cols:
        real_x = categorical_cols[0]
    elif not real_x and numeric_cols:
        real_x = numeric_cols[0]
        
    if not real_y and numeric_cols:
        # Try to pick a different numeric column if x is already numeric
        avail_y = [c for c in numeric_cols if c != real_x]
        real_y = avail_y[0] if avail_y else numeric_cols[0]

    # --- 4. Chart Compatibility Validation ---
    if chart_type in [None, "none", "None", ""]:
        chart_type = "bar" if real_y else "none"

    chart_type = chart_type.lower()
    
    is_x_cat = real_x in categorical_cols
    is_x_num = real_x in numeric_cols
    is_y_num = real_y in numeric_cols

    # Auto-correct chart types
    if chart_type == "scatter" and not (is_x_num and is_y_num):
        chart_type = "bar"
    if chart_type in ["pie", "bar"] and not (real_x and real_y):
        if is_x_num and not real_y:
            chart_type = "histogram"
        else:
            chart_type = "none"

    if chart_type == "none" or not real_x:
        return None

    # --- 5. Data Preparation & Sorting ---
    plot_df = df.copy()
    
    # Sort and Limit large datasets
    if chart_type in ["bar", "pie", "line"] and real_y:
        plot_df = plot_df.sort_values(by=real_y, ascending=False)
        
        if is_x_cat and len(plot_df[real_x].unique()) > 20:
            plot_df = plot_df.head(10)
            # We don't display the message via print, we rely on Streamlit UI for that
            # but we truncate the data

    # --- 6. Render Chart ---
    try:
        fig = None
        template = "plotly_dark"
        
        title = f"{real_y} by {real_x}" if real_y else f"Distribution of {real_x}"
        
        if chart_type == "bar":
            fig = px.bar(plot_df, x=real_x, y=real_y, title=title, template=template, color_discrete_sequence=['#58a6ff'])
        elif chart_type == "line":
            fig = px.line(plot_df, x=real_x, y=real_y, title=title, markers=True, template=template, color_discrete_sequence=['#7ee787'])
        elif chart_type == "pie":
            fig = px.pie(plot_df, values=real_y, names=real_x, title=title, template=template, color_discrete_sequence=['#58a6ff', '#7ee787', '#d2a8ff'])
        elif chart_type == "scatter":
            fig = px.scatter(plot_df, x=real_x, y=real_y, title=title, template=template, color_discrete_sequence=['#d2a8ff'])
        elif chart_type == "histogram":
            fig = px.histogram(plot_df, x=real_x, title=title, template=template, color_discrete_sequence=['#ff7b72'])

        if fig:
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=50, b=20)
            )
            return fig
            
    except Exception as e:
        print(f"Visualization error: {e}")
        return None
        
    return None
