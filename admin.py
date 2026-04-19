# admin.py
# Admin Dashboard & Request Management Controller
# Handles inspection request viewing, status updates, and job application review
# Author: Franklin Diaz | Date: 2026-04-17

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from database import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to ensure only admins can access these routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Display all inspection requests with current status (Use Case 4)"""
    conn = get_db()
    # Fetch requests with customer info via JOIN
    requests = conn.execute('''
        SELECT ir.requestID, ir.propertyAddress, ir.status, ir.isEmergency, 
               ir.submittedDate, c.name as customerName, c.email
        FROM inspection_request ir
        JOIN customer c ON ir.customerID = c.customerID
        ORDER BY ir.submittedDate DESC
    ''').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', requests=requests_list)

@admin_bp.route('/update-status/<int:request_id>', methods=['GET', 'POST'])
@admin_required
def update_status(request_id):
    """Update status of a specific inspection request (Use Case 4)"""
    if request.method == 'POST':
        new_status = request.form.get('status')
        valid_statuses = ['Pending', 'Emergency Flagged', 'Scheduled', 'In Progress', 
                         'Estimate Sent', 'Approved', 'Cancelled', 'Payment Pending', 'Paid', 'Completed']
        
        if new_status not in valid_statuses:
            flash('Invalid status selection.', 'error')
            return redirect(url_for('admin.update_status', request_id=request_id))
        
        conn = get_db()
        
        conn.execute('UPDATE inspection_request SET status = ? WHERE requestID = ?', 
                    (new_status, request_id))
        conn.commit()
        
        conn.close()
        flash(f'Request #{request_id} status updated to "{new_status}".', 'success')
        return redirect(url_for('admin.dashboard'))
    
    # GET: Show current request details for status update
    conn = get_db()
    request_data = conn.execute('''
        SELECT ir.*, c.name as customerName, c.email, c.phone
        FROM inspection_request ir
        JOIN customer c ON ir.customerID = c.customerID
        WHERE ir.requestID = ?
    ''', (request_id,)).fetchone()
    conn.close()
    
    if not request_data:
        flash('Request not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('update_status.html', red_data = request_data)

@admin_bp.route('/applications')
@admin_required
def applications():
    """View all submitted job applications (Use Case 7)"""
    conn = get_db()
    
    applications = conn.execute('''
        SELECT applicationID, applicantName, email, phone, resumeFile, status, submittedDate
        FROM job_application
        ORDER BY submittedDate DESC
    ''').fetchall()
    conn.close()
    return render_template('applications.html', applications=applications)

@admin_bp.route('/applications/<int:app_id>/review', methods=['POST'])
@admin_required
def review_application(app_id):
    """Approve or reject a job application (Use Case 7)"""
    decision = request.form.get('decision')  # 'Approved' or 'Rejected'
    if decision not in ['Approved', 'Rejected']:
        flash('Invalid decision.', 'error')
        return redirect(url_for('admin.applications'))
    
    conn = get_db()
    
    conn.execute('UPDATE job_application SET status = ? WHERE applicationID = ?', 
                (decision, app_id))
    conn.commit()
    
    conn.close()
    flash(f'Application #{app_id} {decision.lower()}.', 'success')
    return redirect(url_for('admin.applications'))