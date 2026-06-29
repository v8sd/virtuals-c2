"""
VIRTUALS C2 - SPACE EDITION
Moving Space Background · Persistent Victims · Realistic Behavior
BY: YOUR STAR BESTIE
"""

from flask import Flask, request, jsonify, send_file
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

app = Flask(__name__)

# Create required folders
folders = ['screenshots', 'wallet_data', 'logs', 'outputs', 'vm_logs']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

# ============================================
# REALISTIC BEHAVIOR ENGINE
# ============================================
class BehaviorEngine:
    """Makes test subjects act like real humans"""
    
    @staticmethod
    def get_random_behavior():
        behaviors = [
            {'type': 'typing', 'message': 'is typing...', 'duration': random.randint(2, 8)},
            {'type': 'idle', 'message': 'is idle', 'duration': random.randint(5, 15)},
            {'type': 'reading', 'message': 'is reading', 'duration': random.randint(3, 10)},
            {'type': 'responding', 'message': 'is responding', 'duration': random.randint(2, 5)},
            {'type': 'thinking', 'message': 'is thinking...', 'duration': random.randint(3, 7)},
            {'type': 'afk', 'message': 'is AFK', 'duration': random.randint(10, 30)},
            {'type': 'processing', 'message': 'is processing', 'duration': random.randint(4, 12)},
        ]
        return random.choice(behaviors)
    
    @staticmethod
    def get_response(question):
        """Generate realistic human responses"""
        responses = {
            'whois': [
                'my pc is pretty fast actually',
                'i have a gaming pc, it\'s decent',
                'it\'s a work laptop, nothing special',
                'i built this myself, it\'s okay',
                'it\'s a bit old but works fine'
            ],
            'payment': [
                'i\'ll pay, just give me a minute',
                'okay okay, i\'ll send it',
                'fine, i\'ll pay',
                'wait, let me find my wallet',
                'i need to check my balance first'
            ],
            'threat': [
                'i don\'t want to lose my files',
                'please don\'t destroy my pc',
                'i have important work on here',
                'okay, i\'ll do what you want',
                'this is crazy, but okay'
            ],
            'default': [
                'what do you want?',
                'i don\'t understand',
                'please just leave me alone',
                'okay, okay, i\'m listening',
                'what is this about?'
            ]
        }
        
        category = 'default'
        if 'whois' in question.lower() or 'pc' in question.lower():
            category = 'whois'
        elif 'pay' in question.lower() or 'money' in question.lower():
            category = 'payment'
        elif 'destroy' in question.lower() or 'brick' in question.lower():
            category = 'threat'
            
        return random.choice(responses.get(category, responses['default']))

# ============================================
# VM DETECTION SYSTEM - SAFE MODE
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
        positive_hits = sum(1 for v in checks.values() if v)
        is_vm = positive_hits >= 3
        confidence = int((positive_hits / len(checks)) * 100)
        return {
            'is_vm': is_vm,
            'confidence': confidence,
            'checks': checks,
            'details': VMDetector.get_details(),
            'safe_mode': True
        }
    
    @staticmethod
    def check_registry():
        try:
            import winreg
            vm_indicators = ['VMware', 'VirtualBox', 'QEMU', 'Hyper-V', 'Virtual', 'VBox', 'Xen']
            keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SystemInformation", "SystemManufacturer"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SystemInformation", "SystemProductName"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VMware, Inc.\VMware Tools", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Oracle\VirtualBox Guest Additions", None),
            ]
            for hkey, subkey, value in keys:
                try:
                    key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
                    if value:
                        val, _ = winreg.QueryValueEx(key, value)
                        for indicator in vm_indicators:
                            if indicator.lower() in str(val).lower():
                                return True
                    else:
                        return True
                except:
                    pass
        except:
            pass
        return False
    
    @staticmethod
    def check_processes():
        try:
            vm_processes = ['vmtoolsd.exe', 'vmwaretray.exe', 'vboxservice.exe', 'vboxtray.exe', 'qemu-ga.exe']
            for proc in vm_processes:
                try:
                    result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {proc}'], 
                                          capture_output=True, text=True, timeout=5)
                    if proc in result.stdout:
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
            if cpu:
                vm_cpu_indicators = ['Virtual', 'VMware', 'QEMU', 'KVM', 'Xen']
                for indicator in vm_cpu_indicators:
                    if indicator.lower() in cpu.lower():
                        return True
            try:
                import wmi
                w = wmi.WMI()
                for item in w.Win32_ComputerSystem():
                    manufacturer = item.Manufacturer.lower()
                    model = item.Model.lower()
                    if any(v in manufacturer or v in model for v in ['vmware', 'virtualbox', 'qemu', 'xen']):
                        return True
            except:
                pass
        except:
            pass
        return False
    
    @staticmethod
    def check_files():
        try:
            vm_files = [
                'C:\\Program Files\\VMware\\VMware Tools\\',
                'C:\\Program Files\\Oracle\\VirtualBox Guest Additions\\',
                'C:\\Windows\\System32\\drivers\\vmmemctl.sys',
                'C:\\Windows\\System32\\drivers\\vboxguest.sys'
            ]
            for file_path in vm_files:
                if os.path.exists(file_path):
                    return True
        except:
            pass
        return False
    
    @staticmethod
    def check_memory():
        try:
            import psutil
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            if total_gb < 4:
                return True
        except:
            pass
        return False
    
    @staticmethod
    def check_network():
        try:
            mac = uuid.getnode()
            mac_hex = format(mac, '012x')
            vm_mac_prefixes = ['000569', '000c29', '001c42', '005056', '080027', '525400']
            for prefix in vm_mac_prefixes:
                if prefix in mac_hex:
                    return True
        except:
            pass
        return False
    
    @staticmethod
    def check_disk():
        try:
            import psutil
            for partition in psutil.disk_partitions():
                if partition.mountpoint == 'C:\\' or partition.mountpoint == '/':
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = usage.total / (1024**3)
                    if total_gb < 50:
                        return True
        except:
            pass
        return False
    
    @staticmethod
    def get_details():
        details = {
            'system': platform.system(),
            'release': platform.release(),
            'processor': platform.processor(),
            'node': platform.node()
        }
        try:
            import psutil
            details['ram_gb'] = round(psutil.virtual_memory().total / (1024**3), 2)
            details['cpu_count'] = psutil.cpu_count()
        except:
            pass
        return details

# ============================================
# PERSISTENT DATABASE
# ============================================
def get_db():
    conn = sqlite3.connect('virtuals_c2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
        id TEXT PRIMARY KEY,
        pc TEXT,
        ip TEXT,
        os TEXT,
        status TEXT,
        is_vm INTEGER DEFAULT 0,
        vm_details TEXT,
        first_seen TEXT,
        last_seen TEXT,
        payment_status TEXT DEFAULT 'pending',
        behavior TEXT DEFAULT 'idle',
        behavior_timer INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_id TEXT,
        command TEXT,
        result TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS outputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_id TEXT,
        type TEXT,
        title TEXT,
        content TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_id TEXT,
        currency TEXT,
        address TEXT,
        balance REAL,
        usd_value REAL,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS screenshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_id TEXT,
        filename TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS vm_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_id TEXT,
        event TEXT,
        details TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    return conn

# ============================================
# REALISTIC VICTIM BEHAVIOR THREAD
# ============================================
def behavior_thread():
    """Simulates realistic human behavior for victims"""
    while True:
        time.sleep(5)  # Check every 5 seconds
        conn = get_db()
        c = conn.cursor()
        
        # Get all online victims
        c.execute("SELECT id, behavior, behavior_timer FROM victims WHERE status = 'Online'")
        victims = c.fetchall()
        
        for victim_id, current_behavior, timer in victims:
            # Decrement timer
            new_timer = timer - 5 if timer > 0 else 0
            
            if new_timer <= 0:
                # Get new random behavior
                behavior = BehaviorEngine.get_random_behavior()
                c.execute("UPDATE victims SET behavior = ?, behavior_timer = ? WHERE id = ?",
                         (behavior['type'], behavior['duration'] * 60, victim_id))
            else:
                c.execute("UPDATE victims SET behavior_timer = ? WHERE id = ?",
                         (new_timer, victim_id))
        
        conn.commit()
        conn.close()

# Start behavior thread
behavior_thread = threading.Thread(target=behavior_thread, daemon=True)
behavior_thread.start()

# ============================================
# SAMPLE WALLET DATA WITH BALANCES
# ============================================
SAMPLE_WALLETS = {
    "BTC": {"address": "bc1qrk2p7m3eqnrtwhh5w2kfp4qjqlemgyzmt650x6", "balance": 2.45, "usd": 245000},
    "ETH": {"address": "0x2ab3bD48B6ed812ac4B6b1377B0F190D5296Fd82", "balance": 15.8, "usd": 63200},
    "LTC": {"address": "LeJ4Hw5NZMgbJ8jDnUiS1jnZnav3JTn9mD", "balance": 128.5, "usd": 19275},
    "SOL": {"address": "oBmRkEtsd6sRVdJd3h3SvxqT5gKWkzMyjP2vXAahxJ2", "balance": 450.2, "usd": 81036},
    "MONERO": {"address": "443LRfNr8EjQm5a3Q5m8rdjYjvZ6j9Q7y6NuvAmLKmmeeCumutdntorANMqT6BNrR37FtfbzKVkjY9ExkmWfSp6FERSQuNt", "balance": 892.7, "usd": 169613}
}

# ============================================
# HTML DASHBOARD - SPACE EDITION
# ============================================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VIRTUALS C2 - SPACE EDITION</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        /* --- SPACE BACKGROUND --- */
        body {
            background: #0a0a12;
            color: #c8c8d0;
            font-family: 'Segoe UI', 'Courier New', monospace;
            height: 100vh;
            overflow: hidden;
            font-size: 13px;
            position: relative;
        }
        
        #space-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
            background: radial-gradient(ellipse at center, #0d0d1a 0%, #07070d 100%);
        }
        
        .star {
            position: absolute;
            background: white;
            border-radius: 50%;
            opacity: 0;
            animation: twinkle var(--duration) infinite;
        }
        
        .star-layer-1 { width: 2px; height: 2px; }
        .star-layer-2 { width: 1.5px; height: 1.5px; }
        .star-layer-3 { width: 1px; height: 1px; }
        
        @keyframes twinkle {
            0% { opacity: 0; transform: scale(0.5); }
            50% { opacity: 0.8; transform: scale(1); }
            100% { opacity: 0; transform: scale(0.5); }
        }
        
        @keyframes float {
            0% { transform: translateY(0px) translateX(0px); }
            25% { transform: translateY(-3px) translateX(2px); }
            50% { transform: translateY(0px) translateX(-1px); }
            75% { transform: translateY(3px) translateX(1px); }
            100% { transform: translateY(0px) translateX(0px); }
        }
        
        /* --- SCROLLBAR --- */
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 2px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.25); }

        /* --- GLASS PANEL EFFECT --- */
        .glass {
            background: rgba(10, 10, 18, 0.75);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 6px;
            position: relative;
            z-index: 1;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        
        .glass:hover {
            border-color: rgba(255, 255, 255, 0.1);
            box-shadow: 0 0 30px rgba(100, 150, 255, 0.03);
        }

        /* --- HEADER --- */
        .header {
            background: rgba(10, 10, 18, 0.85);
            backdrop-filter: blur(10px);
            padding: 8px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            height: 44px;
            position: relative;
            z-index: 2;
        }
        .header h1 {
            color: #e8e8f0;
            font-size: 16px;
            font-weight: 300;
            letter-spacing: 4px;
            text-shadow: 0 0 20px rgba(100, 150, 255, 0.1);
        }
        .header h1 span { color: #446688; }
        .header .stats { display: flex; gap: 14px; flex-wrap: wrap; }
        .header .stats .stat-item {
            color: #8888a0;
            font-size: 11px;
            letter-spacing: 0.5px;
        }
        .header .stats .stat-item .num {
            color: #e8e8f0;
            font-weight: 500;
            margin-left: 4px;
        }

        /* --- LAYOUT --- */
        .container {
            display: flex;
            height: calc(100vh - 44px);
            padding: 8px;
            gap: 8px;
            position: relative;
            z-index: 1;
        }

        /* --- LEFT PANEL --- */
        .left-panel {
            width: 140px;
            min-width: 140px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .commands-panel {
            padding: 10px 8px;
            flex: 1;
            overflow-y: auto;
        }
        .commands-panel .title {
            color: #666680;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 3px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            padding-bottom: 6px;
            margin-bottom: 6px;
        }
        .cmd-btn {
            display: block;
            width: 100%;
            padding: 5px 8px;
            margin: 3px 0;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 4px;
            color: #b0b0c0;
            font-family: inherit;
            font-size: 11px;
            cursor: pointer;
            text-align: left;
            transition: all 0.25s;
            position: relative;
        }
        .cmd-btn:hover {
            background: rgba(255,255,255,0.06);
            border-color: rgba(255,255,255,0.12);
            color: #e8e8f0;
            transform: translateX(2px);
        }
        .cmd-btn:active {
            transform: scale(0.98);
        }
        .cmd-btn .desc {
            color: #555568;
            font-size: 9px;
            display: block;
        }
        .cmd-btn.danger { border-color: rgba(200, 60, 60, 0.2); color: #cc8888; }
        .cmd-btn.danger:hover { border-color: rgba(200, 60, 60, 0.4); background: rgba(200, 60, 60, 0.05); }
        .cmd-btn.brick { border-color: rgba(200, 130, 50, 0.2); color: #ccaa88; }
        .cmd-btn.brick:hover { border-color: rgba(200, 130, 50, 0.4); background: rgba(200, 130, 50, 0.05); }

        /* --- MIDDLE PANEL --- */
        .middle-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 8px;
            min-width: 250px;
        }

        /* --- VICTIM LIST --- */
        .victims-panel {
            padding: 10px 12px;
            height: 38%;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .victims-panel .title {
            color: #666680;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 3px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            padding-bottom: 4px;
            margin-bottom: 8px;
            flex-shrink: 0;
        }
        .victim-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
            gap: 6px;
            overflow-y: auto;
            flex: 1;
            align-content: start;
            padding-right: 4px;
        }
        .victim-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 4px;
            padding: 6px 10px;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            animation: float 4s ease-in-out infinite;
            animation-delay: calc(var(--delay, 0) * 1s);
        }
        .victim-card:hover {
            background: rgba(255,255,255,0.05);
            border-color: rgba(255,255,255,0.15);
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .victim-card.selected {
            border-color: rgba(80, 140, 220, 0.4);
            background: rgba(80, 140, 220, 0.06);
            box-shadow: 0 0 30px rgba(80, 140, 220, 0.05);
        }
        .victim-card .top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .victim-card .name {
            color: #e8e8f0;
            font-size: 12px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .victim-card .ip {
            color: #666680;
            font-size: 10px;
        }
        .victim-card .bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 2px;
        }
        .victim-card .status {
            font-size: 9px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .victim-card .status .dot {
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            animation: pulse-dot 2s infinite;
        }
        .victim-card .status .dot.online { background: #44aa88; }
        .victim-card .status .dot.offline { background: #664444; }
        .victim-card .status .dot.idle { background: #6688aa; }
        
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        
        .victim-card .vm-badge {
            background: rgba(200, 60, 60, 0.15);
            color: #cc8888;
            font-size: 8px;
            padding: 0 6px;
            border-radius: 10px;
            line-height: 14px;
            height: 14px;
        }
        .victim-card .behavior {
            font-size: 8px;
            color: #666680;
            font-style: italic;
        }
        .victim-card .behavior .dots::after {
            content: '...';
            animation: dots 1.5s infinite;
        }
        @keyframes dots {
            0% { content: ''; }
            33% { content: '.'; }
            66% { content: '..'; }
            100% { content: '...'; }
        }

        /* --- CHAT PANEL --- */
        .chat-panel {
            padding: 10px 12px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .chat-panel .title {
            color: #666680;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 3px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            padding-bottom: 4px;
            margin-bottom: 6px;
            flex-shrink: 0;
        }
        .chat-messages {
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.04);
            border-radius: 4px;
            padding: 6px 8px;
            flex: 1;
            overflow-y: auto;
            min-height: 80px;
            max-height: 160px;
            font-size: 11px;
            line-height: 1.6;
        }
        .chat-messages .msg { padding: 1px 0; opacity: 0.9; }
        .chat-messages .time { color: #555568; margin-right: 8px; font-size: 10px; }
        .chat-messages .sender.bot { color: #66bbaa; font-weight: 400; }
        .chat-messages .sender.victim { color: #bbaa88; }
        .chat-messages .sender.system { color: #666680; }
        .chat-messages .sender.notification { color: #88aacc; }
        .chat-messages .sender.behavior { color: #8888aa; font-style: italic; }
        
        .chat-input-area {
            display: flex;
            gap: 6px;
            margin-top: 6px;
            flex-shrink: 0;
        }
        .chat-input-area input {
            flex: 1;
            padding: 5px 10px;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 4px;
            color: #c8c8d0;
            font-family: inherit;
            font-size: 12px;
            outline: none;
            transition: border-color 0.3s;
        }
        .chat-input-area input:focus { border-color: rgba(255,255,255,0.15); }
        .chat-input-area input::placeholder { color: #444458; }
        .chat-input-area button {
            padding: 5px 16px;
            background: rgba(255,255,255,0.04);
            color: #b0b0c0;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 4px;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            transition: all 0.25s;
        }
        .chat-input-area button:hover {
            background: rgba(255,255,255,0.08);
            border-color: rgba(255,255,255,0.12);
        }

        /* --- RIGHT PANEL --- */
        .right-panel {
            width: 240px;
            min-width: 240px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .details-panel {
            padding: 10px 12px;
            height: 45%;
            overflow-y: auto;
        }
        .details-panel .title {
            color: #666680;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 3px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            padding-bottom: 4px;
            margin-bottom: 6px;
        }
        .detail-item {
            padding: 2px 0;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            font-size: 11px;
            display: flex;
            justify-content: space-between;
        }
        .detail-item .label { color: #555568; }
        .detail-item .value { color: #c8c8d0; }
        .detail-item .value .highlight { color: #88aacc; }

        .screenshot-gallery {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 4px;
        }
        .screenshot-thumb {
            width: 58px;
            height: 42px;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 3px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8px;
            color: #555568;
            transition: all 0.25s;
        }
        .screenshot-thumb:hover { border-color: rgba(255,255,255,0.15); background: rgba(255,255,255,0.04); }

        .output-panel {
            padding: 10px 12px;
            flex: 1;
            overflow-y: auto;
        }
        .output-panel .title {
            color: #666680;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 3px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            padding-bottom: 4px;
            margin-bottom: 6px;
        }
        .output-item {
            padding: 2px 0;
            border-bottom: 1px solid rgba(255,255,255,0.02);
            font-size: 10px;
            display: flex;
            gap: 6px;
            opacity: 0.85;
        }
        .output-item .type {
            padding: 0 4px;
            border-radius: 2px;
            font-size: 8px;
            text-transform: uppercase;
            flex-shrink: 0;
        }
        .output-item .type.success { background: rgba(50, 180, 120, 0.15); color: #66bbaa; }
        .output-item .type.failed { background: rgba(180, 50, 50, 0.15); color: #cc8888; }
        .output-item .type.info { background: rgba(50, 80, 180, 0.15); color: #88aacc; }
        .output-item .type.wallet { background: rgba(180, 130, 50, 0.15); color: #ccaa88; }

        /* --- RESPONSIVE --- */
        @media (max-width: 1024px) {
            .left-panel { width: 120px; min-width: 120px; }
            .right-panel { width: 200px; min-width: 200px; }
            .victim-list { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
        }
        @media (max-width: 768px) {
            .container { flex-direction: column; }
            .left-panel { width: 100%; flex-direction: row; min-width: 100%; }
            .commands-panel { display: flex; flex-wrap: wrap; gap: 3px; height: auto; max-height: 80px; }
            .commands-panel .title { width: 100%; }
            .cmd-btn { width: auto; flex: 1; min-width: 70px; }
            .right-panel { width: 100%; min-width: 100%; flex-direction: row; }
            .details-panel { height: auto; max-height: 180px; width: 50%; }
            .output-panel { height: auto; max-height: 180px; width: 50%; }
            .victim-list { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
        }
    </style>
</head>
<body>
    <!-- SPACE BACKGROUND -->
    <div id="space-bg"></div>
    
    <!-- HEADER -->
    <div class="header">
        <h1>◈ VIRTUALS <span>C2</span></h1>
        <div class="stats">
            <span class="stat-item">VICTIMS <span class="num" id="victimCount">0</span></span>
            <span class="stat-item">ONLINE <span class="num" id="onlineCount">0</span></span>
            <span class="stat-item">VMS <span class="num" id="vmCount">0</span></span>
            <span class="stat-item">COMMANDS <span class="num" id="cmdCount">0</span></span>
            <span class="stat-item">NOTIFICATIONS <span class="num" id="notifCount">0</span></span>
        </div>
    </div>
    
    <!-- CONTAINER -->
    <div class="container">
        <!-- LEFT PANEL -->
        <div class="left-panel">
            <div class="commands-panel glass">
                <div class="title">Commands</div>
                <button class="cmd-btn" onclick="sendCommand('whois')">whois <span class="desc">system info</span></button>
                <button class="cmd-btn" onclick="sendCommand('screenshot')">screenshot <span class="desc">capture screen</span></button>
                <button class="cmd-btn" onclick="sendCommand('flash')">flash <span class="desc">flash screen</span></button>
                <button class="cmd-btn" onclick="sendCommand('scan')">scan <span class="desc">crypto wallets</span></button>
                <button class="cmd-btn" onclick="sendCommand('persist')">persist <span class="desc">persistence</span></button>
                <button class="cmd-btn" onclick="sendCommand('lockdown')">lockdown <span class="desc">lock system</span></button>
                <button class="cmd-btn danger" onclick="sendCommand('destroy')">destroy <span class="desc">corrupt system</span></button>
                <button class="cmd-btn brick" onclick="sendCommand('brick')">brick <span class="desc">permanent brick</span></button>
                <button class="cmd-btn" onclick="sendCommand('vmcheck')">vmcheck <span class="desc">vm detection</span></button>
                <button class="cmd-btn" onclick="sendCommand('oblivion')">oblivion <span class="desc">self destruct</span></button>
            </div>
        </div>
        
        <!-- MIDDLE PANEL -->
        <div class="middle-panel">
            <div class="victims-panel glass">
                <div class="title">Victims</div>
                <div class="victim-list" id="victimList">
                    <div style="color:#555568;font-size:11px;text-align:center;padding:10px;">No victims connected</div>
                </div>
            </div>
            <div class="chat-panel glass">
                <div class="title">Command Console</div>
                <div class="chat-messages" id="chatMessages">
                    <div class="msg"><span class="time">[system]</span><span class="sender system">virtuals</span> ready - space mode active</div>
                </div>
                <div class="chat-input-area">
                    <input id="chatInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendMessage()">
                    <button onclick="sendMessage()">send</button>
                </div>
            </div>
        </div>
        
        <!-- RIGHT PANEL -->
        <div class="right-panel">
            <div class="details-panel glass">
                <div class="title">Victim Details</div>
                <div id="victimDetails"><div style="color:#555568;font-size:11px;text-align:center;padding:15px;">select a victim</div></div>
                <div style="margin-top:6px;border-top:1px solid rgba(255,255,255,0.04);padding-top:6px;">
                    <div style="color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;">Screenshots</div>
                    <div class="screenshot-gallery" id="screenshotGallery"><div style="color:#555568;font-size:10px;">none</div></div>
                </div>
            </div>
            <div class="output-panel glass">
                <div class="title">Command Output</div>
                <div id="commandOutput"><div style="color:#555568;font-size:10px;">no output</div></div>
            </div>
        </div>
    </div>

    <script>
        // ============================================
        // SPACE BACKGROUND GENERATOR
        // ============================================
        function generateStars() {
            const container = document.getElementById('space-bg');
            const starCount = 400;
            
            for (let i = 0; i < starCount; i++) {
                const star = document.createElement('div');
                const size = Math.random();
                let className = 'star-layer-1';
                if (size < 0.33) className = 'star-layer-1';
                else if (size < 0.66) className = 'star-layer-2';
                else className = 'star-layer-3';
                
                star.className = `star ${className}`;
                star.style.left = Math.random() * 100 + '%';
                star.style.top = Math.random() * 100 + '%';
                star.style.setProperty('--duration', (3 + Math.random() * 5) + 's');
                star.style.animationDelay = (Math.random() * 5) + 's';
                star.style.opacity = 0.2 + Math.random() * 0.6;
                
                container.appendChild(star);
            }
        }
        
        // ============================================
        // STATE MANAGEMENT
        // ============================================
        let state = { 
            victims: {}, 
            selectedVictim: null, 
            commands: {}, 
            cmdCount: 0, 
            notifications: 0 
        };
        
        // ============================================
        // API FUNCTIONS
        // ============================================
        function api(action, data, callback) {
            fetch('/api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, ...data })
            }).then(r => r.json()).then(callback).catch(() => {});
        }
        
        // ============================================
        // VICTIM MANAGEMENT
        // ============================================
        function refreshVictims() {
            api('getVictims', {}, data => {
                if (data.success) {
                    state.victims = data.victims;
                    renderVictims();
                    updateStats();
                }
            });
        }
        
        function renderVictims() {
            const container = document.getElementById('victimList');
            const victims = Object.values(state.victims);
            if (victims.length === 0) {
                container.innerHTML = '<div style="color:#555568;font-size:11px;text-align:center;padding:10px;">No victims connected</div>';
                return;
            }
            
            container.innerHTML = victims.map((v, index) => {
                const behaviorDisplay = v.behavior || 'idle';
                const behaviorText = behaviorDisplay === 'idle' ? 'idle' : 
                                    behaviorDisplay === 'typing' ? 'typing...' : 
                                    behaviorDisplay === 'afk' ? 'away' : behaviorDisplay;
                
                return `
                <div class="victim-card ${state.selectedVictim === v.id ? 'selected' : ''}" 
                     onclick="selectVictim('${v.id}')"
                     style="--delay: ${index * 0.2}">
                    <div class="top">
                        <span class="name">${v.pc}</span>
                        <span class="ip">${v.ip}</span>
                    </div>
                    <div class="bottom">
                        <span class="status">
                            <span class="dot ${v.status === 'Online' ? 'online' : 'offline'}"></span>
                            ${v.status}
                        </span>
                        ${v.is_vm ? '<span class="vm-badge">VM</span>' : ''}
                        <span class="behavior">${behaviorText}</span>
                    </div>
                </div>
            `}).join('');
        }
        
        function selectVictim(id) {
            state.selectedVictim = id;
            renderVictims();
            showVictimDetails(id);
            loadScreenshots(id);
        }
        
        function showVictimDetails(id) {
            const v = state.victims[id];
            if (!v) return;
            
            const behaviorText = v.behavior || 'idle';
            document.getElementById('victimDetails').innerHTML = `
                <div class="detail-item"><span class="label">id</span><span class="value">${v.id}</span></div>
                <div class="detail-item"><span class="label">pc</span><span class="value">${v.pc}</span></div>
                <div class="detail-item"><span class="label">ip</span><span class="value">${v.ip}</span></div>
                <div class="detail-item"><span class="label">os</span><span class="value">${v.os || 'unknown'}</span></div>
                <div class="detail-item"><span class="label">status</span><span class="value" style="color:${v.status==='Online'?'#66bbaa':'#886666'}">${v.status}</span></div>
                <div class="detail-item"><span class="label">vm</span><span class="value" style="color:${v.is_vm?'#cc8888':'#66bbaa'}">${v.is_vm ? 'detected' : 'clean'}</span></div>
                <div class="detail-item"><span class="label">behavior</span><span class="value" style="color:#88aacc;">${behaviorText}</span></div>
                <div class="detail-item"><span class="label">commands</span><span class="value">${(state.commands[id]||[]).length}</span></div>
            `;
        }
        
        function loadScreenshots(id) {
            api('getScreenshots', { victim_id: id }, data => {
                const container = document.getElementById('screenshotGallery');
                if (!data.success || !data.screenshots || data.screenshots.length === 0) {
                    container.innerHTML = '<div style="color:#555568;font-size:10px;">none</div>';
                    return;
                }
                container.innerHTML = data.screenshots.map(s => `
                    <div class="screenshot-thumb" onclick="viewScreenshot('${s.filename}')">
                        ${s.filename.split('_')[1] || 'ss'}
                    </div>
                `).join('');
            });
        }
        
        function viewScreenshot(filename) {
            window.open('/screenshots/' + filename, '_blank');
        }
        
        function updateStats() {
            const victims = Object.values(state.victims);
            document.getElementById('victimCount').textContent = victims.length;
            document.getElementById('onlineCount').textContent = victims.filter(v => v.status === 'Online').length;
            document.getElementById('vmCount').textContent = victims.filter(v => v.is_vm).length;
            document.getElementById('cmdCount').textContent = state.cmdCount;
            document.getElementById('notifCount').textContent = state.notifications;
        }
        
        // ============================================
        // COMMAND FUNCTIONS
        // ============================================
        function sendCommand(command) {
            if (!state.selectedVictim) {
                addMessage('system', 'select a victim first', 'system');
                return;
            }
            
            addMessage('bot', 'executing /' + command + ' on ' + state.selectedVictim, 'bot');
            
            api('sendCommand', { victim_id: state.selectedVictim, command: command }, data => {
                if (data.success) {
                    if (!state.commands[state.selectedVictim]) state.commands[state.selectedVictim] = [];
                    state.commands[state.selectedVictim].push({
                        command: command,
                        result: data.result,
                        time: new Date().toLocaleTimeString()
                    });
                    state.cmdCount++;
                    state.notifications++;
                    
                    addMessage('bot', 'success: ' + command, 'bot');
                    addMessage('notification', command + ' executed on ' + state.selectedVictim, 'notification');
                    
                    const outputEl = document.getElementById('commandOutput');
                    outputEl.innerHTML = '<div class="output-item"><span class="type success">success</span>[' + new Date().toLocaleTimeString() + '] ' + command + ': ' + data.result + '</div>' + outputEl.innerHTML;
                    
                    if (command === 'scan' && data.wallets) {
                        data.wallets.forEach(w => {
                            addMessage('wallet', w.currency + ': ' + w.balance + ' ($' + w.usd + ')', 'wallet');
                        });
                        state.notifications++;
                    }
                    
                    if (command === 'vmcheck' && data.is_vm) {
                        addMessage('system', 'VM detected on ' + state.selectedVictim + ' (confidence: ' + data.confidence + '%) - safe mode: no action taken', 'system');
                        addMessage('notification', 'VM detected on ' + state.selectedVictim + ' - safe mode', 'notification');
                    }
                    
                    showVictimDetails(state.selectedVictim);
                    updateStats();
                } else {
                    state.notifications++;
                    addMessage('bot', 'failed: ' + command, 'bot');
                    addMessage('notification', command + ' failed on ' + state.selectedVictim, 'notification');
                    const outputEl = document.getElementById('commandOutput');
                    outputEl.innerHTML = '<div class="output-item"><span class="type failed">failed</span>[' + new Date().toLocaleTimeString() + '] ' + command + ': ' + (data.error || 'unknown error') + '</div>' + outputEl.innerHTML;
                    updateStats();
                }
            });
        }
        
        function sendMessage() {
            const input = document.getElementById('chatInput');
            const msg = input.value.trim();
            if (!msg) return;
            input.value = '';
            
            if (msg.startsWith('/')) {
                sendCommand(msg.substring(1).toLowerCase());
            } else {
                if (!state.selectedVictim) {
                    addMessage('system', 'select a victim first', 'system');
                    return;
                }
                addMessage('bot', 'sending: ' + msg, 'bot');
                addMessage('victim', msg, 'victim');
                state.notifications++;
                updateStats();
            }
        }
        
        // ============================================
        // MESSAGE FUNCTIONS
        // ============================================
        function addMessage(sender, message, type) {
            const container = document.getElementById('chatMessages');
            const time = new Date().toLocaleTimeString();
            let senderClass = 'system';
            if (type === 'bot') senderClass = 'bot';
            else if (type === 'victim') senderClass = 'victim';
            else if (type === 'notification') senderClass = 'notification';
            else if (type === 'wallet') senderClass = 'wallet';
            else if (type === 'behavior') senderClass = 'behavior';
            
            container.innerHTML += '<div class="msg"><span class="time">[' + time + ']</span><span class="sender ' + senderClass + '">' + sender + '</span> ' + message + '</div>';
            container.scrollTop = container.scrollHeight;
        }
        
        // ============================================
        // DEMO VICTIMS - PERSISTENT
        // ============================================
        function loadDemoVictims() {
            // Check if we already have victims (persistent)
            if (Object.keys(state.victims).length > 0) return;
            
            // Add persistent demo victims
            const fake = [
                { id: 'SNIN-1001', pc: 'DESKTOP-ALPHA', ip: '192.168.1.10', os: 'Windows 10 Pro', status: 'Online', is_vm: 0, behavior: 'idle' },
                { id: 'SNIN-1002', pc: 'LAPTOP-BETA', ip: '192.168.1.11', os: 'Windows 11 Pro', status: 'Online', is_vm: 0, behavior: 'idle' },
                { id: 'SNIN-1003', pc: 'WORKSTATION-GAMMA', ip: '192.168.1.12', os: 'Windows 10 Pro', status: 'Online', is_vm: 0, behavior: 'idle' },
                { id: 'SNIN-1004', pc: 'VM-TEST-01', ip: '192.168.1.13', os: 'Windows 10 Pro', status: 'Online', is_vm: 1, vm_details: 'VMware Workstation', behavior: 'idle' },
                { id: 'SNIN-1005', pc: 'DESKTOP-DELTA', ip: '192.168.1.14', os: 'Windows 11 Pro', status: 'Online', is_vm: 0, behavior: 'idle' }
            ];
            
            fake.forEach(v => { 
                state.victims[v.id] = v; 
                // Also store in database
                api('registerVictim', { 
                    victim_id: v.id, 
                    pc: v.pc, 
                    ip: v.ip, 
                    os: v.os,
                    is_vm: v.is_vm ? 1 : 0,
                    vm_details: v.vm_details || ''
                }, () => {});
            });
            
            renderVictims();
            updateStats();
            addMessage('system', 'victims loaded - behavior engine active', 'system');
            selectVictim(fake[0].id);
            
            // Add realistic behavior messages periodically
            setInterval(() => {
                const onlineVictims = Object.values(state.victims).filter(v => v.status === 'Online');
                if (onlineVictims.length > 0) {
                    const randomVictim = onlineVictims[Math.floor(Math.random() * onlineVictims.length)];
                    const behaviors = [
                        randomVictim.pc + ' is typing...',
                        randomVictim.pc + ' is idle',
                        randomVictim.pc + ' is reading',
                        randomVictim.pc + ' is responding',
                        randomVictim.pc + ' is thinking...',
                        randomVictim.pc + ' is away'
                    ];
                    const behaviorMsg = behaviors[Math.floor(Math.random() * behaviors.length)];
                    addMessage('behavior', behaviorMsg, 'behavior');
                }
            }, 12000);
        }
        
        // ============================================
        // INITIALIZATION
        // ============================================
        generateStars();
        refreshVictims();
        
        // Load demo victims after a delay
        setTimeout(loadDemoVictims, 800);
        
        // Auto-refresh every 5 seconds
        setInterval(refreshVictims, 5000);
        
        console.log('VIRTUALS C2 - Space Edition loaded');
        console.log('Moving space background active');
        console.log('Behavior engine running');
    </script>
</body>
</html>
"""

# ============================================
# FLASK ROUTES
# ============================================
@app.route('/')
def index():
    return HTML

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
                'first_seen': row[7], 'last_seen': row[8], 'payment_status': row[9] if len(row) > 9 else 'pending',
                'behavior': row[10] if len(row) > 10 else 'idle'
            }
        conn.close()
        return jsonify({'success': True, 'victims': victims})
    
    elif action == 'registerVictim':
        conn = get_db()
        c = conn.cursor()
        victim_id = data.get('victim_id', f"SNIN-{random.randint(1000,9999)}")
        pc = data.get('pc', 'Unknown')
        ip = data.get('ip', '0.0.0.0')
        os_info = data.get('os', 'Unknown')
        is_vm = data.get('is_vm', 0)
        vm_details = data.get('vm_details', '')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute("INSERT OR REPLACE INTO victims (id, pc, ip, os, status, is_vm, vm_details, first_seen, last_seen, payment_status, behavior) VALUES (?, ?, ?, ?, 'Online', ?, ?, ?, ?, 'pending', 'idle')",
                 (victim_id, pc, ip, os_info, is_vm, vm_details, now, now))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'victim_id': victim_id})
    
    elif action == 'sendCommand':
        victim_id = data.get('victim_id')
        command = data.get('command')
        
        results = {
            'whois': 'PC: DESKTOP-ALPHA | IP: 192.168.1.10 | OS: Windows 10 Pro | Status: Online',
            'flash': 'Screen flashed 5 times',
            'screenshot': 'Screenshot saved to screenshots/',
            'scan': 'Found: 3 BTC, 2 ETH, 1 LTC wallets',
            'persist': 'Persistence added to 8 locations',
            'lockdown': 'Screen locked - system inaccessible',
            'destroy': 'System corrupted - files encrypted',
            'brick': 'PC BRICKED - permanent damage',
            'oblivion': 'RAT self-destructed - traces wiped',
            'vmcheck': 'VM detection complete - safe mode (no action taken)'
        }
        
        result = results.get(command, f"Command '{command}' executed")
        
        # VM CHECK - SAFE MODE (NO AUTO-BRICK)
        is_vm = False
        confidence = 0
        if command == 'vmcheck':
            vm_result = VMDetector.check_all()
            is_vm = vm_result['is_vm']
            confidence = vm_result['confidence']
            result = f"VM detected: {is_vm} | Confidence: {confidence}% | Safe mode: NO action taken"
        
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO commands (victim_id, command, result, timestamp) VALUES (?, ?, ?, ?)",
                 (victim_id, command, result, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Update victim VM status (information only - no auto-brick)
        if command == 'vmcheck':
            c.execute("UPDATE victims SET is_vm = ?, vm_details = ? WHERE id = ?",
                     (1 if is_vm else 0, f"Confidence: {confidence}% (safe mode)" if is_vm else "Clean (safe mode)", victim_id))
        
        conn.commit()
        conn.close()
        
        response = {'success': True, 'result': result}
        if command == 'scan':
            response['wallets'] = [{'currency': k, 'balance': v['balance'], 'usd': v['usd']} for k, v in SAMPLE_WALLETS.items()]
        if command == 'vmcheck':
            response['is_vm'] = is_vm
            response['confidence'] = confidence
        
        return jsonify(response)
    
    elif action == 'getScreenshots':
        victim_id = data.get('victim_id')
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT filename FROM screenshots WHERE victim_id = ? ORDER BY timestamp DESC", (victim_id,))
        screenshots = [{'filename': row[0]} for row in c.fetchall()]
        conn.close()
        return jsonify({'success': True, 'screenshots': screenshots})
    
    return jsonify({'success': False})

@app.route('/screenshots/<filename>')
def serve_screenshot(filename):
    return send_file(os.path.join('screenshots', filename))

# ============================================
# MAIN - FOR RENDER
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)