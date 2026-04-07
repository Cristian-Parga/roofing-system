# auth.py
# Description: Handles all account related routes including
#              login, logout, and account creation.
# Author: Cristian Parga
# Date: Apr 6, 2026

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

# Blueprint lets us organize routes into separate files
auth = Blueprint('auth', __name__)

# Create account
@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Show registration form and handle account creation."""

    if request.method == 'POST':
        # Collect form input
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']
        phone    = request.form['phone']
        address  = request.form['address']

        # Validate that required fields are not empty
        if not name or not email or not password:
            flash('Name, email, and password are required.', 'error')
            return redirect(url_for('auth.register'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        conn = get_db()
        try:
            # Insert new customer into the database
            conn.execute('''
                INSERT INTO customer (name, email, password, phone, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, email, hashed_password, phone, address))
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception:
            # Email already used
            flash('An account with that email already exists.', 'error')
            return redirect(url_for('auth.register'))

        finally:
            conn.close()

    # Get request: just show the registration form
    return render_template('register.html')


# Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Show login form and handle authentication."""

    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        conn = get_db()

        # Check if email belongs to a customer
        customer = conn.execute(
            'SELECT * FROM customer WHERE email = ?', (email,)
        ).fetchone()

        # Check if email belongs to an admin
        admin = conn.execute(
            'SELECT * FROM administrator WHERE email = ?', (email,)
        ).fetchone()

        conn.close()

        # Validate customer login
        if customer and check_password_hash(customer['password'], password):
            session['user_id']   = customer['customerID']
            session['user_name'] = customer['name']
            session['role']      = 'customer'
            flash('Welcome back, ' + customer['name'] + '!', 'success')
            return redirect(url_for('customer.dashboard'))

        # Validate admin login
        elif admin and check_password_hash(admin['password'], password):
            session['user_id']   = admin['adminID']
            session['user_name'] = admin['name']
            session['role']      = 'admin'
            flash('Welcome back, ' + admin['name'] + '!', 'success')
            return redirect(url_for('admin.dashboard'))

        else:
            flash('Incorrect email or password.', 'error')
            return redirect(url_for('auth.login'))

    # Get request: just show the login form
    return render_template('login.html')


# Logout
@auth.route('/logout')
def logout():
    """Clear the session and redirect to login."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))