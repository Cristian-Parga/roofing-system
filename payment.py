# payment.py
# Description: Handles payment processing, viewing estimates, and generates receipts.
# Author: Cristian Parga
# Date: April 15, 2025

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db
from datetime import date
import random
import string

payment = Blueprint('payment', __name__)
# Receipt Number
def generate_receipt_number():
    """Generate a unique receipt number."""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
    return 'Receipt-' + random_part

# Payment Page
@payment.route('/payment')
def view_payments():
    """Show all estimates for the logged in customer."""
    # Viewed by customers logged in
    if session.get('role') != 'customer':
        flash('You must be logged in to view payments.', 'error')
        return redirect(url_for('auth.login'))
    customer_id = session.get('user_id')
    conn = get_db()
    # Get estimates for customer
    estimates = conn.execute('''
        SELECT estimate.*, inspection_request.propertyAddress
        FROM estimate
        JOIN inspection_request ON estimate.requestID = inspection_request.requestID
        WHERE inspection_request.customerID = ?
        AND estimate.approvalStatus = 'Approved'
    ''', (customer_id,)).fetchall()
    conn.close()
    return render_template('payment.html', estimates = estimates)

# View a estimate and pay
@payment.route('/payment/<int:estimate_id>', methods = ['GET', 'POST'])
def make_payment(estimate_id):
    """Show payment form for a estimate and handle payment."""
    # Only a customer can make a payment
    if session.get('role') != 'customer':
        flash('You must be logged in to process payments.', 'error')
        return redirect(url_for('auth.login'))
    conn = get_db()
    # Get estimate details 
    estimate = conn.execute('''
        SELECT estimate.*, inspection_request.propertyAddress
        FROM estimate
        JOIN inspection_request ON estimate.requestID = inspection_request.requestID
        WHERE estimate.estimateID = ?
    ''', (estimate_id,)).fetchone()
    # Redirect if estimate not found
    if not estimate:
        flash('Estimate not found.','error')
        conn.close()
        return redirect(url_for('payment.view_payment'))
    if request.method == 'POST':
        # Card input from form
        card_number = request.form['cardNumber'].replace(' ', '')
        expiry = request.form['expiry']
        cvv = request.form['cvv']
        amount = request.form['amount']
        # Validate card input
        if len(card_number) != 16:
            flash('Card number must be 16 digits.', 'error')
            return redirect(url_for('payment.make_payment', estimate_id=estimate_id))
        if len(cvv) != 3:
            flash('CVV must be 3 digits.', 'error')
            return redirect(url_for('payment.make_payment', estimate_id=estimate_id))
        if not expiry or len(expiry) != 5 or expiry[2] != '/':
            flash('Expiry must be in MM/YY format.', 'error')
            return redirect(url_for('payment.make_payment', estimate_id=estimate_id))
        if not card_number.isdigit() or not cvv.isdigit():
            flash('Card number and CVV must be numeric.', 'error')
            return redirect(url_for('payment.make_payment', estimate_id=estimate_id))
        if expiry < date.today().strftime('%m/%y'):
            flash('Card has expired.', 'error')
            return redirect(url_for('payment.make_payment', estimate_id=estimate_id))
        # Convert amount to float and validate
        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid payment amount.', 'error')
            conn.close()
            return redirect(url_for('payment.make_payment', estimate_id = estimate_id))
        # Check if amount is sufficient
        if amount > estimate['balance']:
            flash('Payment amount cannot exceed the balance due.', 'error')
            conn.close()
            return redirect(url_for('payment.make_payment', estimate_id = estimate_id))
        if amount <= 0:
            flash('Payment amount must be greater than zero.', 'error')
            conn.close()
            return redirect(url_for('payment.make_payment', estimate_id = estimate_id))
        # Generate receipt number
        receipt_number = generate_receipt_number()
        today = str(date.today())
        card_last_four = card_number[-4:]
        # Save payment to database
        conn.execute('''
            INSERT INTO payment (estimateID, amount, paymentDate, cardLastFour, receiptNumber)
            VALUES (?, ?, ?, ?, ?)
        ''', (estimate_id, amount, today, card_last_four, receipt_number))
        # Update balance
        new_balance = estimate['balance'] - amount
        new_amount_paid = estimate['amountPaid'] + amount
        conn.execute('''
            UPDATE estimate
            SET balance = ?, amountPaid = ?
            WHERE estimateID = ?
        ''', (new_balance, new_amount_paid, estimate_id))
        # If balance is zero, change status to paid
        if new_balance <= 0:
            conn.execute('''
                UPDATE inspection_request
                SET status = 'Paid'
                WHERE requestID = ?
            ''', (estimate['requestID'],))
        conn.commit()
        conn.close()
        flash('Payment successful! Your receipt number is ' + receipt_number, 'success')
        return redirect(url_for('payment.receipt', receipt_number = receipt_number))
    conn.close()
    return render_template('make_payment.html', estimate = estimate)

# Receipt Page
@payment.route('/payment/receipt/<receipt_number>')
def receipt(receipt_number):
    """Show receipt details for a payment."""
    # Only customers can view receipts
    if session.get('role') != 'customer':
        flash('You must be logged in to view receipts.', 'error')
        return redirect(url_for('auth.login'))
    customer_id = session.get('user_id')
    conn = get_db()
    # Get payment details
    payment_record = conn.execute('''
        SELECT payment.*, inspection_request.propertyAddress
        FROM payment
        JOIN estimate ON payment.estimateID = estimate.estimateID
        JOIN inspection_request ON estimate.requestID = inspection_request.requestID
        WHERE payment.receiptNumber = ?
        ORDER BY payment.paymentDate DESC
    ''', (receipt_number,)).fetchall()
    conn.close()
    if not payment_record:
        flash('Receipt not found.', 'error')
        return redirect(url_for('payment.view_payment'))
    return render_template('receipt.html', payment = payment_record)

# Payment History
@payment.route('/payment/history')
def payment_history():
    """Show all past payments for customer."""
    # Only customers can view payment history
    if session.get('role') != 'customer':
        flash('You must be logged in to view payment history.', 'error')
        return redirect(url_for('auth.login'))
    customer_id = session.get('user_id')
    conn = get_db()
    # Get payment history
    payment_history = conn.execute('''
        SELECT payment.*, inspection_request.propertyAddress
        FROM payment
        JOIN estimate ON payment.estimateID = estimate.estimateID
        JOIN inspection_request ON estimate.requestID = inspection_request.requestID
        WHERE inspection_request.customerID = ?
        ORDER BY payment.paymentDate DESC
    ''', (customer_id,)).fetchall()
    conn.close()
    return render_template('payment_history.html', payments = payment_history)