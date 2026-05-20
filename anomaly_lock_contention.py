"""
BKMS1 Term Project: DB Doctor
Scenario B: Lock Contention

Goal:
  Multiple sessions UPDATE the same rows simultaneously, causing lock waits.
  The agent should detect this via pg_locks and pg_stat_activity.

TODO:
  1. Write UPDATE statements in lock_worker() that target the same rows.
  2. Important: the transaction must be held open long enough for lock waits to be observable.
  3. Manual diagnosis: verify using pg_locks and pg_stat_activity.
"""

import threading
import time
from db_connect import get_connection

# ================================================================
# Configuration
# ================================================================
NUM_THREADS = 5               # Number of concurrent sessions
TARGET_ORDER_IDS = [1, 2, 3]  # Order IDs to contend on
HOLD_SECONDS = 30             # How long to hold the lock (run the agent during this window)


def lock_worker(thread_id: int):
    """
    UPDATEs a specific row and holds the lock.

    TODO: Implement the following steps:
      1. Disable autocommit (conn.autocommit = False)
      2. After BEGIN, UPDATE the target row.
      3. Use time.sleep() to hold the lock.
         -> Other sessions trying to UPDATE the same row will wait.
      4. COMMIT or ROLLBACK.

    Hints:
      - Updating the 'status' column in the orders table is a natural scenario.
      - Multiple threads must UPDATE the same order_id to cause contention.
      - Use UPDATE ... WHERE order_id = X.
    """
    conn = get_connection()
    conn.autocommit = False
    cur = conn.cursor()

    # Pick the target row for this thread
    target_id = TARGET_ORDER_IDS[thread_id % len(TARGET_ORDER_IDS)]

    try:
        # ======================================================
        # TODO: Write your UPDATE statement here.
        # Example:
        #   cur.execute(
        #       "UPDATE orders SET status = %s, updated_at = now() WHERE order_id = %s",
        #       (f'processing_by_thread_{thread_id}', target_id)
        #   )
        # ======================================================

        pass  # <- Remove this line and write cur.execute(...) instead.

        print(f"  [Thread {thread_id}] Lock acquired on order_id={target_id}, holding for {HOLD_SECONDS}s...")

        # Hold the lock — run the agent in another terminal during this window!
        time.sleep(HOLD_SECONDS)

        conn.commit()
        print(f"  [Thread {thread_id}] COMMIT done")

    except Exception as e:
        print(f"  [Thread {thread_id}] Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def inject_anomaly():
    """Starts multiple sessions that UPDATE the same rows to create lock contention."""
    print(f"[Lock Contention] Starting {NUM_THREADS} concurrent UPDATE sessions...")
    print(f"[Lock Contention] Target order_ids: {TARGET_ORDER_IDS}")
    print(f"[Lock Contention] Lock hold time: {HOLD_SECONDS}s")
    print(f"[Lock Contention] -> Run the agent in another terminal during this window!\n")

    threads = []
    for t_id in range(NUM_THREADS):
        t = threading.Thread(target=lock_worker, args=(t_id,))
        threads.append(t)
        t.start()
        time.sleep(0.5)  # Stagger starts slightly so lock contention actually occurs

    for t in threads:
        t.join()

    print(f"\n[Lock Contention] All sessions finished.")


if __name__ == "__main__":
    inject_anomaly()
