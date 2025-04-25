# app.py
import os
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime

# Import database utility
from utils.db import execute_query # Make sure utils/db.py and execute_query exist

load_dotenv()

app = Flask(__name__)
# Make sure FLASK_SECRET_KEY is set in your .env file!
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'change-this-in-production-very-secret')
bcrypt = Bcrypt(app)

# --- Helper Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if logged in
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        # Then check role
        if session.get('role') != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index')) # Redirect non-admins away
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        role = 'customer' # Default role for self-registration

        # --- Validation ---
        if not all([username, password, confirm_password, first_name, last_name, email, phone, address]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        # --- Check Existing User ---
        check_sql = "SELECT user_id FROM Users WHERE username = %s OR email = %s"
        existing_user = execute_query(check_sql, (username, email), fetch_one=True)
        if existing_user:
            flash('Username or Email already exists.', 'danger')
            return redirect(url_for('register'))

        # --- Hash Password ---
        try:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        except Exception as e:
            flash('Error processing registration. Please try again.', 'danger')
            print(f"Password Hashing Error: {e}")
            return redirect(url_for('register'))


        # --- Insert User ---
        insert_sql = """
            INSERT INTO Users (username, password_hash, first_name, last_name, email, phone, address, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (username, hashed_password, first_name, last_name, email, phone, address, role)
        user_id = execute_query(insert_sql, params, is_commit=True)

        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            # execute_query should log the specific DB error
            flash('Registration failed due to a database error. Please try again later.', 'danger')
            return redirect(url_for('register'))

    # --- Handle GET Request ---
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and Password are required.', 'warning')
            return redirect(url_for('login'))

        # Fetch user by email - include necessary fields for session and password check
        sql = """SELECT user_id, username, password_hash, first_name, last_name, email, phone, address, role
                 FROM Users WHERE email = %s"""
        user = execute_query(sql, (email,), fetch_one=True)

        # Check if user exists and password hash matches
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            # Store user info in session
            session.clear() # Clear old session data first
            session['logged_in'] = True
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name'] # Store last name if needed
            session['role'] = user['role']
            # Add other relevant info if needed, but avoid sensitive data

            flash('Login successful!', 'success')

            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                 return redirect(url_for('index')) # Redirect customer/staff to home or orders
        else:
            flash('Invalid email or password.', 'danger')
            # Don't redirect immediately, let the template render again with the flash message
            return render_template('login.html') # Re-render login form on failure

    # --- Handle GET Request ---
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Clears the session to log the user out."""
    session.clear()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/place_order', methods=['GET', 'POST'])
@login_required # Ensure user is logged in
def place_order():
    """Handles placing a new laundry order."""
    # Fetch laundry items for the form dropdown/list
    items_sql = "SELECT laundry_item_id, name, base_price FROM LaundryItems ORDER BY name"
    laundry_items = execute_query(items_sql)
    if laundry_items is None: # Check if query failed
        flash('Could not load laundry items. Please try again later.', 'danger')
        laundry_items = [] # Provide empty list to template

    if request.method == 'POST':
        user_id = session['user_id']
        special_instructions = request.form.get('special_instructions', '')
        order_items_data = []
        total_order_amount = 0.0

        # --- Process items selected in the form ---
        for item in laundry_items: # Iterate through items we fetched earlier
            item_id = item['laundry_item_id']
            quantity_str = request.form.get(f'quantity_{item_id}')
            if quantity_str: # Check if quantity was provided for this item
                try:
                    quantity = int(quantity_str)
                    if quantity > 0:
                        # Use the price fetched earlier for consistency
                        price = float(item['base_price'])
                        item_total = price * quantity
                        order_items_data.append({
                            'laundry_item_id': item_id,
                            'quantity': quantity,
                            'price_per_unit': price,
                            'total_price': item_total
                        })
                        total_order_amount += item_total
                except (ValueError, TypeError):
                    flash(f"Invalid quantity entered for {item['name']}. It was ignored.", 'warning')
                    # Continue processing other items

        # --- Validate if any items were added ---
        if not order_items_data:
            flash('Please select at least one item with a valid quantity > 0.', 'warning')
            # Re-render the form with the items list
            return render_template('place_order.html', laundry_items=laundry_items)

        # --- Create Order and OrderItems in Database ---
        # 1. Create Order record
        order_sql = """
            INSERT INTO Orders (user_id, total_amount, order_status, special_instructions)
            VALUES (%s, %s, %s, %s)
        """
        order_params = (user_id, total_order_amount, 'Pending', special_instructions)
        new_order_id = execute_query(order_sql, order_params, is_commit=True)

        if not new_order_id:
             flash('Failed to create order record. Please try again.', 'danger')
             return render_template('place_order.html', laundry_items=laundry_items)

        # 2. Create OrderItems records
        item_insert_sql = """
            INSERT INTO OrderItems (order_id, laundry_item_id, quantity, price_per_unit, total_price)
            VALUES (%s, %s, %s, %s, %s)
        """
        all_items_inserted = True
        for item_data in order_items_data:
            item_params = (
                new_order_id,
                item_data['laundry_item_id'],
                item_data['quantity'],
                item_data['price_per_unit'],
                item_data['total_price']
            )
            item_result = execute_query(item_insert_sql, item_params, is_commit=True)
            if not item_result:
                 all_items_inserted = False
                 # Log error: Failed to insert item_data['laundry_item_id'] for order new_order_id
                 # More advanced: Could attempt to delete the parent Order record here (rollback logic)

        if all_items_inserted:
            flash(f'Order #{new_order_id} placed successfully!', 'success')
            return redirect(url_for('my_orders')) # Redirect to order history
        else:
             flash('Order placed, but failed to add some items. Please contact support regarding order #{new_order_id}.', 'warning')
             return redirect(url_for('my_orders')) # Redirect anyway

    # --- Handle GET Request ---
    # Pass laundry items to the template
    return render_template('place_order.html', laundry_items=laundry_items)


@app.route('/my_orders')
@login_required # Ensure user is logged in
def my_orders():
    """Displays the logged-in user's order history."""
    user_id = session['user_id']
    # Fetch orders for the current user
    sql = """
        SELECT o.order_id, o.order_date, o.total_amount, o.order_status, o.due_date
        FROM Orders o
        WHERE o.user_id = %s
        ORDER BY o.order_date DESC
    """
    orders = execute_query(sql, (user_id,))
    if orders is None:
        flash('Could not retrieve order history.', 'danger')
        orders = []

    return render_template('my_orders.html', orders=orders)


@app.route('/admin')
@admin_required # Ensure only admins access this
def admin_dashboard():
    """Displays all orders for the admin."""
    # Fetch all orders with user details
    sql = """
        SELECT o.order_id, o.order_date, o.total_amount, o.order_status, o.due_date,
               u.user_id, u.first_name, u.last_name, u.email
        FROM Orders o
        JOIN Users u ON o.user_id = u.user_id
        ORDER BY o.order_date DESC
    """
    all_orders = execute_query(sql)
    if all_orders is None:
        flash('Error fetching orders from the database.', 'danger')
        all_orders = [] # Pass empty list to template on error

    return render_template('admin_dashboard.html', orders=all_orders)


@app.route('/admin/update_status/<int:order_id>', methods=['POST'])
@admin_required # Ensure only admins access this
def update_order_status(order_id):
    """Handles updating the status and due date of an order by an admin."""
    new_status = request.form.get('order_status')
    due_date_str = request.form.get('due_date')

    valid_statuses = ['Pending', 'Received', 'Processing', 'Ready', 'Completed', 'Cancelled']

    # Validate Status
    if not new_status or new_status not in valid_statuses:
         flash('Invalid status selected.', 'warning')
         return redirect(url_for('admin_dashboard'))

    # Prepare parameters and fields for update
    update_params_list = []
    update_fields = []

    update_fields.append("order_status = %s")
    update_params_list.append(new_status)

    # Process due_date only if a non-empty string is provided
    due_date_obj = None
    if due_date_str:
        try:
            due_date_obj = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            update_fields.append("due_date = %s")
            update_params_list.append(due_date_obj)
        except ValueError:
            flash(f'Invalid date format "{due_date_str}". Use YYYY-MM-DD.', 'warning')
            # Continue without updating date if format is wrong

    # Add order_id to params for WHERE clause (must be last)
    update_params_list.append(order_id)

    # Construct and execute the SQL query
    sql = f"UPDATE Orders SET {', '.join(update_fields)} WHERE order_id = %s"
    result = execute_query(sql, tuple(update_params_list), is_commit=True)

    if result is not None: # Check for DB execution success
        if result > 0: # Check if rows were actually affected
            flash(f'Order #{order_id} details updated successfully.', 'success')
        else:
            check_order_sql = "SELECT order_id FROM Orders WHERE order_id = %s"
            order_exists = execute_query(check_order_sql, (order_id,), fetch_one=True)
            if order_exists:
                flash(f'Order #{order_id} found, but no changes made (status/date may be the same).', 'info')
            else:
                flash(f'Order #{order_id} not found.', 'warning')
    else:
        flash(f'Failed to update Order #{order_id}. Database error.', 'danger')

    return redirect(url_for('admin_dashboard'))

# --- Main Execution ---
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    # Use 0.0.0.0 to make accessible on local network (optional)
    # host = '0.0.0.0' if debug_mode else '127.0.0.1'
    app.run(debug=debug_mode, port=5000) # host=host