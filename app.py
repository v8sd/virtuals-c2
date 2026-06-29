"""
OMEGA C2 - COMPLETE REDESIGN
Brand new layout · Different colors · Unique style
BY: SNIN STAR
"""

from flask import Flask, request, jsonify, send_file, session, redirect, url_for
import sqlite3
import datetime
import hashlib
import json
import os
import zipfile
import time
from io import BytesIO
from functools import wraps

app = Flask(__name__)
app.secret_key = 'omega_c2_secure_key_2024'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False

PORT = int(os.environ.get('PORT', 5000))

USERS = {
    "owner": {"password": "omega2024", "role": "owner"},
    "user": {"password": "user2024", "role": "user"}
}

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
        ("PC-ALPHA", "DESKTOP-001", "192.168.1.101", "Windows 11", "Online", now, "US", "", "{}"),
        ("PC-BETA", "LAPTOP-002", "192.168.1.102", "Windows 10", "Online", now, "UK", "", "{}"),
        ("SRV-GAMMA", "SERVER-003", "192.168.1.103", "Server 2022", "Online", now, "DE", "", "{}"),
        ("PC-DELTA", "GAMING-004", "192.168.1.104", "Windows 11", "Online", now, "CA", "", "{}"),
        ("VM-EPSILON", "VM-005", "192.168.1.105", "Windows 10", "Online", now, "US", "VM", "{}"),
        ("PC-ZETA", "WORK-006", "192.168.1.106", "Windows 11", "Online", now, "FR", "", "{}"),
        ("SRV-ETA", "WEB-007", "192.168.1.107", "Ubuntu", "Online", now, "US", "", "{}")
    ]
    
    for v in victims:
        c.execute("INSERT INTO victims (id, hostname, ip, os, status, last_seen, country, note, browser_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8]))
    
    conn.commit()
    conn.close()
    print("[+] Database initialized")

init_db()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# ============================================
# LANDING - NEW
# ============================================
LANDING = '''
<!DOCTYPE html>
<html>
<head>
    <title>OMEGA C2</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0d0d1a;color:#c0c0d0;font-family:'Segoe UI',sans-serif;height:100vh;display:flex;justify-content:center;align-items:center}
        .container{text-align:center}
        h1{font-size:80px;font-weight:900;letter-spacing:20px;background:linear-gradient(135deg,#ff6b35,#ffd700,#ff6b35);background-size:300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shine 4s linear infinite}
        @keyframes shine{0%{background-position:0%}100%{background-position:300%}}
        .sub{color:#444;font-size:14px;letter-spacing:5px;margin-top:10px}
        .sub .dot{color:#ff6b35}
        .login-btn{position:fixed;bottom:30px;right:30px;width:50px;height:50px;border-radius:50%;background:rgba(255,107,53,0.05);border:1px solid rgba(255,107,53,0.05);display:flex;justify-content:center;align-items:center;font-size:24px;color:#333;text-decoration:none;transition:0.3s}
        .login-btn:hover{background:rgba(255,107,53,0.1);border-color:rgba(255,107,53,0.1);color:#ff6b35}
    </style>
</head>
<body>
    <div class="container">
        <h1>◈ OMEGA</h1>
        <div class="sub"><span class="dot">●</span> COMMAND &amp; CONTROL</div>
    </div>
    <a href="/login" class="login-btn">⌘</a>
</body>
</html>
'''

# ============================================
# LOGIN - NEW
# ============================================
LOGIN = '''
<!DOCTYPE html>
<html>
<head>
    <title>OMEGA C2 - Login</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0d0d1a;color:#c0c0d0;font-family:'Segoe UI',sans-serif;height:100vh;display:flex;justify-content:center;align-items:center}
        .box{background:rgba(13,13,26,0.95);border:1px solid rgba(255,107,53,0.05);border-radius:16px;padding:45px;width:380px;max-width:92%}
        h1{font-size:28px;font-weight:900;text-align:center;letter-spacing:10px;background:linear-gradient(135deg,#ff6b35,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .sub{color:#333;text-align:center;font-size:11px;margin-bottom:30px;letter-spacing:4px;border-bottom:1px solid rgba(255,107,53,0.03);padding-bottom:15px}
        .sub .dot{color:#ff6b35}
        label{color:#444;font-size:10px;display:block;margin-bottom:5px;letter-spacing:2px;text-transform:uppercase}
        input{width:100%;padding:14px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,107,53,0.03);border-radius:8px;color:#c0c0d0;font-size:14px;outline:none;margin-bottom:15px;transition:0.3s}
        input:focus{border-color:rgba(255,107,53,0.08)}
        input::placeholder{color:#1a1a2a}
        button{width:100%;padding:14px;background:rgba(255,107,53,0.04);border:1px solid rgba(255,107,53,0.04);border-radius:8px;color:#ff6b35;font-size:15px;cursor:pointer;transition:0.3s;font-weight:700;letter-spacing:4px}
        button:hover{background:rgba(255,107,53,0.08)}
        .error{color:#ff6b6b;text-align:center;margin-top:12px;display:none;font-size:12px}
        .back{text-align:center;margin-top:15px;font-size:10px;color:#1a1a2a}
        .back a{color:#2a2a3a;text-decoration:none}
        .back a:hover{color:#ff6b35}
        .users{color:#1a1a2a;font-size:9px;margin-top:15px;border-top:1px solid rgba(255,107,53,0.02);padding-top:15px;text-align:center;letter-spacing:2px}
        .users .owner{color:#ffd700}
        .users .user{color:#ff6b35}
    </style>
</head>
<body>
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
# DASHBOARD - COMPLETELY NEW DESIGN
# ============================================
DASHBOARD = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OMEGA C2</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0d0d1a;color:#c0c0d0;font-family:'Segoe UI',sans-serif;height:100vh;overflow:hidden}
        ::-webkit-scrollbar{width:3px}
        ::-webkit-scrollbar-thumb{background:rgba(255,107,53,0.1)}
        ::-webkit-scrollbar-track{background:transparent}
        
        .topbar{background:rgba(13,13,26,0.98);padding:10px 30px;border-bottom:2px solid rgba(255,107,53,0.04);display:flex;justify-content:space-between;align-items:center;height:52px}
        .topbar .brand{font-size:20px;font-weight:900;letter-spacing:10px;background:linear-gradient(135deg,#ff6b35,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .topbar-right{display:flex;align-items:center;gap:20px}
        .topbar .counts{display:flex;gap:18px;font-size:10px;color:#1a1a3a}
        .topbar .counts span{color:#c0c0d0;font-weight:700;font-size:14px;margin-left:4px}
        .topbar .counts .green{color:#ffd700}
        .topbar .user{display:flex;align-items:center;gap:10px;font-size:12px}
        .topbar .user .name{color:#c0c0d0}
        .topbar .user .tag{font-size:7px;padding:3px 14px;border-radius:20px;text-transform:uppercase;font-weight:700;letter-spacing:2px}
        .topbar .user .tag.owner{background:rgba(255,215,0,0.05);color:#ffd700;border:1px solid rgba(255,215,0,0.03)}
        .topbar .user .tag.user{background:rgba(255,107,53,0.03);color:#ff6b35;border:1px solid rgba(255,107,53,0.02)}
        .topbar .logout{background:rgba(255,107,53,0.02);color:#442222;border:1px solid rgba(255,107,53,0.02);padding:4px 16px;border-radius:20px;cursor:pointer;font-size:9px;transition:0.3s;font-weight:600;letter-spacing:1px}
        .topbar .logout:hover{background:rgba(255,107,53,0.04);color:#ff6b35}
        
        .main{display:flex;height:calc(100vh - 52px);padding:8px;gap:8px}
        
        .left{width:130px;min-width:130px;background:rgba(13,13,26,0.9);border:1px solid rgba(255,107,53,0.02);border-radius:10px;padding:6px;display:flex;flex-direction:column}
        .left .head{color:#1a1a3a;font-size:7px;text-transform:uppercase;letter-spacing:4px;padding:8px 10px 6px;border-bottom:1px solid rgba(255,107,53,0.02);font-weight:700}
        .agents{flex:1;overflow-y:auto;padding:4px}
        .agent{padding:6px 10px;margin:2px 0;border-radius:6px;cursor:pointer;border-right:2px solid transparent;font-size:11px;display:flex;align-items:center;gap:8px;transition:0.15s}
        .agent:hover{background:rgba(255,107,53,0.02)}
        .agent.active{background:rgba(255,107,53,0.03);border-right-color:#ff6b35}
        .agent .dot{width:5px;height:5px;border-radius:50%;display:inline-block}
        .agent .dot.online{background:#ffd700;box-shadow:0 0 10px rgba(255,215,0,0.05)}
        .agent .dot.offline{background:#221111}
        .agent .id{color:#c0c0d0;flex:1}
        .agent .vm{font-size:5px;padding:0 5px;border-radius:6px;background:rgba(255,107,53,0.02);color:#442222}
        .agent .stat{color:#1a1a3a;font-size:7px}
        
        .middle{flex:1;display:flex;flex-direction:column;gap:8px}
        .terminal{background:rgba(13,13,26,0.9);border:1px solid rgba(255,107,53,0.02);border-radius:10px;padding:10px 14px;flex:1;display:flex;flex-direction:column}
        .terminal .head{color:#1a1a3a;font-size:7px;text-transform:uppercase;letter-spacing:4px;border-bottom:1px solid rgba(255,107,53,0.02);padding-bottom:8px;display:flex;justify-content:space-between;font-weight:700}
        .terminal .head .target{color:#ffd700;font-weight:700;font-size:8px;letter-spacing:2px}
        .output{background:rgba(0,0,0,0.2);border:1px solid rgba(255,107,53,0.01);border-radius:6px;padding:8px 12px;flex:1;overflow-y:auto;font-size:12px;line-height:2;min-height:100px;max-height:160px;font-family:'Courier New',monospace}
        .output .line{padding:1px 0;border-bottom:1px solid rgba(255,107,53,0.005)}
        .output .time{color:#1a1a2a;font-size:7px;margin-right:8px}
        .output .who{font-weight:600;font-size:10px}
        .output .who.cmd{color:#ff6b35}
        .output .who.user{color:#ffd700}
        .output .who.sys{color:#333}
        .output .who.victim{color:#ff6b35}
        .input{display:flex;gap:6px;margin-top:8px}
        .input input{flex:1;padding:8px 16px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,107,53,0.01);border-radius:6px;color:#c0c0d0;font-size:12px;outline:none;font-family:'Courier New',monospace}
        .input input:focus{border-color:rgba(255,107,53,0.03);background:rgba(0,0,0,0.3)}
        .input input::placeholder{color:#1a1a2a}
        .input button{padding:8px 24px;background:rgba(255,107,53,0.02);color:#ff6b35;border:1px solid rgba(255,107,53,0.02);border-radius:6px;cursor:pointer;font-size:10px;transition:0.2s;font-weight:700;letter-spacing:2px}
        .input button:hover{background:rgba(255,107,53,0.04)}
        .quick{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
        .quick span{padding:2px 12px;background:rgba(255,107,53,0.01);border:1px solid rgba(255,107,53,0.005);border-radius:4px;font-size:8px;color:#333;cursor:pointer;transition:0.2s;font-weight:600;letter-spacing:0.5px}
        .quick span:hover{background:rgba(255,107,53,0.02);color:#ff6b35;border-color:rgba(255,107,53,0.02)}
        .tools{display:flex;gap:6px;margin-top:5px}
        .tools button{padding:3px 16px;background:rgba(255,215,0,0.01);color:#444;border:1px solid rgba(255,215,0,0.01);border-radius:4px;cursor:pointer;font-size:8px;transition:0.2s;font-weight:600;letter-spacing:1px}
        .tools button:hover{background:rgba(255,215,0,0.02);color:#ffd700}
        .tools .dl{background:rgba(255,107,53,0.01);color:#333;border:1px solid rgba(255,107,53,0.01)}
        .tools .dl:hover{background:rgba(255,107,53,0.02);color:#ff6b35}
        
        .right{width:210px;min-width:170px;display:flex;flex-direction:column;gap:8px}
        .info{background:rgba(13,13,26,0.9);border:1px solid rgba(255,107,53,0.02);border-radius:10px;padding:10px 14px;height:45%;overflow-y:auto}
        .info .head{color:#1a1a3a;font-size:7px;text-transform:uppercase;letter-spacing:4px;border-bottom:1px solid rgba(255,107,53,0.02);padding-bottom:6px;margin-bottom:6px;font-weight:700}
        .info-item{padding:4px 0;border-bottom:1px solid rgba(255,107,53,0.005);font-size:10px;display:flex;justify-content:space-between}
        .info-item .l{color:#1a1a3a}
        .info-item .v{color:#c0c0d0}
        .activity{background:rgba(13,13,26,0.9);border:1px solid rgba(255,107,53,0.02);border-radius:10px;padding:10px 14px;flex:1;overflow-y:auto}
        .activity .head{color:#1a1a3a;font-size:7px;text-transform:uppercase;letter-spacing:4px;border-bottom:1px solid rgba(255,107,53,0.02);padding-bottom:6px;margin-bottom:6px;font-weight:700}
        .act-item{font-size:8px;padding:2px 0;border-bottom:1px solid rgba(255,107,53,0.003);display:flex;gap:6px;align-items:center}
        .act-item .t{color:#1a1a2a}
        .act-item .u{color:#ffd700}
        .act-item .a{color:#555}
        .act-item .badge{font-size:4px;padding:0 6px;border-radius:8px;text-transform:uppercase;letter-spacing:0.5px}
        .act-item .badge.cmd{background:rgba(255,107,53,0.02);color:#ff6b35}
        .act-item .badge.msg{background:rgba(255,215,0,0.02);color:#ffd700}
        .act-item .badge.sys{background:rgba(255,255,255,0.005);color:#1a1a3a}
    </style>
</head>
<body>
    <div class="topbar">
        <div class="brand">◈ OMEGA</div>
        <div class="topbar-right">
            <div class="counts">
                <span>AGENTS <span id="vicCount">0</span></span>
                <span class="green">ONLINE <span id="onCount">0</span></span>
            </div>
            <div class="user">
                <span class="name" id="userName">Loading...</span>
                <span class="tag" id="userRole">user</span>
            </div>
            <button class="logout" onclick="logout()">LOGOUT</button>
        </div>
    </div>
    
    <div class="main">
        <div class="left">
            <div class="head">AGENTS</div>
            <div class="agents" id="agentList"><div style="color:#1a1a2a;font-size:9px;text-align:center;padding:20px;">scanning...</div></div>
        </div>
        
        <div class="middle">
            <div class="terminal">
                <div class="head">TERMINAL <span class="target" id="curTarget">#general</span></div>
                <div class="output" id="outputBox">
                    <div class="line"><span class="time">[system]</span><span class="who sys">omega</span> ready</div>
                </div>
                <div class="input">
                    <input id="cmdInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendCmd()">
                    <button onclick="sendCmd()">EXEC</button>
                </div>
                <div class="quick">
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
                <div class="tools">
                    <button onclick="window.open('/download-rat','_blank')">⬇ RAT</button>
                    <button class="dl" onclick="getZip()">📦 DATA</button>
                </div>
            </div>
        </div>
        
        <div class="right">
            <div class="info">
                <div class="head">DETAILS</div>
                <div id="detailBox"><div style="color:#1a1a2a;font-size:9px;padding:14px;text-align:center;">select agent</div></div>
            </div>
            <div class="activity">
                <div class="head">ACTIVITY</div>
                <div id="logBox"><div style="color:#1a1a2a;font-size:7px;padding:8px;">awaiting activity</div></div>
            </div>
        </div>
    </div>
    
    <script>
        var state = {agents: {}, active: null, currentUser: '', userRole: ''};
        
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
                    roleEl.className = 'tag ' + d.role;
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
                    state.agents = d.victims;
                    renderAgents();
                    updateStats();
                }
            });
        }
        
        function renderAgents(){
            var el = document.getElementById('agentList');
            var agents = Object.values(state.agents);
            if(!agents || agents.length === 0){
                el.innerHTML = '<div style="color:#1a1a2a;font-size:9px;text-align:center;padding:20px;">no agents</div>';
                return;
            }
            var html = '';
            for(var i = 0; i < agents.length; i++){
                var v = agents[i];
                var active = (state.active === v.id) ? 'active' : '';
                var status = (v.status === 'Online') ? 'online' : 'offline';
                var vm = v.note && v.note.includes('VM') ? '<span class="vm">VM</span>' : '';
                html += '<div class="agent '+active+'" onclick="selectAgent(\''+v.id+'\')">'+
                    '<span class="dot '+status+'"></span>'+
                    '<span class="id">'+v.id+'</span>'+
                    vm+
                    '<span class="stat">'+(v.activity||'idle')+'</span>'+
                    '</div>';
            }
            el.innerHTML = html;
        }
        
        function selectAgent(id){
            state.active = id;
            document.getElementById('curTarget').textContent = '#' + id;
            renderAgents();
            showDetails(id);
        }
        
        function showDetails(id){
            var v = state.agents[id];
            if(!v) return;
            document.getElementById('detailBox').innerHTML =
                '<div class="info-item"><span class="l">ID</span><span class="v">'+v.id+'</span></div>'+
                '<div class="info-item"><span class="l">HOST</span><span class="v">'+v.hostname+'</span></div>'+
                '<div class="info-item"><span class="l">IP</span><span class="v">'+v.ip+'</span></div>'+
                '<div class="info-item"><span class="l">OS</span><span class="v">'+v.os+'</span></div>'+
                '<div class="info-item"><span class="l">STATUS</span><span class="v" style="color:'+(v.status==='Online'?'#ffd700':'#442222')+'">'+v.status+'</span></div>'+
                '<div class="info-item"><span class="l">COUNTRY</span><span class="v">'+v.country+'</span></div>';
        }
        
        function updateStats(){
            var agents = Object.values(state.agents);
            document.getElementById('vicCount').textContent = agents.length;
            var online = 0;
            for(var i = 0; i < agents.length; i++){
                if(agents[i].status === 'Online') online++;
            }
            document.getElementById('onCount').textContent = online;
        }
        
        function addLog(action, type){
            var el = document.getElementById('logBox');
            var time = new Date().toLocaleTimeString();
            var user = state.currentUser || 'system';
            el.innerHTML = '<div class="act-item"><span class="t">['+time+']</span><span class="u">'+user+'</span><span class="badge '+type+'">'+type+'</span><span class="a">'+action+'</span></div>' + el.innerHTML;
        }
        
        function addMsg(who, msg, type){
            var el = document.getElementById('outputBox');
            var t = new Date().toLocaleTimeString();
            var cls = 'sys';
            if(type === 'cmd') cls = 'cmd';
            else if(type === 'victim') cls = 'victim';
            else if(type === 'user') cls = 'user';
            el.innerHTML += '<div class="line"><span class="time">['+t+']</span><span class="who '+cls+'">'+who+'</span> '+msg+'</div>';
            el.scrollTop = el.scrollHeight;
        }
        
        function runCmd(cmd){
            var agent = state.active;
            if(!agent){
                addMsg('system', 'No agent selected', 'sys');
                addLog('No agent selected', 'sys');
                return;
            }
            addMsg('cmd', '/'+cmd+' → '+agent, 'cmd');
            addLog('Executing '+cmd+' on '+agent, 'cmd');
            api('sendCommand', {victim_id: agent, command: cmd}, function(d){
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
            var agent = state.active;
            if(msg.charAt(0) === '/'){
                runCmd(msg.substring(1).toLowerCase());
            } else {
                if(!agent){
                    addMsg('sys', 'No agent selected', 'sys');
                    return;
                }
                addMsg('user', msg, 'user');
                addMsg('victim', msg, 'victim');
                addLog('Message: "'+msg+'" to '+agent, 'msg');
            }
        }
        
        function getZip(){
            var agent = state.active || 'all';
            addMsg('sys', '📦 Generating data for '+agent+'...', 'sys');
            window.open('/download-full-data?victim='+agent, '_blank');
            addMsg('sys', '✅ Download started!', 'sys');
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
            'scan': '🔍 Found 5 crypto wallets | Total: $578,124',
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
        c.execute("SELECT id, hostname, ip, os, country FROM victims")
        victims_data = c.fetchall()
    else:
        c.execute("SELECT id, hostname, ip, os, country FROM victims WHERE id = ?", (victim_id,))
        victims_data = c.fetchall()
    conn.close()
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        summary = f"OMEGA DATA EXTRACTION\\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n"
        for row in victims_data:
            summary += f"Victim: {row[0]}\\nHost: {row[1]}\\nIP: {row[2]}\\nOS: {row[3]}\\nCountry: {row[4]}\\n\\n"
        zf.writestr('summary.txt', summary)
    
    zip_buffer.seek(0)
    return send_file(
        zip_buffer, 
        as_attachment=True, 
        download_name=f'OMEGA_DATA_{victim_id}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    )

@app.route('/download-rat')
@login_required
def download_rat():
    return "⚡ OMEGA RAT Builder available.", 200

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   OMEGA C2 - COMPLETE REDESIGN                             ║
    ║   Brand new layout · Different colors · Unique style        ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║   USERS:                                                    ║
    ║   👑 owner : omega2024                                     ║
    ║   ⚡ user  : user2024                                      ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║   ✅ Orange/Gold color scheme                              ║
    ║   ✅ New 3-column layout                                   ║
    ║   ✅ Terminal shows messages                               ║
    ║   ✅ All commands working                                  ║
    ║   ✅ 7 agents pre-loaded                                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"[*] Server: http://localhost:{PORT}")
    print(f"[*] Login: http://localhost:{PORT}/login")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)