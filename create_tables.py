import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

def execute_sql_file(filename: str) -> None:
    """Executes SQL commands from the specified file to create tables in the SQLite database."""
    db_name = os.getenv('DATABASE_NAME', 'default.db')

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    with open(filename, 'r') as file:
        sql_script = file.read()

    cursor.executescript(sql_script)

    conn.commit()
    conn.close()
    print(f"Executed SQL script from {filename} successfully.")

if __name__ == "__main__":
    tables_sql_path = "scripts\\tables.sql"
    execute_sql_file(tables_sql_path)
