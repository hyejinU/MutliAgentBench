"""
BKMS1 Term Project: DB Doctor
DB Connection & SQL Execution Utility

Install before use: pip install psycopg2-binary
"""

import psycopg2
import os

# ================================================================
# DB Connection Config
# Modify these to match your PostgreSQL environment.
# ================================================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "dbdoctor"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}


def get_connection(readonly=False):
    """Returns a PostgreSQL connection."""
    conn = psycopg2.connect(**DB_CONFIG)
    if readonly:
        conn.set_session(readonly=True, autocommit=True)
    return conn


def run_sql(query: str) -> str:
    """
    Executes a read-only SQL query and returns the result as a string.
    This function is used as the agent's tool.

    - Only SELECT, EXPLAIN, SHOW, and WITH statements are allowed.
    - Results are truncated to 50 rows maximum.
    """
    # ============================================================
    # Safety check: only allow read-only statements
    # ============================================================
    allowed_prefixes = ("select", "explain", "show", "with")
    normalized = query.strip().lower()
    if not normalized.startswith(allowed_prefixes):
        return "ERROR: Only SELECT, EXPLAIN, SHOW, and WITH statements are allowed in read-only mode."

    try:
        conn = get_connection(readonly=True)
        cur = conn.cursor()
        cur.execute(query)

        # Column names
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchmany(50)

        cur.close()
        conn.close()

        if not columns:
            return "(no results)"

        # Format results as a readable string
        result_lines = []
        result_lines.append(" | ".join(columns))
        result_lines.append("-" * len(result_lines[0]))
        for row in rows:
            result_lines.append(" | ".join(str(v) for v in row))

        total_info = f"\n(showing max 50 rows; actual result may contain more)" if len(rows) == 50 else ""
        return "\n".join(result_lines) + total_info

    except Exception as e:
        return f"SQL ERROR: {e}"


def run_sql_write(query: str) -> str:
    """
    Executes a writable SQL statement.
    Use this ONLY in anomaly injection scripts. Do NOT expose this to the agent.
    """
    try:
        conn = get_connection(readonly=False)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute(query)

        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            cur.close()
            conn.close()
            result_lines = [" | ".join(columns)]
            for row in rows:
                result_lines.append(" | ".join(str(v) for v in row))
            return "\n".join(result_lines)

        affected = cur.rowcount
        cur.close()
        conn.close()
        return f"OK ({affected} rows affected)"

    except Exception as e:
        return f"SQL ERROR: {e}"


# ================================================================
# Test
# ================================================================
if __name__ == "__main__":
    print("=== DB Connection Test ===")
    result = run_sql("SELECT 'customers' AS tbl, count(*) FROM customers UNION ALL SELECT 'books', count(*) FROM books UNION ALL SELECT 'orders', count(*) FROM orders;")
    print(result)
