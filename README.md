# Natsu Roofing Management System

A web-based roofing service management system built with Python and Flask.
Allows customers to submit inspection requests, track project status, make
payments, and leave reviews. Administrators can manage requests, create
estimates, and review job applications.

## Built using Python, Flask, HTML/CSS, SQLite

**1. Clone the repository**
git clone https://github.com/Cristian-Parga/roofing-system.git cd roofing-system

**2. Create and activate a virtual environment**
python -m venv venv
source venv/bin/activate        # Mac
venv\Scripts\activate           # Windows

**3. Install dependencies**
pip install flask werkzeug

**4. Create the admin account**
python setup_demo_admin.py

**5. Run the app**
python app.py

**6. Open in browser**
http://127.0.0.1:5001

## Demo Accounts
| Admin | admin@test.com | admin123 | /n
| Customer | Register a new account |

## Features
- Customer account registration and login
- Inspection request submission with emergency flagging
- Admin dashboard for managing requests and updating status
- Estimate creation by administrators
- Online payment processing with receipt generation
- Customer reviews page
- Job application careers page
- Role based access control

## Team
- Cristian Parga
- Franklin Diaz
- Khoi Tran

## Course
Software Engineering — University of Houston-Downtown

