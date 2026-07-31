import json
import sqlite3
import pandas as pd
import google.generativeai as genai
from askql_engine.prompt_engine import SYSTEM_PROMPT, build_prompt
from askql_engine.sql_validator import is_safe_sql

class LLMClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-preview-05-20',
            system_instruction=SYSTEM_PROMPT,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        )

    def generate_query(self, schema_str: str, chat_history_str: str, user_query: str) -> dict:
        """
        Sends the prompt to Gemini and parses the JSON response.
        """
        prompt = build_prompt(schema_str, chat_history_str, user_query)
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            return {"error": f"LLM Generation Error: {str(e)}"}

    def execute_with_retry(self, sqlite_conn, schema_str: str, chat_history_str: str, user_query: str, max_retries: int = 2) -> tuple:
        """
        Generates SQL, validates it, and executes it.
        If SQLite execution fails, it feeds the error back to the LLM to self-correct.
        Returns: (result_df, llm_json_response, error_message)
        """
        error_message = None
        current_retry = 0
        
        while current_retry <= max_retries:
            prompt = build_prompt(schema_str, chat_history_str, user_query, error_message)
            try:
                response = self.model.generate_content(prompt)
                llm_response = json.loads(response.text)
            except Exception as e:
                return None, None, f"Failed to get or parse LLM response: {str(e)}"
                
            # If confidence is LOW or there's a clarification question
            if llm_response.get("confidence") == "LOW" or llm_response.get("clarification_question"):
                # We return immediately, no SQL to execute
                return None, llm_response, None
                
            sql = llm_response.get("sql")
            
            # If LLM didn't return SQL for some reason
            if not sql:
                return None, llm_response, "LLM did not generate SQL despite high/medium confidence."
                
            # 1. Safety Validation
            is_safe, safety_err = is_safe_sql(sql)
            if not is_safe:
                return None, llm_response, f"SQL Safety Violation: {safety_err}"
                
            # 2. Execute SQL
            try:
                df = pd.read_sql(sql, sqlite_conn)
                # Success!
                return df, llm_response, None
            except Exception as e:
                # SQLite execution failed (e.g. hallucinated column)
                error_message = str(e)
                current_retry += 1
                
        # If we exhausted retries
        return None, llm_response, f"Failed after {max_retries} retries. Last error: {error_message}"
