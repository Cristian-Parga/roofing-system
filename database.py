# database.py
# Description: Sets up the SQLite database and creates all tables
#              for the Roofing Service Management System.
# Author: Cristian Parga
# Date: Apr 6, 2026

import sqlite3
import os

# Database file will be created in the same folder as this file
DATABASE = 'roofing.db'

def get_db():
    """Connect to the database and return the connection."""
    conn = sqlite3.connect(DATABASE)
    # Access columns by name instead of index
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create all tables if they do not already exist."""
    conn = get_db()
    cursor = conn.cursor()

    # Customer table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer (
            customerID    INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password      TEXT NOT NULL,
            phone         TEXT,
            address       TEXT
        )
    ''')

    # Administrator table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS administrator (
            adminID       INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password      TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'Staff'
        )
    ''')

    # InspectionRequest table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspection_request (
            requestID       INTEGER PRIMARY KEY AUTOINCREMENT,
            customerID      INTEGER NOT NULL,
            propertyAddress TEXT NOT NULL,
            description     TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'Pending',
            isEmergency     INTEGER NOT NULL DEFAULT 0,
            photoURL        TEXT,
            submittedDate   TEXT NOT NULL,
            FOREIGN KEY (customerID) REFERENCES customer(customerID)
        )
    ''')

    # Estimate table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estimate (
            estimateID      INTEGER PRIMARY KEY AUTOINCREMENT,
            requestID       INTEGER NOT NULL,
            totalCost       REAL NOT NULL DEFAULT 0.00,
            amountPaid      REAL NOT NULL DEFAULT 0.00,
            balance         REAL NOT NULL DEFAULT 0.00,
            createdDate     TEXT NOT NULL,
            approvalStatus  TEXT NOT NULL DEFAULT 'Pending',
            FOREIGN KEY (requestID) REFERENCES inspection_request(requestID)
        )
    ''')

    # Payment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment (
            paymentID       INTEGER PRIMARY KEY AUTOINCREMENT,
            estimateID      INTEGER NOT NULL,
            amount          REAL NOT NULL,
            paymentDate     TEXT NOT NULL,
            cardLastFour    TEXT NOT NULL,
            receiptNumber   TEXT NOT NULL,
            FOREIGN KEY (estimateID) REFERENCES estimate(estimateID)
        )
    ''')

    # Review table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS review (
            reviewID        INTEGER PRIMARY KEY AUTOINCREMENT,
            customerID      INTEGER NOT NULL,
            starRating      INTEGER NOT NULL,
            comments        TEXT NOT NULL,
            photoURL        TEXT,
            submittedDate   TEXT NOT NULL,
            FOREIGN KEY (customerID) REFERENCES customer(customerID)
        )
    ''')

    # JobApplication table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_application (
            applicationID   INTEGER PRIMARY KEY AUTOINCREMENT,
            applicantName   TEXT NOT NULL,
            email           TEXT NOT NULL,
            phone           TEXT,
            resumeFile      TEXT,
            status          TEXT NOT NULL DEFAULT 'Pending',
            submittedDate   TEXT NOT NULL
        )
    ''')

    # Save changes and close connection
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Run this file directly to create the database
if __name__ == '__main__':
    init_db()