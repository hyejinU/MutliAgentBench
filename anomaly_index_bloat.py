"""
BKMS1 Term Project: DB Doctor
Scenario C: Index Bloat (Write Performance Degradation from Unnecessary Indexes)

Goal:
  Create many unnecessary indexes on a single table, then run heavy UPDATEs.
  The index maintenance overhead should cause noticeable write performance degradation.

TODO:
  1. Add CREATE INDEX statements in create_unnecessary_indexes().
  2. Write UPDATE queries in run_heavy_updates().
  3. Manual diagnosis: use pg_stat_user_indexes to identify unused indexes.
"""

import time
from db_connect import run_sql_write, run_sql

# ================================================================
# Step 1: Create Unnecessary Indexes
# ================================================================
def create_unnecessary_indexes():
    """
    Creates 10+ unnecessary indexes on the books table.

    TODO: Add indexes on various columns and column combinations.

    Hints:
      - Single-column index: CREATE INDEX idx_xxx ON books(column);
      - Composite index: CREATE INDEX idx_xxx ON books(col1, col2);
      - The point is to create combinations that will rarely (or never) be used.
      - Examples: (language, page_count), (isbn, rating), (publisher, published_date), etc.
    """
    indexes_to_create = [
        # ======================================================
        # TODO: Add at least 10 CREATE INDEX statements here.
        # Examples:
        #   "CREATE INDEX idx_books_price ON books(price)",
        #   "CREATE INDEX idx_books_rating ON books(rating)",
        #   "CREATE INDEX idx_books_lang_pages ON books(language, page_count)",
        # ======================================================
    ]

    print(f"[Index Bloat] Creating {len(indexes_to_create)} indexes...")
    for sql in indexes_to_create:
        result = run_sql_write(sql)
        print(f"  {sql[:60]}... -> {result}")
    print("[Index Bloat] Index creation complete.\n")


# ================================================================
# Step 2: Run Heavy UPDATEs (observe the difference with/without indexes)
# ================================================================
def run_heavy_updates():
    """
    Runs mass UPDATEs on multiple columns of the books table.
    With many indexes, each UPDATE must also update every index, making it slower.

    TODO: Write UPDATE queries.

    Hints:
      - Update columns like price, stock_quantity, rating simultaneously.
      - Updating all rows (no WHERE clause) makes the effect most visible.
      - Alternatively, update by category in multiple batches.
    """
    print("[Index Bloat] Running heavy UPDATEs (timing each one)...")

    # ======================================================
    # TODO: Write your UPDATE statements here.
    # Examples:
    #   queries = [
    #       "UPDATE books SET price = price * 1.1 WHERE category = 'Fiction'",
    #       "UPDATE books SET stock_quantity = stock_quantity - 1",
    #       "UPDATE books SET rating = round(random()::numeric * 4 + 1, 2)",
    #   ]
    # ======================================================
    queries = []

    for i, sql in enumerate(queries):
        start = time.time()
        result = run_sql_write(sql)
        elapsed = time.time() - start
        print(f"  [{i+1}] {elapsed:.3f}s - {sql[:60]}... -> {result}")

    print("[Index Bloat] UPDATEs complete.\n")


# ================================================================
# Step 3: Drop Unnecessary Indexes (for comparison)
# ================================================================
def drop_unnecessary_indexes():
    """Drops all unnecessary indexes that were created on the books table."""
    # Only drop indexes on the books table, excluding the primary key
    result = run_sql("""
        SELECT indexname FROM pg_indexes
        WHERE tablename = 'books'
          AND indexname != 'books_pkey'
        ORDER BY indexname;
    """)
    print("[Index Bloat] Dropping unnecessary indexes...")
    print(result)
    # TODO: DROP the indexes listed above that you created.


# ================================================================
# Entry Point
# ================================================================
def inject_anomaly():
    """Runs the Index Bloat scenario."""
    print("=" * 60)
    print("[Index Bloat] Starting scenario")
    print("=" * 60)

    # 1. Create unnecessary indexes
    create_unnecessary_indexes()

    # 2. Show current index list
    print("[Index Bloat] Current indexes on the books table:")
    print(run_sql("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'books'
        ORDER BY indexname;
    """))
    print()

    # 3. Run heavy UPDATEs (with indexes present)
    print(">>> UPDATEs WITH indexes <<<")
    run_heavy_updates()

    # 4. (Optional) Drop indexes and repeat UPDATEs for comparison
    # drop_unnecessary_indexes()
    # print(">>> UPDATEs WITHOUT indexes <<<")
    # run_heavy_updates()

    print("[Index Bloat] Now run the agent to diagnose the issue.")


if __name__ == "__main__":
    inject_anomaly()
