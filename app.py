# app.py
# Description: Main Flask application file for the
#              Roofing Service Management System.
# Author: Cristian Parga
# Date: Apr 4, 2026

from flask import Flask, redirect, render_template, session, url_for
from database import get_db, init_db
from auth import auth
from reviews import reviews
from admin import admin_bp
from careers import careers_bp
from payment import payment
from customer import customer

app = Flask(__name__)
app.secret_key = 'roofing_secret_key_2026'

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(reviews)
app.register_blueprint(admin_bp)
app.register_blueprint(careers_bp)
app.register_blueprint(payment)
app.register_blueprint(customer)

# Initiate database tables when the app opens
with app.app_context():
    init_db()

# Redirect users to their respective dashboards based on role
@app.route('/')
def home():
    # If logged in direct dashboard
    if session.get('role') == 'customer':
        return redirect(url_for('customer.dashboard')) 
    elif session.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    # Else show homepage
    return render_template('home.html')
    
@app.route('/setup-admin')
def setup_admin():
    from werkzeug.security import generate_password_hash
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO administrator (name, email, password, role)
            VALUES (?, ?, ?, ?)
        ''', ('Demo Admin', 'admin@test.com', generate_password_hash('admin123'), 'Admin'))
        conn.commit()
        conn.close()
        return 'Admin created successfully. Delete this route now.'
    except:
        conn.close()
        return 'Admin already exists.'

if __name__ == '__main__':
    app.run(debug=True, port=5001)