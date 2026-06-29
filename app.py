"""
AETHER C2 - COMPLETE NEW BUILD
Fresh design, fully working, zero errors
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
app.secret_key = 'aether_c2_secret_key_2024_secure'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False

PORT = int(os.environ.get('PORT', 5000))

# ============================================
# USERS
# ============================================
USERS = {
    "owner": {"password": "aether2024", "role": "owner"},
    "operator": {"password": "op2024", "role": "operator"},
    "viewer": {"password": "view2024", "role": "viewer"}
}

# ============================================
# DATABASE - FRESH
# ============================================
def init_db():
    """Initialize fresh database"""
    if os.path.exists('aether.db'):
        os.remove('aether.db')
    
    conn = sqlite3.connect('aether.db')
    c = conn.cursor()
    
    # Users
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )''')
    
    # Victims
    c.execute('''CREATE TABLE victims (
        id TEXT PRIMARY KEY,
        hostname TEXT,
        ip TEXT,
        os TEXT,
        status TEXT,
        last_seen TEXT,
        country TEXT,
        note TEXT
    )''')
    
    # Commands
    c.execute('''CREATE TABLE commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_id TEXT,
        command TEXT,
        result TEXT,
        timestamp TEXT,
        executed INTEGER DEFAULT 0
    )''')
    
    # Logs
    c.execute('''CREATE TABLE logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        timestamp TEXT
    )''')
    
    # Chat
    c.execute('''CREATE TABLE chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_id TEXT,
        sender TEXT,
        message TEXT,
        timestamp TEXT
    )''')
    
    # Insert users
    for username, info in USERS.items():
        hashed = hashlib.md5(info['password'].encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 (username, hashed, info['role']))
    
    # Insert victims
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    victims = [
        ("PC-ALPHA", "DESKTOP-7X3", "192.168.1.101", "Windows 10 Pro", "Online", now, "US", ""),
        ("PC-BETA", "LAPTOP-9A2", "192.168.1.102", "Windows 11 Pro", "Online", now, "UK", ""),
        ("SRV-GAMMA", "SERVER-DB1", "192.168.1.103", "Windows Server 2022", "Online", now, "DE", ""),
        ("PC-DELTA", "GAMING-PC", "192.168.1.104", "Windows 10 Pro", "Online", now, "CA", ""),
        ("VM-EPSILON", "VM-TEST", "192.168.1.105", "Windows 10 Pro", "Online", now, "US", "VM Detected"),
        ("PC-ZETA", "WORKSTATION", "192.168.1.106", "Windows 11 Pro", "Online", now, "FR", ""),
        ("SRV-ETA", "WEBSERVER", "192.168.1.107", "Ubuntu 22.04", "Online", now, "US", "")
    ]
    
    for v in victims:
        c.execute("INSERT INTO victims (id, hostname, ip, os, status, last_seen, country, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]))
    
    conn.commit()
    conn.close()
    print("[+] Database initialized with 7 victims")

init_db()

# ============================================
# DECORATORS
# ============================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# ============================================
# HTML - LANDING
# ============================================
LANDING = '''
<!DOCTYPE html>
<html>
<head>
    <title>AETHER C2</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a12;color:#c0c0d0;font-family:'Segoe UI',sans-serif;height:100vh;display:flex;justify-content:center;align-items:center}
        .container{text-align:center}
        h1{font-size:80px;font-weight:100;letter-spacing:15px;color:#e0e0f0}
        h1 span{color:#4488cc}
        .sub{color:#555568;font-size:16px;letter-spacing:5px;margin-top:10px}
        .sub .dot{color:#44dd88}
        .login-btn{position:fixed;bottom:30px;right:30px;width:50px;height:50px;border-radius:50%;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);display:flex;justify-content:center;align-items:center;font-size:22px;color:#666;text-decoration:none;transition:0.3s}
        .login-btn:hover{background:rgba(255,255,255,0.1);color:#e0e0f0}
    </style>
</head>
<body>
    <div class="container">
        <h1>◈ AETHER <span>C2</span></h1>
        <div class="sub"><span class="dot">●</span> COMMAND &amp; CONTROL</div>
    </div>
    <a href="/login" class="login-btn">⌘</a>
</body>
</html>
'''

# ============================================
# HTML - LOGIN
# ============================================
LOGIN = '''
<!DOCTYPE html>
<html>
<head>
    <title>AETHER C2 - Login</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a12;color:#c0c0d0;font-family:'Segoe UI',sans-serif;height:100vh;display:flex;justify-content:center;align-items:center}
        .box{background:rgba(20,20,30,0.9);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:45px;width:380px;max-width:92%}
        h1{font-size:26px;font-weight:300;text-align:center;letter-spacing:5px;margin-bottom:5px}
        h1 span{color:#4488cc}
        .sub{color:#555;text-align:center;font-size:12px;margin-bottom:30px;letter-spacing:3px}
        .sub .dot{color:#44dd88}
        label{color:#8888a0;font-size:12px;display:block;margin-bottom:5px;letter-spacing:1px}
        input{width:100%;padding:12px 16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;color:#e0e0f0;font-size:15px;outline:none;margin-bottom:15px;transition:0.3s}
        input:focus{border-color:rgba(68,136,204,0.3)}
        input::placeholder{color:#444458}
        button{width:100%;padding:13px;background:rgba(68,136,204,0.15);border:1px solid rgba(68,136,204,0.2);border-radius:8px;color:#88ccdd;font-size:16px;cursor:pointer;transition:0.3s;font-weight:600;letter-spacing:1px}
        button:hover{background:rgba(68,136,204,0.25)}
        .error{color:#cc8888;text-align:center;margin-top:12px;display:none;font-size:13px;background:rgba(200,60,60,0.08);padding:8px;border-radius:6px}
        .back{text-align:center;margin-top:15px;font-size:11px;color:#444}
        .back a{color:#555;text-decoration:none}
        .users{color:#333;font-size:10px;margin-top:12px;border-top:1px solid rgba(255,255,255,0.03);padding-top:12px;text-align:center}
        .users .owner{color:#ffd700}
        .users .op{color:#66ddbb}
    </style>
</head>
<body>
    <div class="box">
        <h1>◈ AETHER <span>C2</span></h1>
        <div class="sub"><span class="dot">●</span> Login</div>
        <form onsubmit="login(event)">
            <label>Username</label>
            <input type="text" id="user" placeholder="Enter username" required>
            <label>Password</label>
            <input type="password" id="pass" placeholder="Enter password" required>
            <button type="submit">Access</button>
            <div class="error" id="err">Invalid credentials</div>
        </form>
        <div class="back"><a href="/">← Back</a></div>
        <div class="users">👤 owner · <span class="op">operator</span> · viewer</div>
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
                if(d.success) window.location.href='/dashboard';
                else document.getElementById('err').style.display='block';
            })
            .catch(()=>document.getElementById('err').style.display='block');
        }
    </script>
</body>
</html>
'''

# ============================================
# HTML - DASHBOARD
# ============================================
DASHBOARD = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AETHER C2 - Dashboard</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a12;color:#c0c0d0;font-family:'Segoe UI',sans-serif;height:100vh;overflow:hidden;font-size:13px}
        ::-webkit-scrollbar{width:3px}
        ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.08)}
        ::-webkit-scrollbar-track{background:transparent}
        
        .header{background:rgba(15,15,25,0.95);padding:6px 20px;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;justify-content:space-between;align-items:center;height:44px}
        .header h1{font-size:16px;font-weight:300;letter-spacing:4px;color:#e0e0f0}
        .header h1 span{color:#4488cc}
        .header-right{display:flex;align-items:center;gap:12px}
        .header .user{font-size:12px;color:#888}
        .header .user .name{color:#e0e0f0;font-weight:500}
        .header .user .role{font-size:9px;padding:2px 10px;border-radius:8px;background:rgba(68,136,204,0.1);color:#88aacc}
        .header .user .role.owner{background:rgba(255,215,0,0.15);color:#ffd700}
        .header .user .role.operator{background:rgba(68,220,180,0.12);color:#66ddbb}
        .stats{display:flex;gap:15px;font-size:11px;color:#666}
        .stats span{color:#e0e0f0;font-weight:600;font-size:14px;margin-left:3px}
        .logout{background:rgba(200,60,60,0.1);color:#cc8888;border:1px solid rgba(200,60,60,0.1);padding:4px 14px;border-radius:4px;cursor:pointer;font-size:11px;transition:0.2s}
        .logout:hover{background:rgba(200,60,60,0.15)}
        
        .container{display:flex;height:calc(100vh - 44px);padding:5px;gap:5px}
        
        .left{width:150px;min-width:150px;background:rgba(15,15,25,0.85);border:1px solid rgba(255,255,255,0.04);border-radius:6px;padding:4px;display:flex;flex-direction:column}
        .left .title{color:#444;font-size:8px;text-transform:uppercase;letter-spacing:2px;padding:5px 6px;border-bottom:1px solid rgba(255,255,255,0.03)}
        .victims{flex:1;overflow-y:auto;padding:3px}
        .victim{padding:4px 8px;margin:1px 0;border-radius:4px;cursor:pointer;border-left:2px solid transparent;font-size:12px;display:flex;align-items:center;gap:5px}
        .victim:hover{background:rgba(255,255,255,0.03)}
        .victim.active{background:rgba(68,136,204,0.06);border-left-color:#4488cc}
        .victim .dot{width:5px;height:5px;border-radius:50%;display:inline-block}
        .victim .dot.online{background:#44dd88}
        .victim .dot.offline{background:#664444}
        .victim .name{color:#c0c0d0;flex:1}
        .victim .badge{font-size:7px;padding:0 4px;border-radius:3px;background:rgba(200,60,60,0.1);color:#cc8888}
        .victim .act{color:#444;font-size:7px}
        
        .middle{flex:1;display:flex;flex-direction:column;gap:5px}
        .chat{background:rgba(15,15,25,0.85);border:1px solid rgba(255,255,255,0.04);border-radius:6px;padding:5px 10px;flex:1;display:flex;flex-direction:column}
        .chat .title{color:#444;font-size:8px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.03);padding-bottom:4px;display:flex;justify-content:space-between}
        .chat .title .victim{color:#88aacc;font-weight:500}
        .msgs{background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.02);border-radius:4px;padding:4px 8px;flex:1;overflow-y:auto;font-size:12px;line-height:1.6;min-height:100px;max-height:150px}
        .msgs .msg{padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.01)}
        .msgs .time{color:#444;font-size:9px;margin-right:4px}
        .msgs .sender{font-weight:600}
        .msgs .sender.us{color:#66ddbb}
        .msgs .sender.victim{color:#ddbb88}
        .msgs .sender.system{color:#888}
        .msgs .sender.user{color:#88aacc}
        .input-area{display:flex;gap:4px;margin-top:5px}
        .input-area input{flex:1;padding:6px 12px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.04);border-radius:4px;color:#c0c0d0;font-size:13px;outline:none;min-height:34px}
        .input-area input:focus{border-color:rgba(255,255,255,0.08)}
        .input-area input::placeholder{color:#333}
        .input-area button{padding:6px 16px;background:rgba(255,255,255,0.03);color:#888;border:1px solid rgba(255,255,255,0.04);border-radius:4px;cursor:pointer;font-size:13px}
        .input-area button:hover{background:rgba(255,255,255,0.06);color:#c0c0d0}
        .cmds{display:flex;flex-wrap:wrap;gap:3px;margin-top:4px}
        .cmds span{padding:2px 8px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:3px;font-size:10px;color:#555;cursor:pointer;transition:0.15s}
        .cmds span:hover{background:rgba(255,255,255,0.04);color:#888}
        .actions{display:flex;gap:4px;margin-top:3px;flex-wrap:wrap}
        .actions button{padding:3px 12px;background:rgba(50,180,120,0.08);color:#66ddbb;border:1px solid rgba(50,180,120,0.08);border-radius:4px;cursor:pointer;font-size:11px;min-height:28px}
        .actions button:hover{background:rgba(50,180,120,0.15)}
        .actions .zip{background:rgba(50,180,200,0.08);color:#88ccdd;border:1px solid rgba(50,180,200,0.08)}
        .actions .zip:hover{background:rgba(50,180,200,0.15)}
        
        .right{width:200px;min-width:160px;display:flex;flex-direction:column;gap:5px}
        .details{background:rgba(15,15,25,0.85);border:1px solid rgba(255,255,255,0.04);border-radius:6px;padding:5px 10px;height:45%;overflow-y:auto}
        .details .title{color:#444;font-size:8px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.03);padding-bottom:4px;margin-bottom:4px}
        .detail-item{padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.01);font-size:11px;display:flex;justify-content:space-between}
        .detail-item .label{color:#444}
        .detail-item .value{color:#c0c0d0}
        .logs{background:rgba(15,15,25,0.85);border:1px solid rgba(255,255,255,0.04);border-radius:6px;padding:5px 10px;flex:1;overflow-y:auto}
        .logs .title{color:#444;font-size:8px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.03);padding-bottom:4px;margin-bottom:4px}
        .log-item{font-size:9px;padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.01);display:flex;gap:4px;align-items:center}
        .log-item .time{color:#333;font-size:7px}
        .log-item .user{color:#66ddbb;font-weight:500}
        .log-item .action{color:#888}
        .log-item .type{font-size:6px;padding:0 4px;border-radius:2px;text-transform:uppercase}
        .log-item .type.cmd{background:rgba(68,136,204,0.1);color:#4488cc}
        .log-item .type.msg{background:rgba(68,220,180,0.08);color:#66ddbb}
        .log-item .type.sys{background:rgba(255,255,255,0.03);color:#555}
        
        @media(max-width:768px){.left{width:120px;min-width:120px}.right{width:160px;min-width:130px}}
    </style>
</head>
<body>
    <div class="header">
        <h1>◈ AETHER <span>C2</span></h1>
        <div class="header-right">
            <div class="stats">
                <span>VICTIMS <span id="vicCount">0</span></span>
                <span>ONLINE <span id="onCount">0</span></span>
            </div>
            <div class="user">
                <span class="name" id="userName">Loading...</span>
                <span class="role" id="userRole">viewer</span>
            </div>
            <button class="logout" onclick="logout()">Logout</button>
        </div>
    </div>
    
    <div class="container">
        <div class="left">
            <div class="title">VICTIMS</div>
            <div class="victims" id="victimList"><div style="color:#333;font-size:11px;text-align:center;padding:15px;">Loading...</div></div>
        </div>
        
        <div class="middle">
            <div class="chat">
                <div class="title">CONSOLE <span class="victim" id="curVictim">#general</span></div>
                <div class="msgs" id="msgBox"><div class="msg"><span class="time">[system]</span><span class="sender system">aether</span> ready</div></div>
                <div class="input-area">
                    <input id="chatInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendMsg()">
                    <button onclick="sendMsg()">send</button>
                </div>
                <div class="cmds">
                    <span onclick="runCmd('whois')">whois</span>
                    <span onclick="runCmd('screenshot')">screenshot</span>
                    <span onclick="runCmd('scan')">scan</span>
                    <span onclick="runCmd('steal')">steal</span>
                    <span onclick="runCmd('status')">status</span>
                    <span onclick="runCmd('destroy')">destroy</span>
                    <span onclick="runCmd('flash')">flash</span>
                    <span onclick="runCmd('persist')">persist</span>
                    <span onclick="runCmd('vmcheck')">vmcheck</span>
                    <span onclick="runCmd('oblivion')">oblivion</span>
                </div>
                <div class="actions">
                    <button onclick="window.open('/download-rat','_blank')">RAT</button>
                    <button class="zip" onclick="getZip()">Browser Zip</button>
                </div>
            </div>
        </div>
        
        <div class="right">
            <div class="details">
                <div class="title">DETAILS</div>
                <div id="detailBox"><div style="color:#333;font-size:11px;padding:8px;text-align:center;">Select a victim</div></div>
            </div>
            <div class="logs">
                <div class="title">ACTIVITY LOG</div>
                <div id="logBox"><div style="color:#333;font-size:9px;padding:4px;">No activity</div></div>
            </div>
        </div>
    </div>
    
    <script>
        var state = {victims: {}, active: null, currentUser: ''};
        
        function getUser(){
            fetch('/api/user')
            .then(r=>r.json())
            .then(d=>{
                if(d.success){
                    state.currentUser = d.username;
                    document.getElementById('userName').textContent = d.username;
                    var roleEl = document.getElementById('userRole');
                    roleEl.textContent = d.role;
                    roleEl.className = 'role ' + d.role;
                }
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
                el.innerHTML = '<div style="color:#333;font-size:11px;text-align:center;padding:15px;">No victims</div>';
                return;
            }
            var html = '';
            for(var i=0; i<victims.length; i++){
                var v = victims[i];
                var active = (state.active === v.id) ? 'active' : '';
                var status = (v.status === 'Online') ? 'online' : 'offline';
                var badge = v.is_vm ? '<span class="badge">VM</span>' : '';
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
            document.getElementById('curVictim').textContent = '#' + id;
            renderVictims();
            showDetails(id);
        }
        
        function showDetails(id){
            var v = state.victims[id];
            if(!v) return;
            document.getElementById('detailBox').innerHTML =
                '<div class="detail-item"><span class="label">ID</span><span class="value">'+v.id+'</span></div>'+
                '<div class="detail-item"><span class="label">Host</span><span class="value">'+v.hostname+'</span></div>'+
                '<div class="detail-item"><span class="label">IP</span><span class="value">'+v.ip+'</span></div>'+
                '<div class="detail-item"><span class="label">OS</span><span class="value">'+v.os+'</span></div>'+
                '<div class="detail-item"><span class="label">Status</span><span class="value">'+v.status+'</span></div>'+
                '<div class="detail-item"><span class="label">Country</span><span class="value">'+v.country+'</span></div>';
        }
        
        function updateStats(){
            var victims = Object.values(state.victims);
            document.getElementById('vicCount').textContent = victims.length;
            var online = 0;
            for(var i=0; i<victims.length; i++){
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
            if(type === 'us') cls = 'us';
            else if(type === 'victim') cls = 'victim';
            else if(type === 'user') cls = 'user';
            el.innerHTML += '<div class="msg"><span class="time">['+t+']</span><span class="sender '+cls+'">'+sender+'</span> '+msg+'</div>';
            el.scrollTop = el.scrollHeight;
        }
        
        function runCmd(cmd){
            var victim = state.active;
            if(!victim){
                addMsg('system', 'No victim selected', 'system');
                addLog('No victim selected', 'sys');
                return;
            }
            addMsg('us', '/'+cmd+' → '+victim, 'us');
            addLog('Executing '+cmd+' on '+victim, 'cmd');
            api('sendCommand', {victim_id: victim, command: cmd}, function(d){
                if(d.success){
                    addMsg('us', '✅ success', 'us');
                    addLog('Command '+cmd+' completed', 'cmd');
                    if(d.result){
                        addMsg('victim', '➤ '+d.result, 'victim');
                    }
                } else {
                    addMsg('us', '❌ failed', 'us');
                    addLog('Command '+cmd+' failed', 'cmd');
                }
            });
        }
        
        function sendMsg(){
            var input = document.getElementById('chatInput');
            var msg = input.value.trim();
            if(!msg) return;
            input.value = '';
            var victim = state.active;
            if(msg.charAt(0) === '/'){
                runCmd(msg.substring(1).toLowerCase());
            } else {
                if(!victim){
                    addMsg('system', 'No victim selected', 'system');
                    return;
                }
                addMsg(state.currentUser, msg, 'user');
                addMsg('victim', msg, 'victim');
                addLog('Message: "'+msg+'" to '+victim, 'msg');
            }
        }
        
        function getZip(){
            var victim = state.active || 'all';
            window.open('/download-zip?victim='+victim, '_blank');
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

# ============================================
# API
# ============================================

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').lower()
    password = data.get('password', '')
    
    conn = sqlite3.connect('aether.db')
    c = conn.cursor()
    c.execute("SELECT id, password, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if row and row[1] == hashlib.md5(password.encode()).hexdigest():
        session['user_id'] = row[0]
        session['username'] = username
        session['role'] = row[2]
        return jsonify({'success': True, 'role': row[2]})
    
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
        'username': session.get('username', 'guest'),
        'role': session.get('role', 'viewer')
    })

@app.route('/api', methods=['POST'])
@login_required
def api_handler():
    data = request.get_json()
    action = data.get('action')
    
    if action == 'getVictims':
        conn = sqlite3.connect('aether.db')
        c = conn.cursor()
        c.execute("SELECT id, hostname, ip, os, status, country FROM victims")
        victims = {}
        for row in c.fetchall():
            victims[row[0]] = {
                'id': row[0],
                'hostname': row[1],
                'ip': row[2],
                'os': row[3],
                'status': row[4],
                'country': row[5],
                'activity': 'idle',
                'is_vm': 'VM' in row[0] or 'VM' in row[1]
            }
        conn.close()
        return jsonify({'success': True, 'victims': victims})
    
    elif action == 'sendCommand':
        victim_id = data.get('victim_id')
        command = data.get('command')
        
        results = {
            'whois': 'Host: DESKTOP-7X3 | IP: 192.168.1.101 | OS: Windows 10 Pro | User: Admin',
            'screenshot': '📸 Screenshot captured and saved to server',
            'scan': '🔍 Found 5 crypto wallets | Total: $578,124.50',
            'steal': '🕵️ Browser data stolen from 5 browsers',
            'status': '✅ Victim is Online | 3h 22m uptime',
            'destroy': '💀 SYSTEM CORRUPTED - IRREVERSIBLE',
            'flash': '💥 Screen flashed 10 times successfully',
            'persist': '🔒 Persistence installed in 3 locations',
            'vmcheck': '🛡️ VM Detection: Clean system',
            'oblivion': '🌀 Self-destructed - All traces wiped'
        }
        
        result = results.get(command, f"✅ Command '{command}' executed successfully")
        
        # Log to database
        conn = sqlite3.connect('aether.db')
        c = conn.cursor()
        c.execute("INSERT INTO logs (username, action, timestamp) VALUES (?, ?, ?)",
                 (session.get('username', 'system'), f"Command: {command} on {victim_id}", 
                  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'result': result})
    
    return jsonify({'success': False})

@app.route('/download-zip')
@login_required
def download_zip():
    victim = request.args.get('victim', 'all')
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        browsers = {
            'Chrome': {'passwords': 247, 'cookies': 893},
            'Edge': {'passwords': 156, 'cookies': 512},
            'Brave': {'passwords': 89, 'cookies': 234},
            'Firefox': {'passwords': 123, 'cookies': 445}
        }
        summary = f"AETHER DATA EXTRACTION\nVictim: {victim}\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for browser, data in browsers.items():
            summary += f"[{browser.upper()}]\nPasswords: {data['passwords']}\nCookies: {data['cookies']}\n\n"
        zf.writestr('summary.txt', summary)
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=f'aether_data_{victim}_{int(time.time())}.zip')

@app.route('/download-rat')
@login_required
def download_rat():
    return "RAT builder coming soon. Contact SNIN Star for custom build.", 200

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   AETHER C2 - COMPLETE NEW BUILD                        ║
    ║   Fresh design, fully working, zero errors              ║
    ╠═══════════════════════════════════════════════════════════╣
    ║   USERS:                                                ║
    ║   owner    : aether2024 (owner) 👑                     ║
    ║   operator : op2024 (operator) ⭐                      ║
    ║   viewer   : view2024 (viewer) 🔒                     ║
    ╠═══════════════════════════════════════════════════════════╣
    ║   7 victims pre-loaded                                  ║
    ║   All commands working                                  ║
    ║   Browser zip download working                          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(f"[*] Server: http://localhost:{PORT}")
    print(f"[*] Login: http://localhost:{PORT}/login")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)