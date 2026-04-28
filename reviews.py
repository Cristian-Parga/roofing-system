# Author: Cristian Parga
# Date: April 13, 2026
# Description: Handles the reviews page for the Natsu Roofing Service Management System.

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db
from datetime import date

reviews = Blueprint('reviews', __name__)

# View all reviews
@reviews.route('/reviews')
def view_reviews():
    """Display all reviews sorted by most recent."""
    conn = get_db()
    all_reviews = conn.execute('''
                               SELECT review.*, customer.name as customerName
                               FROM review
                               JOIN customer ON review.customerID = customer.customerID
                               ORDER BY review.submittedDate DESC
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
    star_rating = request.form['starRating']
    comments    = request.form['comments']
    today       = str(date.today())
    # Open one connection for everything
    conn = get_db()
    # Check if customer already submitted a review
    existing = conn.execute(
        'SELECT reviewID FROM review WHERE customerID = ?',
        (customer_id,)
    ).fetchone()

    if existing:
        conn.close()
        flash('You have already submitted a review.', 'error')
        return redirect(url_for('reviews.view_reviews'))

    # Validate comments
    if not comments:
        conn.close()
        flash('Please enter a comment.', 'error')
        return redirect(url_for('reviews.submit_review'))

    # Validate star rating
    if not star_rating or int(star_rating) < 1 or int(star_rating) > 5:
        conn.close()
        flash('Please select a star rating between 1 and 5.', 'error')
        return redirect(url_for('reviews.submit_review'))

    # Save review to database
    conn.execute('''
        INSERT INTO review (customerID, starRating, comments, submittedDate)
        VALUES (?, ?, ?, ?)
    ''', (customer_id, int(star_rating), comments, today))
    conn.commit()
    conn.close()

    flash('Review submitted successfully!', 'success')
    return redirect(url_for('reviews.view_reviews'))