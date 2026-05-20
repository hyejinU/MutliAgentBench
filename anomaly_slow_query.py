"""
BKMS1 Term Project: DB Doctor
Scenario A: Slow Query (Full Table Scan)

Goal:
  Run heavy SELECT queries without indexes across multiple concurrent sessions
  to cause performance degradation via sequential scans.

TODO:
  1. Write slow queries inside inject_anomaly().
  2. Run them concurrently across multiple threads to generate load.
  3. Manual diagnosis: verify using EXPLAIN ANALYZE and pg_stat_statements.
"""

import threading
import time
from db_connect import get_connection

# ================================================================
# Configuration
# ================================================================
NUM_THREADS = 5          # Number of concurrent sessions
QUERIES_PER_THREAD = 10  # Number of queries each session will execute


def slow_query_worker(thread_id: int):
    """
    Repeatedly executes slow queries in a single session.

    TODO: Use conn.cursor() to write SELECT queries that trigger
          sequential scans.

    Hints:
      - The books table has no index on the 'description' column.
      - WHERE description LIKE '%keyword%' cannot use an index.
      - Filtering on category, author, etc. without an index causes full scans.
      - JOINing multiple tables makes it heavier.
    """
    conn = get_connection()
    cur = conn.cursor()

    for i in range(QUERIES_PER_THREAD):
        # ======================================================
        # TODO: Write your slow query here.
        # Example (try to create something heavier than this):
        #   cur.execute("SELECT * FROM books WHERE description LIKE '%explores%'")
        # ======================================================

        pass  # <- Remove this line and write cur.execute(...) instead.

        cur.fetchall()  # Must fetch all results to complete execution
        print(f"  [Thread {thread_id}] Query {i+1}/{QUERIES_PER_THREAD} done")

    cur.close()
    conn.close()


def inject_anomaly():
    """Runs slow queries concurrently across multiple threads."""
    print(f"[Slow Query] Starting {NUM_THREADS} concurrent sessions...")
    print(f"[Slow Query] Each session will run {QUERIES_PER_THREAD} queries\n")

    threads = []
    start_time = time.time()

    for t_id in range(NUM_THREADS):
        t = threading.Thread(target=slow_query_worker, args=(t_id,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.time() - start_time
    print(f"\n[Slow Query] Done. Total elapsed time: {elapsed:.2f}s")
    print("[Slow Query] Now run the agent to diagnose the issue.")


if __name__ == "__main__":
    inject_anomaly()
