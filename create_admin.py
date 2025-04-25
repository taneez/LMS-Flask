import os
import getpass # For securely getting password input
from flask_bcrypt import Bcrypt # Use Bcrypt directly or app's bcrypt instance
from dotenv import load_dotenv

# Import your database utility function
# Make sure this path is correct relative to where you run the script
from utils.db import execute_query, get_db_connection

# Initialize Bcrypt separately for the script if needed
# Or, if running within Flask context isn't feasible:
bcrypt = Bcrypt()

load_dotenv() # Load .env variables

def create_admin_user():
    print("--- Create New Admin User ---")

    # Get admin details from input
    username = input("Enter admin username: ").strip()
    email = input("Enter admin email: ").strip()
    first_name = input("Enter admin first name: ").strip()
    last_name = input("Enter admin last name: ").strip()
    phone = input("Enter admin phone number: ").strip()
    address = input("Enter admin address: ").strip()

    while True:
        password = getpass.getpass("Enter admin password: ") # Hides input
        confirm_password = getpass.getpass("Confirm admin password: ")
        if password == confirm_password:
            if len(password) < 6: # Add basic length check if desired
                print("Password must be at least 6 characters long.")
            else:
                break
        else:
            print("Passwords do not match. Please try again.")

    # Check if username or email already exists
    check_sql = "SELECT user_id FROM Users WHERE username = %s OR email = %s"
    existing_user = execute_query(check_sql, (username, email), fetch_one=True)
    if existing_user:
        print(f"Error: Username '{username}' or Email '{email}' already exists.")
        return # Exit if user exists

    # Hash the password
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        print("Password hashed successfully.")
    except Exception as e:
        print(f"Error hashing password: {e}")
        return

    # Prepare SQL INSERT statement
    insert_sql = """
        INSERT INTO Users
        (username, password_hash, first_name, last_name, email, phone, address, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    # Set the role explicitly to 'admin'
    params = (username, hashed_password, first_name, last_name, email, phone, address, 'admin')

    # Execute the query
    print("Attempting to insert admin user...")
    try:
        user_id = execute_query(insert_sql, params, is_commit=True)
        if user_id:
            print(f"Admin user '{username}' created successfully with user_id: {user_id}!")
        else:
            # Check utils/db.py for specific logged errors if this happens
            print("Admin user creation failed. Check database connection or logs.")
    except Exception as e: # Catch potential errors from execute_query itself
         print(f"An error occurred during database insertion: {e}")


if __name__ == "__main__":
    # Ensure database connection works before proceeding
    print("Checking DB connection...")
    conn_test = get_db_connection()
    if conn_test and conn_test.is_connected():
        print("Connection successful.")
        conn_test.close()
        create_admin_user()
    else:
        print("Failed to connect to the database. Please check your .env settings and DB status.")