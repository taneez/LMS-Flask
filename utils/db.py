# utils/db.py

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
# Ensure your .env file is in the main project directory (e.g., simple-laundry-flask/)
# Adjust path if .env is elsewhere, e.g., load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=os.getenv('DB_PORT', 3306) # Default to 3306 if not specified
        )
        # print("Database connection successful") # Uncomment for debugging connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        # Optionally raise the error or handle it based on application needs
        # raise err
    return connection # Returns None if connection failed

def execute_query(query, params=None, fetch_one=False, is_commit=False):
    """
    Executes a given SQL query with optional parameters.

    Args:
        query (str): The SQL query string (use %s for placeholders).
        params (tuple, optional): A tuple of parameters to substitute into the query. Defaults to None.
        fetch_one (bool, optional): If True, fetches only the first row. Defaults to False.
        is_commit (bool, optional): If True, commits the transaction (for INSERT, UPDATE, DELETE). Defaults to False.

    Returns:
        list: A list of dictionaries for SELECT queries (or a single dict if fetch_one=True).
        int: The last inserted row ID or number of affected rows for commit operations.
        None: If an error occurs or the connection fails.
    """
    conn = None
    cursor = None
    result = None
    error_occurred = False

    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            # Using dictionary=True makes fetching results by column name easy
            cursor = conn.cursor(dictionary=True, buffered=True) # Added buffered=True for potential fetch after commit/read issues

            # Ensure params is a tuple or None
            cursor.execute(query, params or ())

            if is_commit:
                # --- Handle INSERT, UPDATE, DELETE ---
                conn.commit()
                if cursor.lastrowid:
                    result = cursor.lastrowid # Return ID of inserted row
                    # print(f"DB Commit Successful - Last Row ID: {result}") # Debug log
                else:
                    result = cursor.rowcount # Return number of affected rows
                    # print(f"DB Commit Successful - Rows Affected: {result}") # Debug log
            elif fetch_one:
                # --- Handle SELECT single row ---
                result = cursor.fetchone()
                # print(f"DB Fetch One Result: {result}") # Debug log
            else:
                # --- Handle SELECT multiple rows ---
                result = cursor.fetchall()
                # print(f"DB Fetch All Result Count: {len(result) if result else 0}") # Debug log
        else:
            print("Database connection could not be established.")
            error_occurred = True

    except mysql.connector.Error as err:
        print(f"Database Query Error: {err}")
        print(f"Query attempted: {query}") # Log the query that failed
        print(f"Params used: {params}")     # Log the params used
        error_occurred = True
        if conn and is_commit:
            try:
                conn.rollback() # Rollback changes if a commit operation failed
                print("Transaction rolled back due to error.")
            except mysql.connector.Error as rollback_err:
                print(f"Error during rollback: {rollback_err}")
        result = None # Ensure result is None on error

    except Exception as e: # Catch other potential errors
         print(f"An unexpected error occurred during DB operation: {e}")
         error_occurred = True
         result = None

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            # print("Database connection closed.") # Debug log

        # Final check - if an error happened, ensure None is returned
        if error_occurred:
            return None
        return result

# Example Usage (Can be run directly for testing: python utils/db.py)
if __name__ == "__main__":
    print("Testing database connection...")
    test_conn = get_db_connection()
    if test_conn and test_conn.is_connected():
        print("Connection test successful.")
        test_conn.close()
    else:
        print("Connection test failed.")

    print("\nTesting SELECT query (fetching all users)...")
    # Make sure the 'Users' table exists if you run this test
    # users = execute_query("SELECT user_id, username, email FROM Users LIMIT 5")
    # if users is not None:
    #     print(f"Found {len(users)} users:")
    #     for user in users:
    #         print(user)
    # else:
    #     print("Failed to fetch users or table empty/missing.")
    print("(User fetch test commented out - uncomment and ensure 'Users' table exists to test fully)")