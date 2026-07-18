"""
api/index.py
Vercel's Python runtime looks for a WSGI app named `app` in this file.
This just imports the real Flask app from the project root.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402  (Vercel's WSGI entrypoint)