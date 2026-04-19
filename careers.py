# careers.py
# Careers Page & Job Application Handler
# Handles public application form submission and storage
# Author: Franklin Diaz | Date: 2026-04-17

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
from werkzeug.utils import secure_filename
from database import get_db

careers_bp = Blueprint('careers', __name__, url_prefix='/careers')

# Allowed file extensions for resume uploads
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    """Helper: Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@careers_bp.route('/')
def careers_page():
    """Public careers page with application form (Use Case 6)"""
    return render_template('careers.html')

@careers_bp.route('/submit', methods=['POST'])
def submit_application():
    """Process job application submission (Use Case 6)"""
    # Validate required fields
    applicant_name = request.form.get('applicantName', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    if not applicant_name or not email or '@' not in email:
        flash('Please fill in all required fields with valid information.', 'error')
        return render_template('careers.html', form_name = applicant_name, form_email = email, form_phone = phone)
    
    # Handle resume upload
    resume_file = request.files.get('resume')
    resume_filename = None
    
    if resume_file and resume_file.filename != '' and allowed_file(resume_file.filename):
        filename = secure_filename(resume_file.filename)
        # Save to static/uploads/resumes/ (create dir if needed)
        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'resumes')
        os.makedirs(upload_folder, exist_ok=True)
        resume_filename = f"{applicant_name}_{filename}"  # Avoid collisions
        resume_file.save(os.path.join(upload_folder, resume_filename))
    else:
        flash('Please upload a valid resume file (PDF, DOC, DOCX, or TXT).', 'error')
        return render_template('careers.html', form_name = applicant_name, form_email = email, form_phone = phone)
    
    # Save to database
    conn = get_db()
    conn.execute('''
        INSERT INTO job_application (applicantName, email, phone, resumeFile, status, submittedDate)
        VALUES (?, ?, ?, ?, 'Pending', DATE('now'))
    ''', (applicant_name, email, phone, resume_filename))
    conn.commit()
    conn.close()
    
    flash('Thank you for applying! Your application has been submitted.', 'success')
    return redirect(url_for('careers.careers_page'))