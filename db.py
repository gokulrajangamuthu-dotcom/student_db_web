"""
db.py
Handles the MySQL database connection.
Works locally (uses defaults) AND on Railway (reads env vars Railway injects automatically).
"""

import os
import mysql.connector
from mysql.connector import Error
import sys


def get_connection():
    """
    Creates and returns a new MySQL connection.
    Railway automatically provides MYSQLHOST, MYSQLUSER, MYSQLPASSWORD,
    MYSQLDATABASE, MYSQLPORT as environment variables when you attach
    a MySQL service to your project.

    Locally, it falls back to your local MySQL (edit the defaults below
    if your local password is different).
    """
    config = {
        "host": os.environ.get("MYSQLHOST", "localhost"),
        "user": os.environ.get("MYSQLUSER", "root"),
        "password": os.environ.get("MYSQLPASSWORD", "Gokul@123"),
        "database": os.environ.get("MYSQLDATABASE", "student_db"),
        "port": int(os.environ.get("MYSQLPORT", 3306)),
    }
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        print(f"\n[ERROR] Could not connect to MySQL: {e}")
        sys.exit(1)
