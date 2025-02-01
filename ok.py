from flask import Flask, request, jsonify
import mysql.connector
import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# MySQL connection details
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'port': '3306',
    'password': '3isha417',
    'database': 'sprintparkwebsite'
}


def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Password Validation Function
def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[@$!%*?&]', password):
        return False, "Password must contain at least one special character (@$!%*?&)."
    return True, None

# Signup Endpoint
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    required_fields = ["username", "email", "password", "full_name", "designation", "reporting_manager", "employee_id", "mobile_number", "location", "date_of_birth", "blood_group"]
    if not all(data.get(field) for field in required_fields):
        return jsonify({"error": "All fields are required."}), 400
    
    is_valid, error_msg = is_strong_password(data['password'])
    if not is_valid:
        return jsonify({"error": error_msg}), 400
    
    data['password'] = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed."}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, designation, reporting_manager, employee_id, mobile_number, location, date_of_birth, blood_group, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (data['username'], data['email'], data['password'], data['full_name'], data['designation'], data['reporting_manager'], data['employee_id'], data['mobile_number'], data['location'], data['date_of_birth'], data['blood_group'], 'active'))
        conn.commit()
        return jsonify({"message": "User signed up successfully."}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username, email, or employee ID already exists."}), 409
    finally:
        cursor.close()
        conn.close()

# Signin Endpoint
@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON format. Please check."}), 400
    
    required_fields = ["username", "password"]
    if not all(data.get(field) for field in required_fields):
        return jsonify({"error": "All fields are required."}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed."}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT email, password, status, full_name, designation, reporting_manager, employee_id FROM users WHERE username = %s', (data['username'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User does not exist."}), 404
        if user['status'] != 'active':
            return jsonify({"error": "Account is not active."}), 403
        
        if check_password_hash(user['password'], data['password']):
            return jsonify({
                "message": "Signin successful.",
                "full_name": user["full_name"],
                "designation": user["designation"],
                "reporting_manager": user["reporting_manager"],
                "employee_id": user["employee_id"],
                "email": user["email"]
            }), 200
        else:
            return jsonify({"error": "Invalid password."}), 401
    finally:
        cursor.close()
        conn.close()

# Get All Employees Endpoint
@app.route('/getAllEmployees', methods=['GET'])
def get_all_employees():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed."}), 500
    
    cursor = conn.cursor(dictionary=True)   
    try:
        cursor.execute('SELECT username, email, full_name, designation, reporting_manager, employee_id, mobile_number, location, date_of_birth, blood_group, status FROM users')
        employees = cursor.fetchall()
        return jsonify({"employees": employees}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
