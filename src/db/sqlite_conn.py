import sqlite3
from sqlite3 import Error

# Function to create a database connection
def create_connection(database):
    conn = sqlite3.connect(database)
    return conn


# Function to query the database
def query_database(conn, query, search_text):
    cur = conn.cursor()
    cur.execute(query, (search_text,))
    rows = cur.fetchall()
    return rows


def create_table_if_not_exists(conn):
    ddl = """
        CREATE TABLE prs (
        	pr_id INTEGER PRIMARY KEY,
            created_at INTEGER,
            updated_at INTEGER,
	        pr_title TEXT NOT NULL,
	        pr_body TEXT NOT NULL,
	        commits_id TEXT NOT NULL,
            explanation TEXT NOT NULL
        );
    """
    cur = conn.cursor()
    cur.execute(ddl)


if __name__ == "__main__":
    conn = create_connection("pr_database")
    create_table_if_not_exists(conn)
