"""
OMEGA C2 - COMPLETE GUI OVERHAUL
Brand new design · Different colors · Modern layout
BY: SNIN STAR
"""

from flask import Flask, request, jsonify, send_file, session, redirect, url_for
import sqlite3
import datetime
import hashlib
import json
import os
import random
import zipfile
import time
from io import BytesIO
from functools import wraps

app = Flask(__name__)
app.secret_key = 'omega_c2_secure_key_2024'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False

PORT = int(os.environ.get('PORT', 5000))

# ============================================
# USERS - JUST 2
# ============================================
USERS = {
    "owner": {"password": "omega2024", "role": "owner"},
    "user": {"password": "user2024", "role": "user"}
}

# ============================================
# DATABASE
# ============================================
def init_db():
    if os.path.exists('omega.db'):
        os.remove('omega.db')
    
    conn = sqlite3.connect('omega.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )''')
    
    c.execute('''CREATE TABLE victims (
        id TEXT PRIMARY KEY,
        hostname TEXT,
        ip TEXT,
        os TEXT,
        status TEXT,
        last_seen TEXT,
        country TEXT,
        note TEXT,
        browser_data TEXT
    )''')
    
    c.execute('''CREATE TABLE logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        timestamp TEXT
    )''')
    
    for username, info in USERS.items():
        hashed = hashlib.md5(info['password'].encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 (username, hashed, info['role']))
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    victims = [
        ("PC-ALPHA", "DESKTOP-001", "192.168.1.101", "Windows 11", "Online", now, "US", "", json.dumps({
            "chrome": {"passwords": 247, "cookies": 893, "history": 1245, "bookmarks": 89},
            "edge": {"passwords": 156, "cookies": 512, "history": 789, "bookmarks": 45}
        })),
        ("PC-BETA", "LAPTOP-002", "192.168.1.102", "Windows 10", "Online", now, "UK", "", json.dumps({
            "chrome": {"passwords": 312, "cookies": 1024, "history": 1567, "bookmarks": 112},
            "firefox": {"passwords": 67, "cookies": 189, "history": 345, "bookmarks": 12}
        })),
        ("SRV-GAMMA", "SERVER-003", "192.168.1.103", "Server 2022", "Online", now, "DE", "", json.dumps({
            "chrome": {"passwords": 89, "cookies": 234, "history": 456, "bookmarks": 23}
        })),
        ("PC-DELTA", "GAMING-004", "192.168.1.104", "Windows 11", "Online", now, "CA", "", json.dumps({
            "chrome": {"passwords": 445, "cookies": 1567, "history": 2345, "bookmarks": 156},
            "brave": {"passwords": 89, "cookies": 234, "history": 456, "bookmarks": 23}
        })),
        ("VM-EPSILON", "VM-005", "192.168.1.105", "Windows 10", "Online", now, "US", "VM", json.dumps({
            "chrome": {"passwords": 34, "cookies": 89, "history": 123, "bookmarks": 5}
        })),
        ("PC-ZETA", "WORK-006", "192.168.1.106", "Windows 11", "Online", now, "FR", "", json.dumps({
            "chrome": {"passwords": 567, "cookies": 2034, "history": 3456, "bookmarks": 234},
            "firefox": {"passwords": 234, "cookies": 890, "history": 1567, "bookmarks": 56}
        })),
        ("SRV-ETA", "WEB-007", "192.168.1.107", "Ubuntu", "Online", now, "US", "", json.dumps({
            "chrome": {"passwords": 78, "cookies": 234, "history": 567, "bookmarks": 23}
        }))
    ]
    
    for v in victims:
        c.execute("INSERT INTO victims (id, hostname, ip, os, status, last_seen, country, note, browser_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8]))
    
    conn.commit()
    conn.close()
    print("[+] Omega database initialized")

init_db()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# ============================================
# HTML - LANDING (NEW DESIGN)
# ============================================
LANDING = '''
<!DOCTYPE html>
<html>
<head>
    <title>OMEGA C2</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a1a;color:#c0c0d0;font-family:'Orbitron',sans-serif;height:100vh;display:flex;justify-content:center;align-items:center;overflow:hidden}
        .bg{position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(ellipse at 30% 50%, rgba(0,255,200,0.03) 0%, transparent 70%), radial-gradient(ellipse at 70% 50%, rgba(255,0,200,0.03) 0%, transparent 70%);z-index:0}
        .container{text-align:center;z-index:1;animation:fadeIn 1.5s ease}
        @keyframes fadeIn{0%{opacity:0;transform:scale(0.9)}100%{opacity:1;transform:scale(1)}}
        .glitch{font-size:90px;font-weight:900;letter-spacing:25px;background:linear-gradient(135deg,#00ffc8,#ff00c8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-shadow:0 0 60px rgba(0,255,200,0.1)}
        .sub{color:#333;font-size:12px;letter-spacing:10px;margin-top:15px;border-top:1px solid rgba(255,255,255,0.03);padding-top:15px}
        .sub .dot{color:#00ffc8;display:inline-block;animation:pulse 1.5s infinite}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.2}}
        .login-btn{position:fixed;bottom:40px;right:40px;width:60px;height:60px;border-radius:50%;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);display:flex;justify-content:center;align-items:center;font-size:28px;color:#333;text-decoration:none;transition:0.5s;z-index:10;backdrop-filter:blur(10px)}
        .login-btn:hover{background:rgba(0,255,200,0.05);border-color:rgba(0,255,200,0.1);color:#00ffc8;transform:scale(1.1);box-shadow:0 0 40px rgba(0,255,200,0.05)}
        .status{color:#1a1a2a;font-size:9px;letter-spacing:4px;margin-top:20px}
        .status span{color:#00ffc8}
    </style>
</head>
<body>
    <div class="bg"></div>
    <div class="container">
        <div class="glitch">◈ OMEGA</div>
        <div class="sub"><span class="dot">●</span> COMMAND &amp; CONTROL</div>
        <div class="status">● <span>7</span> agents online</div>
    </div>
    <a href="/login" class="login-btn">⌘</a>
</body>
</html>
'''

# ============================================
# HTML - LOGIN (NEW DESIGN)
# ============================================
LOGIN = '''
<!DOCTYPE html>
<html>
<head>
    <title>OMEGA C2 - Login</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a1a;color:#c0c0d0;font-family:'Orbitron',sans-serif;height:100vh;display:flex;justify-content:center;align-items:center}
        .bg{position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(ellipse at 30% 50%, rgba(0,255,200,0.03) 0%, transparent 70%), radial-gradient(ellipse at 70% 50%, rgba(255,0,200,0.03) 0%, transparent 70%);z-index:0}
        .box{background:rgba(10,10,30,0.95);border:1px solid rgba(255,255,255,0.03);border-radius:20px;padding:50px 45px;width:400px;max-width:92%;z-index:1;backdrop-filter:blur(20px);box-shadow:0 40px 80px rgba(0,0,0,0.6)}
        h1{font-size:30px;font-weight:900;text-align:center;letter-spacing:8px;background:linear-gradient(135deg,#00ffc8,#ff00c8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .sub{color:#333;text-align:center;font-size:10px;margin-bottom:35px;letter-spacing:6px;border-bottom:1px solid rgba(255,255,255,0.02);padding-bottom:15px}
        .sub .dot{color:#00ffc8}
        label{color:#444;font-size:9px;display:block;margin-bottom:6px;letter-spacing:3px;text-transform:uppercase}
        input{width:100%;padding:14px 18px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:10px;color:#c0c0d0;font-size:14px;outline:none;margin-bottom:18px;transition:0.3s;font-family:'Orbitron',sans-serif}
        input:focus{border-color:rgba(0,255,200,0.1);background:rgba(255,255,255,0.03);box-shadow:0 0 30px rgba(0,255,200,0.02)}
        input::placeholder{color:#1a1a2a}
        button{width:100%;padding:14px;background:linear-gradient(135deg,rgba(0,255,200,0.05),rgba(255,0,200,0.05));border:1px solid rgba(0,255,200,0.05);border-radius:10px;color:#00ffc8;font-size:14px;cursor:pointer;transition:0.3s;font-weight:700;letter-spacing:4px;font-family:'Orbitron',sans-serif}
        button:hover{background:linear-gradient(135deg,rgba(0,255,200,0.1),rgba(255,0,200,0.05));box-shadow:0 0 40px rgba(0,255,200,0.05)}
        .error{color:#ff6b6b;text-align:center;margin-top:14px;display:none;font-size:10px;background:rgba(255,107,107,0.03);padding:10px;border-radius:8px;border:1px solid rgba(255,107,107,0.05);letter-spacing:2px}
        .back{text-align:center;margin-top:18px;font-size:9px;color:#1a1a2a}
        .back a{color:#2a2a3a;text-decoration:none;transition:0.3s;letter-spacing:2px}
        .back a:hover{color:#00ffc8}
        .users{color:#1a1a2a;font-size:8px;margin-top:15px;border-top:1px solid rgba(255,255,255,0.01);padding-top:15px;text-align:center;letter-spacing:3px}
        .users .owner{color:#ffd93d}
        .users .user{color:#00ffc8}
    </style>
</head>
<body>
    <div class="bg"></div>
    <div class="box">
        <h1>◈ OMEGA</h1>
        <div class="sub"><span class="dot">●</span> AUTHENTICATE</div>
        <form onsubmit="login(event)">
            <label>Username</label>
            <input type="text" id="user" placeholder="Enter username" required>
            <label>Password</label>
            <input type="password" id="pass" placeholder="Enter password" required>
            <button type="submit">ACCESS</button>
            <div class="error" id="err">⛔ Invalid credentials</div>
        </form>
        <div class="back"><a href="/">← BACK</a></div>
        <div class="users"><span class="owner">👑 owner</span> · <span class="user">⚡ user</span></div>
    </div>
    <script>
        function login(e){
            e.preventDefault();
            var u = document.getElementById('user').value;
            var p = document.getElementById('pass').value;
            fetch('/api/login', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({username:u, password:p})
            })
            .then(r=>r.json())
            .then(d=>{
                if(d.success){
                    window.location.href = '/dashboard';
                } else {
                    document.getElementById('err').style.display = 'block';
                }
            })
            .catch(()=>{
                document.getElementById('err').style.display = 'block';
            });
        }
    </script>
</body>
</html>
'''

# ============================================
# HTML - DASHBOARD (COMPLETELY NEW DESIGN)
# ============================================
DASHBOARD = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OMEGA C2</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Fira+Code:wght@300;400;600;700&display=swap');
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#070714;color:#c0c0d0;font-family:'Fira Code',monospace;height:100vh;overflow:hidden}
        ::-webkit-scrollbar{width:2px}
        ::-webkit-scrollbar-thumb{background:rgba(0,255,200,0.1);border-radius:10px}
        ::-webkit-scrollbar-track{background:transparent}
        
        /* HEADER - Cyber */
        .header{background:rgba(7,7,20,0.98);padding:10px 30px;border-bottom:1px solid rgba(0,255,200,0.03);display:flex;justify-content:space-between;align-items:center;height:55px}
        .header .logo{font-family:'Orbitron',sans-serif;font-size:20px;font-weight:900;letter-spacing:8px;background:linear-gradient(135deg,#00ffc8,#ff00c8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .header-right{display:flex;align-items:center;gap:20px}
        .stats{display:flex;gap:20px;font-size:9px;color:#1a1a3a;letter-spacing:2px}
        .stats span{color:#c0c0d0;font-weight:700;font-size:14px;margin-left:5px;font-family:'Orbitron',sans-serif}
        .stats .online{color:#00ffc8}
        .user-info{display:flex;align-items:center;gap:10px;font-size:11px}
        .user-info .name{color:#c0c0d0;font-weight:300}
        .user-info .role{font-size:7px;padding:4px 14px;border-radius:20px;text-transform:uppercase;font-weight:700;letter-spacing:2px;font-family:'Orbitron',sans-serif}
        .user-info .role.owner{background:rgba(255,217,61,0.06);color:#ffd93d;border:1px solid rgba(255,217,61,0.04)}
        .user-info .role.user{background:rgba(0,255,200,0.04);color:#00ffc8;border:1px solid rgba(0,255,200,0.02)}
        .logout{background:rgba(255,107,107,0.02);color:#442222;border:1px solid rgba(255,107,107,0.02);padding:5px 18px;border-radius:20px;cursor:pointer;font-size:8px;transition:0.3s;font-family:'Orbitron',sans-serif;letter-spacing:2px}
        .logout:hover{background:rgba(255,107,107,0.04);color:#ff6b6b;border-color:rgba(255,107,107,0.04)}
        
        /* MAIN */
        .container{display:flex;height:calc(100vh - 55px);padding:8px;gap:8px}
        
        /* LEFT - AGENTS */
        .left{width:180px;min-width:180px;background:rgba(7,7,20,0.9);border:1px solid rgba(255,255,255,0.02);border-radius:12px;padding:8px;display:flex;flex-direction:column}
        .left .title{color:#1a1a3a;font-size:7px;text-transform:uppercase;letter-spacing:4px;padding:8px 10px 6px;border-bottom:1px solid rgba(255,255,255,0.01);font-family:'Orbitron',sans-serif}
        .victims{flex:1;overflow-y:auto;padding:4px}
        .victim{padding:6px 10px;margin:2px 0;border-radius:6px;cursor:pointer;border-left:2px solid transparent;font-size:10px;display:flex;align-items:center;gap:8px;transition:0.15s}
        .victim:hover{background:rgba(255,255,255,0.01)}
        .victim.active{background:rgba(0,255,200,0.02);border-left-color:#00ffc8}
        .victim .dot{width:5px;height:5px;border-radius:50%;display:inline-block}
        .victim .dot.online{background:#00ffc8;box-shadow:0 0 10px rgba(0,255,200,0.15)}
        .victim .dot.offline{background:#221111}
        .victim .name{color:#c0c0d0;flex:1;font-size:10px}
        .victim .badge{font-size:5px;padding:0 6px;border-radius:10px;background:rgba(255,107,107,0.04);color:#442222;font-family:'Orbitron',sans-serif}
        .victim .act{color:#1a1a3a;font-size:7px}
        
        /* MIDDLE - TERMINAL */
        .middle{flex:1;display:flex;flex-direction:column;gap:8px}
        .terminal{background:rgba(7,7,20,0.9);border:1px solid rgba(255,255,255,0.02);border-radius:12px;padding:10px 14px;flex:1;display:flex;flex-direction:column}
        .terminal .title{color:#1a1a3a;font-size:7px;text-transform:uppercase;letter-spacing:4px;border-bottom:1px solid rgba(255,255,255,0.01);padding-bottom:8px;display:flex;justify-content:space-between;font-family:'Orbitron',sans-serif}
        .terminal .title .target{color:#00ffc8;font-weight:700;font-size:8px;letter-spacing:2px}
        .msgs{background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.005);border-radius:8px;padding:8px 12px;flex:1;overflow-y:auto;font-size:11px;line-height:2;min-height:100px;max-height:160px}
        .msgs .msg{padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.003)}
        .msgs .time{color:#111122;font-size:7px;margin-right:8px}
        .msgs .sender{font-weight:600;font-size:10px}
        .msgs .sender.user{color:#00ffc8}
        .msgs .sender.system{color:#333}
        .msgs .sender.victim{color:#ffd93d}
        .msgs .sender.cmd{color:#ff6b6b}
        .input-area{display:flex;gap:6px;margin-top:8px}
        .input-area input{flex:1;padding:8px 16px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.01);border-radius:8px;color:#c0c0d0;font-size:11px;outline:none;font-family:'Fira Code',monospace;transition:0.2s}
        .input-area input:focus{border-color:rgba(0,255,200,0.03);background:rgba(0,0,0,0.3)}
        .input-area input::placeholder{color:#111122}
        .input-area button{padding:8px 22px;background:rgba(0,255,200,0.02);color:#00ffc8;border:1px solid rgba(0,255,200,0.02);border-radius:8px;cursor:pointer;font-size:10px;transition:0.2s;font-family:'Orbitron',sans-serif;letter-spacing:2px}
        .input-area button:hover{background:rgba(0,255,200,0.04);color:#00ffc8}
        .cmds{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
        .cmds span{padding:3px 12px;background:rgba(255,255,255,0.005);border:1px solid rgba(255,255,255,0.005);border-radius:6px;font-size:8px;color:#1a1a3a;cursor:pointer;transition:0.2s;font-family:'Orbitron',sans-serif;letter-spacing:1px}
        .cmds span:hover{background:rgba(0,255,200,0.02);color:#00ffc8;border-color:rgba(0,255,200,0.02)}
        .actions{display:flex;gap:6px;margin-top:6px;flex-wrap:wrap}
        .actions button{padding:4px 16px;background:rgba(255,217,61,0.01);color:#444;border:1px solid rgba(255,217,61,0.01);border-radius:6px;cursor:pointer;font-size:8px;font-family:'Orbitron',sans-serif;letter-spacing:2px;transition:0.2s}
        .actions button:hover{background:rgba(255,217,61,0.02);color:#ffd93d}
        .actions .zip{background:rgba(0,255,200,0.01);color:#333;border:1px solid rgba(0,255,200,0.01)}
        .actions .zip:hover{background:rgba(0,255,200,0.02);color:#00ffc8}
        
        /* RIGHT - DETAILS + LOGS */
        .right{width:230px;min-width:190px;display:flex;flex-direction:column;gap:8px}
        .details{background:rgba(7,7,20,0.9);border:1px solid rgba(255,255,255,0.02);border-radius:12px;padding:10px 14px;height:45%;overflow-y:auto}
        .details .title{color:#1a1a3a;font-size:7px;text-transform:uppercase;letter-spacing:4px;border-bottom:1px solid rgba(255,255,255,0.01);padding-bottom:6px;margin-bottom:6px;font-family:'Orbitron',sans-serif}
        .detail-item{padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.003);font-size:9px;display:flex;justify-content:space-between}
        .detail-item .label{color:#1a1a3a;font-size:8px}
        .detail-item .value{color:#c0c0d0;font-size:9px}
        .logs{background:rgba(7,7,20,0.9);border:1px solid rgba(255,255,255,0.02);border-radius:12px;padding:10px 14px;flex:1;overflow-y:auto}
        .logs .title{color:#1a1a3a;font-size:7px;text-transform:uppercase;letter-spacing:4px;border-bottom:1px solid rgba(255,255,255,0.01);padding-bottom:6px;margin-bottom:6px;font-family:'Orbitron',sans-serif}
        .log-item{font-size:7px;padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.003);display:flex;gap:6px;align-items:center}
        .log-item .time{color:#111122}
        .log-item .user{color:#00ffc8;font-size:7px}
        .log-item .action{color:#444}
        .log-item .type{font-size:4px;padding:0 6px;border-radius:10px;text-transform:uppercase;letter-spacing:1px}
        .log-item .type.cmd{background:rgba(255,107,107,0.03);color:#ff6b6b}
        .log-item .type.msg{background:rgba(0,255,200,0.02);color:#00ffc8}
        .log-item .type.sys{background:rgba(255,255,255,0.005);color:#1a1a3a}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">◈ OMEGA</div>
        <div class="header-right">
            <div class="stats">
                <span>AGENTS <span id="vicCount">0</span></span>
                <span class="online">ONLINE <span id="onCount">0</span></span>
            </div>
            <div class="user-info">
                <span class="name" id="userName">Loading...</span>
                <span class="role" id="userRole">user</span>
            </div>
            <button class="logout" onclick="logout()">LOGOUT</button>
        </div>
    </div>
    
    <div class="container">
        <div class="left">
            <div class="title">AGENTS</div>
            <div class="victims" id="victimList"><div style="color:#111122;font-size:9px;text-align:center;padding:20px;">scanning...</div></div>
        </div>
        
        <div class="middle">
            <div class="terminal">
                <div class="title">TERMINAL <span class="target" id="curTarget">#general</span></div>
                <div class="msgs" id="msgBox"><div class="msg"><span class="time">[system]</span><span class="sender system">omega</span> ready</div></div>
                <div class="input-area">
                    <input id="cmdInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendCmd()">
                    <button onclick="sendCmd()">EXEC</button>
                </div>
                <div class="cmds">
                    <span onclick="runCmd('whois')">whois</span>
                    <span onclick="runCmd('scan')">scan</span>
                    <span onclick="runCmd('status')">status</span>
                    <span onclick="runCmd('steal')">steal</span>
                    <span onclick="runCmd('screenshot')">ss</span>
                    <span onclick="runCmd('destroy')">destroy</span>
                    <span onclick="runCmd('persist')">persist</span>
                    <span onclick="runCmd('flash')">flash</span>
                    <span onclick="runCmd('vmcheck')">vm</span>
                </div>
                <div class="actions">
                    <button onclick="window.open('/download-rat','_blank')">⬇ RAT</button>
                    <button class="zip" onclick="getZip()">📦 DATA</button>
                </div>
            </div>
        </div>
        
        <div class="right">
            <div class="details">
                <div class="title">DETAILS</div>
                <div id="detailBox"><div style="color:#111122;font-size:9px;padding:15px;text-align:center;">select agent</div></div>
            </div>
            <div class="logs">
                <div class="title">ACTIVITY</div>
                <div id="logBox"><div style="color:#111122;font-size:7px;padding:8px;">awaiting activity</div></div>
            </div>
        </div>
    </div>
    
    <script>
        var state = {victims: {}, active: null, currentUser: '', userRole: ''};
        
        function getUser(){
            fetch('/api/user')
            .then(r => r.json())
            .then(d => {
                if(d.success){
                    state.currentUser = d.username;
                    state.userRole = d.role;
                    document.getElementById('userName').textContent = d.username;
                    var roleEl = document.getElementById('userRole');
                    roleEl.textContent = d.role.toUpperCase();
                    roleEl.className = 'role ' + d.role;
                    document.title = 'OMEGA C2 - ' + d.username;
                } else {
                    window.location.href = '/login';
                }
            })
            .catch(() => {
                window.location.href = '/login';
            });
        }
        
        function logout(){
            fetch('/api/logout',{method:'POST'}).then(()=>window.location.href='/login');
        }
        
        function api(action, data, cb){
            fetch('/api', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({action:action, ...data})
            }).then(r=>r.json()).then(cb).catch(()=>{});
        }
        
        function refresh(){
            api('getVictims', {}, function(d){
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
            if(!victims || victims.length === 0){
                el.innerHTML = '<div style="color:#111122;font-size:9px;text-align:center;padding:20px;">no agents</div>';
                return;
            }
            var html = '';
            for(var i = 0; i < victims.length; i++){
                var v = victims[i];
                var active = (state.active === v.id) ? 'active' : '';
                var status = (v.status === 'Online') ? 'online' : 'offline';
                var badge = v.note && v.note.includes('VM') ? '<span class="badge">VM</span>' : '';
                html += '<div class="victim '+active+'" onclick="selectVictim(\''+v.id+'\')">'+
                    '<span class="dot '+status+'"></span>'+
                    '<span class="name">'+v.id+'</span>'+
                    badge+
                    '<span class="act">'+(v.activity||'idle')+'</span>'+
                    '</div>';
            }
            el.innerHTML = html;
        }
        
        function selectVictim(id){
            state.active = id;
            document.getElementById('curTarget').textContent = '#' + id;
            renderVictims();
            showDetails(id);
        }
        
        function showDetails(id){
            var v = state.victims[id];
            if(!v) return;
            document.getElementById('detailBox').innerHTML =
                '<div class="detail-item"><span class="label">ID</span><span class="value">'+v.id+'</span></div>'+
                '<div class="detail-item"><span class="label">HOST</span><span class="value">'+v.hostname+'</span></div>'+
                '<div class="detail-item"><span class="label">IP</span><span class="value">'+v.ip+'</span></div>'+
                '<div class="detail-item"><span class="label">OS</span><span class="value">'+v.os+'</span></div>'+
                '<div class="detail-item"><span class="label">STATUS</span><span class="value" style="color:'+(v.status==='Online'?'#00ffc8':'#442222')+'">'+v.status+'</span></div>'+
                '<div class="detail-item"><span class="label">COUNTRY</span><span class="value">'+v.country+'</span></div>';
        }
        
        function updateStats(){
            var victims = Object.values(state.victims);
            document.getElementById('vicCount').textContent = victims.length;
            var online = 0;
            for(var i = 0; i < victims.length; i++){
                if(victims[i].status === 'Online') online++;
            }
            document.getElementById('onCount').textContent = online;
        }
        
        function addLog(action, type){
            var el = document.getElementById('logBox');
            var time = new Date().toLocaleTimeString();
            var user = state.currentUser || 'system';
            el.innerHTML = '<div class="log-item"><span class="time">['+time+']</span><span class="user">'+user+'</span><span class="type '+type+'">'+type+'</span><span class="action">'+action+'</span></div>' + el.innerHTML;
        }
        
        function addMsg(sender, msg, type){
            var el = document.getElementById('msgBox');
            var t = new Date().toLocaleTimeString();
            var cls = 'system';
            if(type === 'cmd') cls = 'cmd';
            else if(type === 'victim') cls = 'victim';
            else if(type === 'user') cls = 'user';
            el.innerHTML += '<div class="msg"><span class="time">['+t+']</span><span class="sender '+cls+'">'+sender+'</span> '+msg+'</div>';
            el.scrollTop = el.scrollHeight;
        }
        
        function runCmd(cmd){
            var victim = state.active;
            if(!victim){
                addMsg('system', 'No agent selected', 'system');
                addLog('No agent selected', 'sys');
                return;
            }
            addMsg('cmd', '/'+cmd+' → '+victim, 'cmd');
            addLog('Executing '+cmd+' on '+victim, 'cmd');
            api('sendCommand', {victim_id: victim, command: cmd}, function(d){
                if(d.success){
                    addMsg('cmd', '✅ success', 'cmd');
                    addLog('Command '+cmd+' completed', 'cmd');
                    if(d.result){
                        addMsg('victim', '➤ '+d.result, 'victim');
                    }
                } else {
                    addMsg('cmd', '❌ failed', 'cmd');
                    addLog('Command '+cmd+' failed', 'cmd');
                }
            });
        }
        
        function sendCmd(){
            var input = document.getElementById('cmdInput');
            var msg = input.value.trim();
            if(!msg) return;
            input.value = '';
            var victim = state.active;
            if(msg.charAt(0) === '/'){
                runCmd(msg.substring(1).toLowerCase());
            } else {
                if(!victim){
                    addMsg('system', 'No agent selected', 'system');
                    return;
                }
                addMsg('user', msg, 'user');
                addMsg('victim', msg, 'victim');
                addLog('Message: "'+msg+'" to '+victim, 'msg');
            }
        }
        
        function getZip(){
            var victim = state.active || 'all';
            addMsg('system', '📦 Generating full data for '+victim+'...', 'system');
            window.open('/download-full-data?victim='+victim, '_blank');
            addMsg('system', '✅ Download started!', 'system');
        }
        
        setInterval(refresh, 3000);
        refresh();
        getUser();
    </script>
</body>
</html>
'''

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return LANDING

@app.route('/login')
def login_page():
    return LOGIN

@app.route('/dashboard')
@login_required
def dashboard():
    return DASHBOARD

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').lower()
    password = data.get('password', '')
    
    conn = sqlite3.connect('omega.db')
    c = conn.cursor()
    c.execute("SELECT id, password, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if row and row[1] == hashlib.md5(password.encode()).hexdigest():
        session.clear()
        session['user_id'] = row[0]
        session['username'] = username
        session['role'] = row[2]
        session['logged_in'] = True
        return jsonify({'success': True, 'role': row[2], 'username': username})
    
    return jsonify({'success': False})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/user')
@login_required
def api_user():
    return jsonify({
        'success': True,
        'username': session.get('username', 'unknown'),
        'role': session.get('role', 'user')
    })

@app.route('/api', methods=['POST'])
@login_required
def api_handler():
    data = request.get_json()
    action = data.get('action')
    
    if action == 'getVictims':
        conn = sqlite3.connect('omega.db')
        c = conn.cursor()
        c.execute("SELECT id, hostname, ip, os, status, country, note FROM victims")
        victims = {}
        for row in c.fetchall():
            victims[row[0]] = {
                'id': row[0],
                'hostname': row[1],
                'ip': row[2],
                'os': row[3],
                'status': row[4],
                'country': row[5],
                'note': row[6] or '',
                'activity': 'idle'
            }
        conn.close()
        return jsonify({'success': True, 'victims': victims})
    
    elif action == 'sendCommand':
        victim_id = data.get('victim_id')
        command = data.get('command')
        
        results = {
            'whois': '🖥️ Host: DESKTOP-001 | IP: 192.168.1.101 | OS: Windows 11',
            'scan': '🔍 Found 5 crypto wallets | Total: $578,124.50',
            'status': '✅ Victim Online | Uptime: 3h 22m',
            'steal': '🕵️ Browser data stolen from 5 browsers',
            'screenshot': '📸 Screenshot captured and saved',
            'destroy': '💀 SYSTEM CORRUPTED - IRREVERSIBLE',
            'persist': '🔒 Persistence installed in 3 locations',
            'flash': '💥 Screen flashed 10 times',
            'vmcheck': '🛡️ VM Detection: Clean system'
        }
        
        result = results.get(command, f"✅ Command '{command}' executed")
        
        conn = sqlite3.connect('omega.db')
        c = conn.cursor()
        c.execute("INSERT INTO logs (username, action, timestamp) VALUES (?, ?, ?)",
                 (session.get('username', 'system'), f"Command: {command} on {victim_id}", 
                  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'result': result})
    
    return jsonify({'success': False})

@app.route('/download-full-data')
@login_required
def download_full_data():
    victim_id = request.args.get('victim', 'all')
    
    conn = sqlite3.connect('omega.db')
    c = conn.cursor()
    
    if victim_id == 'all':
        c.execute("SELECT id, hostname, ip, os, country, browser_data FROM victims")
        victims_data = c.fetchall()
    else:
        c.execute("SELECT id, hostname, ip, os, country, browser_data FROM victims WHERE id = ?", (victim_id,))
        victims_data = c.fetchall()
    conn.close()
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for row in victims_data:
            vid = row[0]
            hostname = row[1]
            ip = row[2]
            os = row[3]
            country = row[4]
            browser_data = json.loads(row[5]) if row[5] else {}
            
            summary = f"""OMEGA DATA EXTRACTION
=========================================
Victim: {vid}
Hostname: {hostname}
IP: {ip}
OS: {os}
Country: {country}
Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
=========================================

BROWSER DATA:
"""
            for browser, data in browser_data.items():
                summary += f"""
[{browser.upper()}]
  Passwords: {data.get('passwords', 0)}
  Cookies: {data.get('cookies', 0)}
  History: {data.get('history', 0)}
  Bookmarks: {data.get('bookmarks', 0)}
"""
                content = f"{browser.upper()} DATA\\n"
                content += "=" * 30 + "\\n"
                for i in range(min(data.get('passwords', 0), 10)):
                    content += f"  site{i+1}.com - user{i+1}@email.com - Pass123!{i+1}\\n"
                zf.writestr(f'{vid}/{browser}_data.txt', content)
            
            zf.writestr(f'{vid}/summary.txt', summary)
    
    zip_buffer.seek(0)
    return send_file(
        zip_buffer, 
        as_attachment=True, 
        download_name=f'OMEGA_DATA_{victim_id}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    )

@app.route('/download-rat')
@login_required
def download_rat():
    return "⚡ OMEGA RAT Builder available. Contact SNIN Star.", 200

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   OMEGA C2 - COMPLETE GUI OVERHAUL                         ║
    ║   Brand new design · Different colors · Modern layout      ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║   USERS:                                                    ║
    ║   👑 owner : omega2024                                     ║
    ║   ⚡ user  : user2024                                      ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║   NEW CYBERPUNK DESIGN                                      ║
    ║   Neon cyan + pink gradient                                ║
    ║   Glitch effects                                          ║
    ║   Clean terminal interface                                 ║
    ║   7 agents with browser data                                ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"[*] Server: http://localhost:{PORT}")
    print(f"[*] Login: http://localhost:{PORT}/login")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)