import pandas as pd

def extract_schema(df: pd.DataFrame, table_name: str = "data_table", sample_rows: int = 3) -> str:
    """
    Extracts the schema of a pandas DataFrame and returns a string representation
    suitable for injecting into an LLM prompt. Includes column names, data types,
    and a few sample rows to help the LLM understand semantics.
    """
    schema_lines = [f"Table Name: {table_name}"]
    schema_lines.append(f"Total Rows: {len(df)}")
    schema_lines.append("Columns:")
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        # Identify if it's likely a primary key or categorical
        unique_count = df[col].nunique()
        notes = []
        if unique_count == len(df):
            notes.append("Unique ID")
        elif unique_count < 10:
            notes.append(f"Categorical ({unique_count} distinct values)")
            
        note_str = f" - {', '.join(notes)}" if notes else ""
        schema_lines.append(f"  - {col} ({dtype}){note_str}")
        
    schema_lines.append(f"\nSample Data ({sample_rows} rows):")
    
    # Convert sample data to a structured string representation
    # Replacing newlines to keep it compact
    sample_df = df.head(sample_rows)
    schema_lines.append(sample_df.to_markdown(index=False))
    
    return "\n".join(schema_lines)
