# 🧺 Laundry Management System (LMS) – Flask

A full-featured Laundry Management System built using **HTML**, **Flask (Python)**, and **MySQL**.

This system is designed to streamline and automate laundry services — from order placement to tracking and admin management.

---

## 📖 Overview

The Laundry Management System (LMS) solves common problems faced by laundry facilities:

- Manual and inefficient laundry operations.
- Lack of real-time status updates for users.
- Difficulty in tracking order progress.

---

## 🎯 Features

- ✅ **Place Orders**: Users can submit laundry requests with quantities and item types.
- 🔐 **User Authentication**: Sign-up/login with secure password hashing.
- 🔍 **Order Tracking**: Track laundry orders via unique reference ID.
- 🛠️ **Admin Dashboard**: Manage and update all orders from a single interface.
- 📬 **Contact Form**: Users can submit queries or support requests.

---

## 💻 Technologies Used

- **Frontend**: HTML, CSS, Bootstrap
- **Backend**: Flask (Python)
- **Database**: MySQL (for LMS-Flask version)
- **Authentication**: Password hashing with Flask-Bcrypt
- **Styling**: Bootstrap for responsive design

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone <link to repository>
```
### 2. Install Dependencies

It's recommended to use a virtual environment.

```bash
pip install Flask Flask-Cors Flask-Bcrypt mysql-connector-python python-dotenv
```
### 3. Configure Environment Variables

Create a `.env` file in the root directory and add the following content:

```ini
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=laundry_db
```

### 4. Create the MySql Database

Run the queries from `database_setup.sql` in your MySQL terminal.

### 5. Create an Admin User

Run `create_admin.py` to create a new Admin user.

### 6. Run the Project

Start the development server with:

```bash
python -m flask run
```
open your browser and visit: http://127.0.0.1:5000
