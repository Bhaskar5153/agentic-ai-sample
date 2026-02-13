import sqlite3

DB_PATH = r"C:\Users\Priya Bhaskar\AppData\Roaming\DBeaverData\workspace6\.metadata\sample-database-sqlite-1\Chinook.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def query_sales(limit=10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM supermarket_sales LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

query_sales()