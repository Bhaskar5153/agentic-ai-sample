from google.adk.agents.llm_agent import Agent
import sqlite3
import pandas as pd
import numpy as np

# def add_two(a, b):
#     c = a+b
#     return c

# def multiply(a, b):
#     c = a*b
#     return c


# def tokenize(text):
#     tokens = text.split()
#     return tokens

def query_sales_db(query: str, db_path: str = r'C:\Users\Priya Bhaskar\AppData\Roaming\DBeaverData\workspace6\.metadata\sample-database-sqlite-1\Chinook.db'):
    """
    Execute a SQL query on the specified SQLite database and return results as a list of dictionaries.
    
    Args:
        query (str): The SQL query to execute (e.g., 'SELECT * FROM supermarket_sales').
        db_path (str): Path to the SQLite database file. Defaults to the supermarket sales database.
    
    Returns:
        list[dict]: Query results as a list of dictionaries, or an error message string if connection fails.
    """
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient='records')
    except sqlite3.OperationalError as e:
        return f"Database connection error: {e}. Please check the file path and permissions."


def analyze_sales(query: str, db_path: str = r'C:\Users\Priya Bhaskar\AppData\Roaming\DBeaverData\workspace6\.metadata\sample-database-sqlite-1\Chinook.db'):
    """
    Execute a SQL query and provide deep analysis of the results, including summary statistics, branch comparisons, and sales trends.
    
    Args:
        query (str): The SQL query to execute (e.g., 'SELECT * FROM supermarket_sales').
        db_path (str): Path to the SQLite database file. Defaults to the supermarket sales database.
    
    Returns:
        dict: Analysis results including summary statistics, branch sales, sales over time, or error message.
    """
    df = query_sales_db(query, db_path)
    if isinstance(df, str):
        return {"error": df}
    analysis = {}
    if df:
        df = pd.DataFrame(df)  # Convert list of dictionaries back to DataFrame for analysis
        summary = df.describe(include='all').replace({np.nan: None}).to_dict()
        analysis['summary'] = summary
        if 'Branch' in df.columns:
            branch_sales = df.groupby('Branch').sum(numeric_only=True).replace({np.nan: None}).to_dict()
            analysis['branch_sales'] = branch_sales
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            if not df['Date'].isnull().all():
                sales_over_time = df.groupby(df['Date'].dt.to_period('M')).sum(numeric_only=True).replace({np.nan: None}).to_dict()
                analysis['sales_over_time'] = sales_over_time
    else:
        analysis['message'] = 'No data returned for the query.'
    return analysis


def get_db_schema(db_path: str = r'C:\Users\Priya Bhaskar\AppData\Roaming\DBeaverData\workspace6\.metadata\sample-database-sqlite-1\Chinook.db'):
    """
    Discover and return all table names and their columns from the specified SQLite database.
    
    Args:
        db_path (str): Path to the SQLite database file. Defaults to the supermarket sales database.
    
    Returns:
        dict: Mapping of table names to lists of column names, or error message if connection fails.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        schema = {}
        for (table_name,) in tables:
            columns = cursor.execute(f'PRAGMA table_info({table_name});').fetchall()
            schema[table_name] = [col[1] for col in columns]
        conn.close()
        return schema
    except sqlite3.OperationalError as e:
        return {"error": f"Database connection error: {e}. Please check the file path and permissions."}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions. The database table and columns are case-sensitive. Use the schema discovery tool to check table and column names before querying.',
    instruction='Answer user questions to the best of your knowledge. Use the get_db_schema tool to check table and column names before querying.',
    tools=[query_sales_db, analyze_sales, get_db_schema]
)
