"""
VIRTUALS C2 - COMPLETE FIXED
Login Working - No Syntax Errors
BY: SNIN STAR
"""

from flask import Flask, request, jsonify, send_file, session, redirect, url_for
import sqlite3
import datetime
import random
import json
import os
import hashlib
import time
import zipfile
from io import BytesIO
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'virtuals_c2_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

PORT = int(os.environ.get('PORT', 8080))

# ============================================
# USERS
# ============================================
USERS = {
    "adam": {"password": "virtuals2024", "role": "viewer", "can_chat": False},
    "jerry": {"password": "virtuals2024", "role": "operator", "can_chat": True},
    "haunt": {"password": "virtuals2024", "role": "viewer", "can_chat": False},
    "owner": {"password": "whiteknight", "role": "owner", "can_chat": True}
}

CHAT_USERS = ["jerry", "owner"]

# ============================================
# DATABASE
# ============================================
def get_db():
    conn = sqlite3.connect('virtuals_c2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
        id TEXT PRIMARY KEY, pc TEXT, ip TEXT, os TEXT, status TEXT,
        is_vm INTEGER DEFAULT 0, first_seen TEXT, last_seen TEXT,
        activity TEXT DEFAULT 'idle'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, 
        password TEXT, role TEXT, can_chat INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT,
        action TEXT, timestamp TEXT, type TEXT DEFAULT 'info'
    )''')
    
    for username, info in USERS.items():
        hashed = hashlib.md5(info['password'].encode()).hexdigest()
        c.execute("INSERT OR REPLACE INTO users (username, password, role, can_chat) VALUES (?, ?, ?, ?)",
                 (username, hashed, info['role'], 1 if info['can_chat'] else 0))
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
        ("PC-ALPHA", "DESKTOP-ALPHA", "192.168.1.10", "Windows 10 Pro", 0, "idle"),
        ("PC-BETA", "LAPTOP-BETA", "192.168.1.11", "Windows 11 Pro", 0, "typing"),
        ("PC-GAMMA", "WORKSTATION-GAMMA", "192.168.1.12", "Windows 10 Pro", 0, "reading"),
        ("PC-VM-01", "VM-TEST-01", "192.168.1.13", "Windows 10 Pro", 1, "idle"),
        ("PC-DELTA", "DESKTOP-DELTA", "192.168.1.14", "Windows 11 Pro", 0, "processing"),
        ("PC-OMEGA", "SERVER-OMEGA", "192.168.1.15", "Windows Server 2022", 0, "active"),
        ("PC-ZETA", "LAPTOP-ZETA", "192.168.1.16", "Windows 10 Pro", 0, "idle")
    ]
    for v in victims:
        c.execute("INSERT OR REPLACE INTO victims (id, pc, ip, os, status, is_vm, first_seen, last_seen, activity) VALUES (?, ?, ?, ?, 'Online', ?, ?, ?, ?)",
                 (v[0], v[1], v[2], v[3], v[4], now, now, v[5]))
    conn.commit()
    conn.close()

create_test_victims()

# ============================================
# DECORATORS
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
            return jsonify({'error': 'Permission denied'}), 403
        return f(*args, **kwargs)
    return decorated

# ============================================
# HTML PAGES
# ============================================

LANDING_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#0a0a0f,#1a0a2e);color:#c8c8d0;font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center}
.box{text-align:center}
.box h1{color:#e8e8f0;font-size:72px;font-weight:100;letter-spacing:8px;opacity:0.6}
.box h1 span{color:#446688}
.box .sub{color:#555568;font-size:18px;margin-top:10px;letter-spacing:4px}
.box .sub .dot{color:#44dd88}
.link{position:fixed;bottom:30px;right:30px;width:50px;height:50px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:24px;color:#666680;cursor:pointer;transition:0.3s;text-decoration:none}
.link:hover{background:rgba(255,255,255,0.1);color:#e8e8f0}
</style>
</head>
<body>
<div class="box">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div class="sub"><span class="dot">●</span> COMMAND &amp; CONTROL</div>
</div>
<a href="/login" class="link">⌘</a>
</body>
</html>
'''

LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>VIRTUALS C2 - Login</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#0a0a0f,#1a0a2e);color:#c8c8d0;font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center}
.login-box{background:rgba(10,10,18,0.85);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:40px;width:400px;max-width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.5)}
.login-box h1{color:#e8e8f0;font-size:28px;font-weight:300;text-align:center;letter-spacing:4px;margin-bottom:5px}
.login-box h1 span{color:#446688}
.login-box .sub{color:#666680;text-align:center;font-size:13px;margin-bottom:30px}
.login-box .sub .dot{color:#44dd88}
.login-box label{color:#8888a0;font-size:13px;display:block;margin-bottom:5px}
.login-box input{width:100%;padding:14px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:8px;color:#e8e8f0;font-size:16px;outline:none;margin-bottom:15px}
.login-box input:focus{border-color:rgba(68,170,255,0.4)}
.login-box input::placeholder{color:#444458}
.login-box button{width:100%;padding:14px;background:rgba(68,170,255,0.15);border:1px solid rgba(68,170,255,0.2);border-radius:8px;color:#88ccdd;font-size:17px;cursor:pointer;transition:0.3s;font-weight:600}
.login-box button:hover{background:rgba(68,170,255,0.25)}
.login-box .error{color:#cc8888;text-align:center;margin-top:10px;display:none;font-size:14px}
.login-box .back{text-align:center;margin-top:15px;font-size:12px;color:#555568}
.login-box .back a{color:#666680;text-decoration:none}
.login-box .back a:hover{color:#88aacc}
.users{color:#444;font-size:10px;margin-top:15px;border-top:1px solid rgba(255,255,255,0.03);padding-top:12px;text-align:center}
.users .operator{color:#66ddbb}
.users .owner{color:#ffd700}
</style>
</head>
<body>
<div class="login-box">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div class="sub"><span class="dot">●</span> Control Panel Login</div>
<form onsubmit="login(event)">
<label>Username</label>
<input type="text" id="user" placeholder="Enter username" required>
<label>Password</label>
<input type="password" id="pass" placeholder="Enter password" required>
<button type="submit">Access Panel</button>
<div class="error" id="err">Invalid credentials</div>
</form>
<div class="back"><a href="/">← Back</a></div>
<div class="users">👤 adam · <span class="operator">jerry</span> · haunt · <span class="owner">owner</span></div>
</div>
<script>
function login(e){
    e.preventDefault();
    var u = document.getElementById('user').value;
    var p = document.getElementById('pass').value;
    fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: u, password: p})
    })
    .then(r => r.json())
    .then(d => {
        if(d.success){
            window.location.href = '/dashboard';
        } else {
            document.getElementById('err').style.display = 'block';
        }
    })
    .catch(() => {
        document.getElementById('err').style.display = 'block';
    });
}
</script>
</body>
</html>
'''

DASHBOARD_PAGE = '''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>VIRTUALS C2 - Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#c8c8d0;font-family:'Segoe UI',sans-serif;height:100vh;overflow:hidden;font-size:14px}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:rgba(255,255,255,0.02)}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.12);border-radius:3px}
.header{background:rgba(10,10,18,0.95);padding:6px 16px;border-bottom:1px solid rgba(255,255,255,0.05);display:flex;justify-content:space-between;align-items:center;height:42px}
.header h1{color:#e8e8f0;font-size:16px;font-weight:300;letter-spacing:3px}
.header h1 span{color:#446688}
.header .info{display:flex;align-items:center;gap:8px;color:#8888a0;font-size:12px}
.header .info .name{color:#e8e8f0;font-weight:500}
.header .info .role{font-size:9px;padding:2px 10px;border-radius:10px}
.header .info .role.owner{background:rgba(255,215,0,0.2);color:#ffd700}
.header .info .role.operator{background:rgba(68,220,180,0.15);color:#66ddbb}
.header .info .role.viewer{background:rgba(68,170,255,0.1);color:#88aacc}
.header .stats{display:flex;gap:12px;align-items:center}
.header .stats .item{color:#8888a0;font-size:11px}
.header .stats .item .num{color:#e8e8f0;font-weight:600;font-size:14px;margin-left:3px}
.header .logout{background:rgba(200,60,60,0.12);color:#cc8888;border:1px solid rgba(200,60,60,0.15);padding:3px 12px;border-radius:4px;cursor:pointer;font-size:11px}
.header .logout:hover{background:rgba(200,60,60,0.2)}
.container{display:flex;height:calc(100vh - 42px);padding:4px;gap:4px}
.left{width:160px;min-width:160px;display:flex;flex-direction:column;gap:3px;height:100%;background:rgba(10,10,18,0.85);border:1px solid rgba(255,255,255,0.05);border-radius:6px;padding:4px 6px}
.left .title{color:#666680;font-size:8px;text-transform:uppercase;letter-spacing:2px;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.04)}
.victim-list{flex:1;overflow-y:auto;padding:2px}
.victim{display:flex;align-items:center;padding:3px 6px;margin:1px 0;border-radius:3px;cursor:pointer;border-left:2px solid transparent;font-size:12px}
.victim:hover{background:rgba(255,255,255,0.04)}
.victim.active{background:rgba(68,170,255,0.08);border-left-color:#44aaff}
.victim .dot{width:5px;height:5px;border-radius:50%;margin-right:5px}
.victim .dot.online{background:#44dd88}
.victim .dot.offline{background:#664444}
.victim .name{color:#e8e8f0;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.victim .badge{background:rgba(200,60,60,0.12);color:#cc8888;font-size:6px;padding:0 4px;border-radius:4px;line-height:12px;height:12px;margin-left:3px}
.victim .act{color:#666680;font-size:7px;margin-left:3px;font-style:italic}
.middle{flex:1;display:flex;flex-direction:column;gap:4px;min-width:200px;height:100%}
.chat{background:rgba(10,10,18,0.85);border:1px solid rgba(255,255,255,0.05);border-radius:6px;padding:4px 8px;flex:1;display:flex;flex-direction:column}
.chat .title{color:#666680;font-size:8px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:3px;margin-bottom:3px;display:flex;justify-content:space-between}
.chat .title .victim-name{color:#88aacc;font-weight:500}
.chat .msgs{background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.03);border-radius:4px;padding:4px 6px;flex:1;overflow-y:auto;min-height:80px;max-height:130px;font-size:12px;line-height:1.5}
.chat .msgs .msg{padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.01)}
.chat .msgs .time{color:#555568;margin-right:3px;font-size:9px}
.chat .msgs .sender{font-weight:600;font-size:12px}
.chat .msgs .sender.us{color:#66ddbb}
.chat .msgs .sender.victim{color:#ddbb88}
.chat .msgs .sender.system{color:#8888aa}
.chat .msgs .sender.user{color:#88aacc}
.chat .input-area{display:flex;gap:4px;margin-top:4px}
.chat .input-area input{flex:1;padding:6px 12px;background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.04);border-radius:4px;color:#c8c8d0;font-family:inherit;font-size:14px;outline:none;min-height:34px}
.chat .input-area input:focus{border-color:rgba(255,255,255,0.1)}
.chat .input-area input::placeholder{color:#444458;font-size:12px}
.chat .input-area button{padding:6px 14px;background:rgba(255,255,255,0.04);color:#b0b0c0;border:1px solid rgba(255,255,255,0.05);border-radius:4px;cursor:pointer;font-family:inherit;font-size:13px;min-height:34px}
.chat .input-area button:hover{background:rgba(255,255,255,0.08);color:#e8e8f0}
.commands-box{background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.03);border-radius:4px;padding:3px 6px;margin-top:3px;max-height:70px;overflow-y:auto}
.commands-box .cmd{display:inline-block;padding:1px 6px;margin:1px 2px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.03);border-radius:3px;font-size:10px;color:#8888aa;cursor:pointer}
.commands-box .cmd:hover{background:rgba(255,255,255,0.06);color:#e8e8f0}
.commands-box .cmd-title{color:#666680;font-size:7px;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;display:block}
.downloads{display:flex;gap:4px;margin-top:3px;flex-wrap:wrap}
.downloads button{background:rgba(50,180,120,0.12);color:#66ddbb;border:1px solid rgba(50,180,120,0.15);padding:3px 12px;border-radius:4px;cursor:pointer;font-size:12px;min-height:28px}
.downloads button:hover{background:rgba(50,180,120,0.2)}
.downloads .zip{background:rgba(50,180,200,0.12);color:#88ccdd;border:1px solid rgba(50,180,200,0.15)}
.downloads .zip:hover{background:rgba(50,180,200,0.2)}
.right{width:220px;min-width:180px;display:flex;flex-direction:column;gap:4px;height:100%}
.details{background:rgba(10,10,18,0.85);border:1px solid rgba(255,255,255,0.05);border-radius:6px;padding:4px 8px;height:45%;overflow-y:auto}
.details .title{color:#666680;font-size:8px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:3px;margin-bottom:3px}
.detail-item{padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.02);font-size:11px;display:flex;justify-content:space-between}
.detail-item .label{color:#555568}
.detail-item .value{color:#e8e8f0;font-weight:500}
.logs{background:rgba(10,10,18,0.85);border:1px solid rgba(255,255,255,0.05);border-radius:6px;padding:4px 8px;flex:1;overflow-y:auto}
.logs .title{color:#666680;font-size:8px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.04);padding-bottom:3px;margin-bottom:3px}
.log-item{padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.01);font-size:9px;display:flex;gap:3px}
.log-item .type{padding:0 3px;border-radius:2px;font-size:5px;text-transform:uppercase;font-weight:600;margin-top:1px}
.log-item .type.success{background:rgba(50,180,120,0.2);color:#66ddbb}
.log-item .type.failed{background:rgba(180,50,50,0.2);color:#cc8888}
.log-item .type.info{background:rgba(68,170,255,0.12);color:#44aaff}
.log-item .time{color:#444458;font-size:7px}
.log-item .content{color:#b0b0c0;font-size:9px}
.perms-badge{font-size:7px;padding:1px 5px;border-radius:3px;margin-left:5px}
.perms-badge.full{background:rgba(68,220,180,0.15);color:#66ddbb}
.perms-badge.limited{background:rgba(68,170,255,0.1);color:#88aacc}
</style>
</head>
<body>
<div class="header">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div style="display:flex;align-items:center;gap:8px;">
<div class="stats">
<span class="item">VICTIMS <span class="num" id="vicCount">0</span></span>
<span class="item">ONLINE <span class="num" id="onCount">0</span></span>
</div>
<div class="info">
<span class="name" id="userName">Loading...</span>
<span class="role" id="userRole">loading</span>
<span id="permsBadge"></span>
</div>
<button class="logout" onclick="logout()">Logout</button>
</div>
</div>
<div class="container">
<div class="left">
<div class="title">VICTIMS</div>
<div class="victim-list" id="victimList"><div style="color:#444;font-size:11px;text-align:center;padding:10px;">Loading...</div></div>
</div>
<div class="middle">
<div class="chat">
<div class="title">CONSOLE <span class="victim-name" id="curVictim">#general</span></div>
<div class="msgs" id="msgBox"><div class="msg"><span class="time">[system]</span><span class="sender system">ready</span></div></div>
<div class="input-area">
<input id="chatInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendMsg()">
<button onclick="sendMsg()">send</button>
</div>
<div class="commands-box">
<span class="cmd-title">📋 COMMANDS</span>
<span class="cmd" onclick="runCmd('whois')">whois</span>
<span class="cmd" onclick="runCmd('flash')">flash</span>
<span class="cmd" onclick="runCmd('screenshot')">screenshot</span>
<span class="cmd" onclick="runCmd('scan')">scan</span>
<span class="cmd" onclick="runCmd('steal')">steal</span>
<span class="cmd" onclick="runCmd('destroy')">destroy</span>
<span class="cmd" onclick="runCmd('status')">status</span>
</div>
</div>
</div>
<div class="right">
<div class="details">
<div class="title">DETAILS</div>
<div id="detailBox"><div style="color:#444;font-size:11px;padding:8px;">Select a victim</div></div>
</div>
<div class="logs">
<div class="title">ACTIVITY LOG</div>
<div id="logBox"><div style="color:#444;font-size:10px;padding:4px;">no logs</div></div>
</div>
</div>
</div>
<script>
var state = {victims: {}, active: null, currentUser: '', canChat: false};

function getUser(){
    fetch('/api/get_user')
    .then(r=>r.json())
    .then(d=>{
        if(d.success){
            state.currentUser = d.username;
            state.canChat = d.can_chat || false;
            document.getElementById('userName').textContent = d.username;
            var roleEl = document.getElementById('userRole');
            roleEl.textContent = d.role;
            roleEl.className = 'role ' + d.role;
            var badgeEl = document.getElementById('permsBadge');
            if(state.canChat){
                badgeEl.innerHTML = '<span class="perms-badge full">⭐ CHAT</span>';
            } else {
                badgeEl.innerHTML = '<span class="perms-badge limited">🔒 VIEW</span>';
                document.getElementById('chatInput').disabled = true;
                document.getElementById('chatInput').placeholder = '⛔ View only';
                document.querySelector('#chatInputArea button').disabled = true;
            }
        }
    });
}

function logout(){
    fetch('/api/logout',{method:'POST'}).then(()=>window.location.href='/login');
}

function api(action, data, cb){
    fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:action,...data})})
    .then(r=>r.json()).then(cb).catch(()=>{});
}

function refresh(){
    api('getVictims',{},function(d){
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
        el.innerHTML = '<div style="color:#444;font-size:11px;text-align:center;padding:10px;">No victims</div>';
        return;
    }
    var html = '';
    for(var i=0;i<victims.length;i++){
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
    var v = state.victims[id];
    if(v){
        document.getElementById('detailBox').innerHTML =
            '<div class="detail-item"><span class="label">ID</span><span class="value">'+v.id+'</span></div>'+
            '<div class="detail-item"><span class="label">PC</span><span class="value">'+v.pc+'</span></div>'+
            '<div class="detail-item"><span class="label">IP</span><span class="value">'+v.ip+'</span></div>'+
            '<div class="detail-item"><span class="label">OS</span><span class="value">'+v.os+'</span></div>'+
            '<div class="detail-item"><span class="label">Status</span><span class="value">'+v.status+'</span></div>';
    }
}

function updateStats(){
    var victims = Object.values(state.victims);
    document.getElementById('vicCount').textContent = victims.length;
    var online = 0;
    for(var i=0;i<victims.length;i++){
        if(victims[i].status === 'Online') online++;
    }
    document.getElementById('onCount').textContent = online;
}

function addLog(type, content){
    var el = document.getElementById('logBox');
    var time = new Date().toLocaleTimeString();
    el.innerHTML = '<div class="log-item"><span class="time">['+time+']</span><span class="type '+type+'">'+type+'</span><span class="content">'+content+'</span></div>' + el.innerHTML;
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
        addMsg('system','no victim selected','system');
        return;
    }
    addMsg('us','/'+cmd+' → '+victim,'us');
    api('sendCommand',{victim_id:victim,command:cmd},function(d){
        if(d.success){
            addMsg('us','✅ success','us');
            if(d.result) addMsg('victim','➤ '+d.result,'victim');
        } else {
            addMsg('us','❌ failed','us');
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
            addMsg('system','no victim selected','system');
            return;
        }
        addMsg(state.currentUser, msg, 'user');
        addMsg('victim', msg, 'victim');
    }
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
def landing():
    return LANDING_PAGE

@app.route('/login')
def login_page():
    return LOGIN_PAGE

@app.route('/dashboard')
@login_required
def dashboard():
    return DASHBOARD_PAGE

@app.route('/api/get_user', methods=['GET'])
@login_required
def api_get_user():
    return jsonify({
        'success': True,
        'username': session.get('username', 'guest'),
        'role': session.get('role', 'viewer'),
        'can_chat': session.get('can_chat', False)
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').lower()
    password = data.get('password', '')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT password, role, can_chat FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if row and row[0] == hashlib.md5(password.encode()).hexdigest():
        session['logged_in'] = True
        session['username'] = username
        session['role'] = row[1]
        session['can_chat'] = bool(row[2])
        return jsonify({'success': True, 'role': row[1], 'can_chat': bool(row[2])})
    
    return jsonify({'success': False})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api', methods=['POST'])
@login_required
def api_handler():
    data = request.get_json()
    action = data.get('action')
    
    if action == 'getVictims':
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, pc, ip, os, status, is_vm, activity FROM victims")
        victims = {}
        for row in c.fetchall():
            victims[row[0]] = {
                'id': row[0], 'pc': row[1], 'ip': row[2],
                'os': row[3], 'status': row[4], 'is_vm': row[5],
                'activity': row[6] if row[6] else 'idle'
            }
        conn.close()
        return jsonify({'success': True, 'victims': victims})
    
    elif action == 'sendCommand':
        victim_id = data.get('victim_id')
        command = data.get('command')
        
        results = {
            'whois': 'PC: DESKTOP-ALPHA | IP: 192.168.1.10 | OS: Windows 10 Pro',
            'flash': '💥 Screen flashed 10 times',
            'screenshot': '📸 Screenshot captured',
            'scan': '🔍 Found 5 crypto wallets',
            'steal': '🕵️ Browser data stolen',
            'destroy': '💀 SYSTEM CORRUPTED',
            'status': '✅ Victim is Online'
        }
        result = results.get(command, f"✅ Command '{command}' executed")
        return jsonify({'success': True, 'result': result})
    
    return jsonify({'success': False})

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
        summary = "BROWSER DATA\nVictim: " + victim_id + "\nTime: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
        for browser, data in browsers.items():
            summary += f"[{browser.upper()}]\nPasswords: {data['passwords']}\nCookies: {data['cookies']}\n\n"
        zip_file.writestr('summary.txt', summary)
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=f'browser_data_{victim_id}.zip')

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════╗
    ║   VIRTUALS C2 - COMPLETE FIXED          ║
    ║   Login Working - No Syntax Errors      ║
    ╠═══════════════════════════════════════════╣
    ║   adam    : virtuals2024 (viewer)       ║
    ║   jerry   : virtuals2024 (operator)     ║
    ║   haunt   : virtuals2024 (viewer)       ║
    ║   owner   : whiteknight (owner)         ║
    ╚═══════════════════════════════════════════╝
    """)
    print(f"[*] Server: http://localhost:{PORT}")
    print(f"[*] Login: http://localhost:{PORT}/login")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)