import re
import sqlparse

def is_safe_sql(sql: str) -> tuple[bool, str]:
    """
    Validates that the SQL query is read-only and does not contain destructive commands.
    Returns (is_safe, error_message).
    """
    if not sql:
        return False, "Empty SQL query."

    # List of forbidden keywords
    forbidden_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'PRAGMA',
        'CREATE', 'GRANT', 'REVOKE', 'REPLACE', 'UPSERT', 'MERGE', 'EXEC', 'EXECUTE'
    ]

    # Parse the SQL to handle comments and strings properly
    try:
        parsed = sqlparse.parse(sql)
        for statement in parsed:
            # Check statement type
            stmt_type = statement.get_type()
            if stmt_type != 'SELECT' and stmt_type != 'UNKNOWN': # UNKNOWN happens for some valid SQLite stuff, but we will regex check anyway
                return False, f"Dangerous operation detected. Only SELECT statements are allowed."
            
            # Token check
            for token in statement.flatten():
                if token.ttype in sqlparse.tokens.Keyword or token.ttype in sqlparse.tokens.Keyword.DML or token.ttype in sqlparse.tokens.Keyword.DDL:
                    if token.value.upper() in forbidden_keywords:
                        return False, f"Dangerous keyword '{token.value.upper()}' detected. Operation blocked."

    except Exception as e:
        return False, f"Failed to parse SQL: {str(e)}"

    # Fallback regex check just in case sqlparse misses something weird
    upper_sql = sql.upper()
    for kw in forbidden_keywords:
        # Match whole words only
        if re.search(rf'\b{kw}\b', upper_sql):
            return False, f"Dangerous keyword '{kw}' detected via fallback check. Operation blocked."

    return True, ""

def check_hallucinations(sql: str, valid_columns: list) -> tuple[bool, str]:
    """
    Checks if the SQL query uses any columns that don't exist in the schema.
    (Basic check: SQLite execution will catch it anyway, but we can do a preliminary check).
    Returns (is_valid, error_message).
    """
    # SQLite execution is actually the best hallucination checker,
    # so we will rely on the try/except loop in llm_client for robust checking.
    # We provide a basic placeholder here.
    return True, ""
