# Author: Cristian Parga
# Date: April 13, 2026
# Description: Handles the reviews page for the Natsu Roofing Service Management System.

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import flask
from database import get_db
from datetime import date

reviews = Blueprint('reviews', __name__)

# View all reviews
@reviews.route('/reviews')
def view_reviews():
    """Display all reviews sorted by most recent."""
    conn = get_db()
    all_reviews = conn.execute('''
                               SELECT review.*, customer.name as customer_name
                               FROM review
                               JOIN customer ON review.customer_id = customer.id
                               ''').fetchall()
    conn.close()
    return render_template('reviews.html', reviews=all_reviews)
# Submit review
@reviews.route('/reviews/submit', methods=['GET', 'POST'])
def submit_review():
    '''Show review form and handle submission.'''
    # Only customers can submit reviews
    if session.get('role') != 'customer':
        flash('Only customers can submit reviews.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        customer_id = session.get('user_id')
        star_rating = request.form('starRating')
        comments = request.form('comments')
        today = str(date.today())
    # Validate input
        if not comments:
            flash('Please enter a comment.', 'error')
            return redirect(url_for('reviews.submit_review'))

        conn = get_db()
        conn.execute('''
            INSERT INTO review (customerID, starRating, comments, submittedDate)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, star_rating, comments, today))
        conn.commit()
        conn.close()

        flash('Review submitted successfully!', 'success')
        return redirect(url_for('reviews.view_reviews'))

    return render_template('submit_review.html')