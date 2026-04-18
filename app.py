# app.py
# Description: Main Flask application file for the
#              Roofing Service Management System.
# Author: Cristian Parga
# Date: Apr 4, 2026

from flask import Flask, redirect, url_for
from database import init_db
from auth import auth
from reviews import reviews
from admin import admin_bp
from careers import careers_bp

app = Flask(__name__)
app.secret_key = 'roofing_secret_key_2024'

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(reviews)
app.register_blueprint(admin_bp)
app.register_blueprint(careers_bp)

# Initiate database tables when the app opens
with app.app_context():
    init_db()

# Home route redirects to login
@app.route('/')
def home():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)