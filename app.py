"""
VIRTUALS C2 - ULTRA OPTIMIZED V3
4 Logins | Real-time Activity | Shared Logs
BY: SNIN STAR
"""

from flask import Flask, request, jsonify, session, redirect, url_for
import datetime
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

PORT = int(os.environ.get('PORT', 8080))

# ============================================
# USERS - 4 Separate Logins
# ============================================
USERS = {
    "adam": {"pass": "virtuals2024", "role": "viewer"},
    "jerry": {"pass": "virtuals2024", "role": "operator"},
    "haunt": {"pass": "virtuals2024", "role": "viewer"},
    "owner": {"pass": "whiteknight", "role": "owner"}
}

# ============================================
# SHARED DATA - Everyone sees everything
# ============================================
VICTIMS = {}
COMMANDS = ['whois', 'screenshot', 'scan', 'status', 'steal', 'destroy', 'flash', 'persist']
ACTIVITY_LOG = []  # Shared log - everyone sees this
CHAT_HISTORY = []  # Shared chat - everyone sees this

# Test victims
for i, name in enumerate(['ALPHA', 'BETA', 'GAMMA', 'DELTA', 'VM-01']):
    VICTIMS[f"PC-{name}"] = {
        "id": f"PC-{name}",
        "ip": f"192.168.1.{10+i}",
        "os": "Windows 10" if i != 1 else "Windows 11",
        "status": "Online",
        "last": str(datetime.datetime.now()),
        "activity": "idle"
    }

# ============================================
# DECORATOR
# ============================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# ============================================
# HTML PAGES
# ============================================

INDEX = """<!DOCTYPE html>
<html>
<head><title>VIRTUALS</title>
<style>
*{margin:0;padding:0}
body{background:#0a0a0f;color:#c8c8d0;font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center}
.box{text-align:center}
h1{font-size:48px;font-weight:100;letter-spacing:8px}
h1 span{color:#446688}
.sub{color:#555;margin-top:10px;letter-spacing:4px}
a{position:fixed;bottom:30px;right:30px;color:#555;text-decoration:none;font-size:20px}
</style>
</head>
<body>
<div class="box">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div class="sub">● COMMAND & CONTROL</div>
</div>
<a href="/login">⌘</a>
</body>
</html>"""

LOGIN = """<!DOCTYPE html>
<html>
<head><title>VIRTUALS - Login</title>
<style>
*{margin:0;padding:0}
body{background:#0a0a0f;color:#c8c8d0;font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center}
.box{background:rgba(10,10,18,0.9);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:40px;width:340px}
h1{font-size:24px;font-weight:300;text-align:center;letter-spacing:4px;margin-bottom:5px}
h1 span{color:#446688}
.sub{color:#555;text-align:center;font-size:12px;margin-bottom:25px}
input{width:100%;padding:12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:8px;color:#c8c8d0;font-size:14px;margin-bottom:12px;outline:none}
input:focus{border-color:rgba(68,170,255,0.3)}
button{width:100%;padding:12px;background:rgba(68,170,255,0.1);border:1px solid rgba(68,170,255,0.15);border-radius:8px;color:#88ccdd;font-size:15px;cursor:pointer}
button:hover{background:rgba(68,170,255,0.2)}
.err{color:#cc8888;text-align:center;margin-top:10px;display:none;font-size:13px}
.back{text-align:center;margin-top:12px;font-size:11px;color:#444}
.back a{color:#555;text-decoration:none}
.users{color:#444;font-size:10px;margin-top:15px;border-top:1px solid rgba(255,255,255,0.03);padding-top:12px}
.users span{color:#666;margin:0 4px}
</style>
</head>
<body>
<div class="box">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div class="sub">● Login</div>
<form onsubmit="login(event)">
<input type="text" id="user" placeholder="Username" required>
<input type="password" id="pass" placeholder="Password" required>
<button type="submit">Access</button>
<div class="err" id="err">Invalid credentials</div>
</form>
<div class="back"><a href="/">← Back</a></div>
<div class="users">👤 adam · jerry · haunt · <span style="color:#ffd700">owner</span></div>
</div>
<script>
function login(e){
    e.preventDefault();
    fetch('/api/login', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            username:document.getElementById('user').value,
            password:document.getElementById('pass').value
        })
    }).then(r=>r.json()).then(d=>{
        if(d.success) window.location.href='/dashboard';
        else document.getElementById('err').style.display='block';
    });
}
</script>
</body>
</html>"""

DASHBOARD = """<!DOCTYPE html>
<html>
<head><title>VIRTUALS - C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#c8c8d0;font-family:'Segoe UI',sans-serif;height:100vh;overflow:hidden;font-size:13px}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1)}
.header{background:rgba(10,10,18,0.95);padding:6px 16px;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;justify-content:space-between;align-items:center;height:40px}
h1{font-size:16px;font-weight:300;letter-spacing:3px}
h1 span{color:#446688}
.user-info{display:flex;align-items:center;gap:10px}
.user-info .name{color:#c8c8d0;font-size:13px}
.user-info .role{font-size:9px;padding:2px 8px;border-radius:8px;background:rgba(68,170,255,0.1);color:#88aacc}
.user-info .role.owner{background:rgba(255,215,0,0.15);color:#ffd700}
.stats{display:flex;gap:12px;color:#666;font-size:11px}
.stats span{color:#c8c8d0;font-weight:600}
.logout{background:rgba(200,60,60,0.1);color:#cc8888;border:1px solid rgba(200,60,60,0.1);padding:3px 12px;border-radius:4px;cursor:pointer;font-size:11px}
.logout:hover{background:rgba(200,60,60,0.15)}
.container{display:flex;height:calc(100vh - 40px);padding:4px;gap:4px}
.left{width:150px;min-width:150px;background:rgba(10,10,18,0.8);border:1px solid rgba(255,255,255,0.04);border-radius:6px;padding:4px;display:flex;flex-direction:column}
.left .title{color:#444;font-size:8px;text-transform:uppercase;letter-spacing:2px;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.03)}
.victims{flex:1;overflow-y:auto;padding:2px}
.victim{padding:4px 6px;margin:1px 0;border-radius:3px;cursor:pointer;border-left:2px solid transparent;font-size:12px}
.victim:hover{background:rgba(255,255,255,0.03)}
.victim.active{background:rgba(68,170,255,0.06);border-left-color:#44aaff}
.victim .dot{display:inline-block;width:5px;height:5px;border-radius:50%;margin-right:4px}
.victim .dot.online{background:#44dd88}
.victim .dot.offline{background:#664444}
.middle{flex:1;display:flex;flex-direction:column;gap:4px}
.chat{background:rgba(10,10,18,0.8);border:1px solid rgba(255,255,255,0.04);border-radius:6px;padding:4px 8px;flex:1;display:flex;flex-direction:column}
.chat .title{color:#444;font-size:8px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.03);padding-bottom:3px;display:flex;justify-content:space-between}
.chat .msgs{background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.02);border-radius:4px;padding:4px 6px;flex:1;overflow-y:auto;font-size:12px;line-height:1.5;min-height:80px;max-height:150px}
.chat .msgs .msg{padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.01)}
.chat .msgs .time{color:#444;font-size:9px;margin-right:3px}
.chat .msgs .user-msg{color:#66ddbb}
.chat .msgs .victim-msg{color:#ddbb88}
.chat .msgs .system-msg{color:#8888aa}
.chat .input{display:flex;gap:4px;margin-top:4px}
.chat .input input{flex:1;padding:6px 10px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.04);border-radius:4px;color:#c8c8d0;font-size:13px;outline:none}
.chat .input input:focus{border-color:rgba(255,255,255,0.08)}
.chat .input button{padding:6px 14px;background:rgba(255,255,255,0.03);color:#aaa;border:1px solid rgba(255,255,255,0.04);border-radius:4px;cursor:pointer}
.chat .input button:hover{background:rgba(255,255,255,0.06)}
.cmds{display:flex;flex-wrap:wrap;gap:3px;margin-top:3px}
.cmds span{padding:2px 8px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);border-radius:3px;font-size:10px;color:#8888aa;cursor:pointer}
.cmds span:hover{background:rgba(255,255,255,0.04);color:#c8c8d0}
.right{width:200px;min-width:160px;display:flex;flex-direction:column;gap:4px}
.details{background:rgba(10,10,18,0.8);border:1px solid rgba(255,255,255,0.04);border-radius:6px;padding:4px 8px;height:45%;overflow-y:auto}
.details .title{color:#444;font-size:8px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.03);padding-bottom:3px}
.detail-item{font-size:11px;padding:2px 0;display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.01)}
.detail-item .label{color:#555}
.detail-item .value{color:#c8c8d0}
.logs{background:rgba(10,10,18,0.8);border:1px solid rgba(255,255,255,0.04);border-radius:6px;padding:4px 8px;flex:1;overflow-y:auto}
.logs .title{color:#444;font-size:8px;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid rgba(255,255,255,0.03);padding-bottom:3px}
.log-item{font-size:10px;padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.01);display:flex;gap:4px}
.log-item .user{color:#66ddbb}
.log-item .action{color:#ddbb88}
.log-item .time{color:#444;font-size:8px}
.log-item .type{font-size:7px;padding:0 4px;border-radius:2px}
.log-item .type.cmd{background:rgba(68,170,255,0.1);color:#44aaff}
.log-item .type.msg{background:rgba(68,220,180,0.1);color:#66ddbb}
.log-item .type.sys{background:rgba(255,255,255,0.05);color:#888}
</style>
</head>
<body>
<div class="header">
<h1>◈ VIRTUALS <span>C2</span></h1>
<div style="display:flex;align-items:center;gap:12px;">
<div class="stats">
<span>VICTIMS <span id="vicCount">0</span></span>
<span>ONLINE <span id="onCount">0</span></span>
</div>
<div class="user-info">
<span class="name" id="userName">guest</span>
<span class="role" id="userRole">viewer</span>
</div>
<button class="logout" onclick="logout()">Logout</button>
</div>
</div>
<div class="container">
<div class="left">
<div class="title">VICTIMS</div>
<div class="victims" id="victimList"><div style="color:#444;font-size:11px;text-align:center;padding:10px;">No victims</div></div>
</div>
<div class="middle">
<div class="chat">
<div class="title">CONSOLE <span id="curVictim">#none</span></div>
<div class="msgs" id="msgBox"><div class="msg"><span class="time">[system]</span><span class="system-msg">ready</span></div></div>
<div class="input">
<input id="chatInput" placeholder="/command or message" onkeypress="if(event.key==='Enter')sendMsg()">
<button onclick="sendMsg()">Send</button>
</div>
<div class="cmds">
<span onclick="runCmd('whois')">whois</span>
<span onclick="runCmd('screenshot')">screenshot</span>
<span onclick="runCmd('scan')">scan</span>
<span onclick="runCmd('status')">status</span>
<span onclick="runCmd('steal')">steal</span>
<span onclick="runCmd('destroy')">destroy</span>
<span onclick="runCmd('flash')">flash</span>
<span onclick="runCmd('persist')">persist</span>
</div>
</div>
</div>
<div class="right">
<div class="details">
<div class="title">DETAILS</div>
<div id="detailBox"><div style="color:#444;font-size:11px;text-align:center;padding:8px;">Select a victim</div></div>
</div>
<div class="logs">
<div class="title">ACTIVITY LOG</div>
<div id="logBox"><div style="color:#444;font-size:10px;padding:4px;">No activity yet</div></div>
</div>
</div>
</div>
<script>
var state = {victims: {}, active: null, currentUser: 'guest'};

// Get current user info
function getUser(){
    fetch('/api/user').then(r=>r.json()).then(d=>{
        if(d.success){
            state.currentUser = d.username;
            document.getElementById('userName').textContent = d.username;
            var roleEl = document.getElementById('userRole');
            roleEl.textContent = d.role;
            roleEl.className = 'role';
            if(d.role === 'owner') roleEl.classList.add('owner');
        }
    });
}

function logout(){
    fetch('/api/logout', {method: 'POST'}).then(()=>{
        window.location.href = '/login';
    });
}

function api(action, data, cb){
    fetch('/api', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: action, ...data})
    }).then(r=>r.json()).then(cb).catch(()=>{});
}

// Refresh victims
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
    if(victims.length === 0){
        el.innerHTML = '<div style="color:#444;font-size:11px;text-align:center;padding:10px;">No victims</div>';
        return;
    }
    var html = '';
    for(var i=0; i<victims.length; i++){
        var v = victims[i];
        var active = (state.active === v.id) ? 'active' : '';
        var status = (v.status === 'Online') ? 'online' : 'offline';
        html += '<div class="victim '+active+'" onclick="selectVictim(\''+v.id+'\')">'+
            '<span class="dot '+status+'"></span>'+
            '<span>'+v.id+'</span>'+
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
        '<div class="detail-item"><span class="label">IP</span><span class="value">'+v.ip+'</span></div>'+
        '<div class="detail-item"><span class="label">OS</span><span class="value">'+v.os+'</span></div>'+
        '<div class="detail-item"><span class="label">Status</span><span class="value">'+v.status+'</span></div>'+
        '<div class="detail-item"><span class="label">Activity</span><span class="value">'+v.activity+'</span></div>';
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

// Get shared logs
function getLogs(){
    fetch('/api/logs').then(r=>r.json()).then(d=>{
        if(d.success && d.logs){
            var el = document.getElementById('logBox');
            if(d.logs.length === 0){
                el.innerHTML = '<div style="color:#444;font-size:10px;padding:4px;">No activity yet</div>';
                return;
            }
            var html = '';
            for(var i=d.logs.length-1; i>=0; i--){
                var log = d.logs[i];
                html += '<div class="log-item">'+
                    '<span class="time">['+log.time+']</span>'+
                    '<span class="user">'+log.user+'</span>'+
                    '<span class="type '+log.type+'">'+log.type+'</span>'+
                    '<span class="action">'+log.action+'</span>'+
                    '</div>';
            }
            el.innerHTML = html;
        }
    });
}

function addMsg(sender, msg, type){
    var el = document.getElementById('msgBox');
    var t = new Date().toLocaleTimeString();
    var cls = 'system-msg';
    if(type === 'us') cls = 'user-msg';
    else if(type === 'victim') cls = 'victim-msg';
    el.innerHTML += '<div class="msg"><span class="time">['+t+']</span><span class="'+cls+'">'+sender+'</span> '+msg+'</div>';
    el.scrollTop = el.scrollHeight;
}

function runCmd(cmd){
    var victim = state.active;
    if(!victim){
        addMsg('system', 'No victim selected', 'system');
        return;
    }
    addMsg(state.currentUser, '/'+cmd+' → '+victim, 'us');
    
    api('sendCommand', {victim_id: victim, command: cmd}, function(d){
        if(d.success){
            addMsg('system', '✅ Command sent: '+cmd, 'system');
            // Add to shared log
            fetch('/api/log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user: state.currentUser,
                    action: 'Command: '+cmd+' on '+victim,
                    type: 'cmd'
                })
            });
            // Get result
            fetch('/api/command-result?cmd='+cmd).then(r=>r.json()).then(res=>{
                if(res.result){
                    addMsg('victim', '➤ '+res.result, 'victim');
                }
            });
        } else {
            addMsg('system', '❌ Command failed', 'system');
        }
    });
    getLogs();
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
        addMsg(state.currentUser, msg, 'us');
        addMsg('victim', msg, 'victim');
        // Add to shared log
        fetch('/api/log', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user: state.currentUser,
                action: 'Message: "'+msg+'" to '+victim,
                type: 'msg'
            })
        });
        getLogs();
    }
}

setInterval(refresh, 3000);
setInterval(getLogs, 2000);
getUser();
refresh();
getLogs();
</script>
</body>
</html>"""

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return INDEX

@app.route('/login')
def login_page():
    return LOGIN

@app.route('/dashboard')
@login_required
def dashboard():
    return DASHBOARD

# ============================================
# API ROUTES
# ============================================

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username', '').lower()
    password = data.get('password', '')
    
    if username in USERS and USERS[username]['pass'] == password:
        session['user'] = username
        session['role'] = USERS[username]['role']
        # Log login
        ACTIVITY_LOG.append({
            'time': datetime.datetime.now().strftime('%H:%M:%S'),
            'user': username,
            'action': 'Logged in',
            'type': 'sys'
        })
        return jsonify({'success': True, 'username': username, 'role': USERS[username]['role']})
    
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
        'username': session['user'],
        'role': session.get('role', 'viewer')
    })

@app.route('/api', methods=['POST'])
@login_required
def api_handler():
    data = request.json
    action = data.get('action')
    
    if action == 'getVictims':
        return jsonify({'success': True, 'victims': VICTIMS})
    
    elif action == 'sendCommand':
        victim_id = data.get('victim_id')
        command = data.get('command')
        
        if victim_id in VICTIMS:
            # Log command
            ACTIVITY_LOG.append({
                'time': datetime.datetime.now().strftime('%H:%M:%S'),
                'user': session['user'],
                'action': f'Command: {command} on {victim_id}',
                'type': 'cmd'
            })
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Victim not found'})
    
    return jsonify({'success': False, 'error': 'Unknown action'})

@app.route('/api/logs')
@login_required
def api_logs():
    return jsonify({'success': True, 'logs': ACTIVITY_LOG})

@app.route('/api/log', methods=['POST'])
@login_required
def api_log():
    data = request.json
    ACTIVITY_LOG.append({
        'time': datetime.datetime.now().strftime('%H:%M:%S'),
        'user': data.get('user', session['user']),
        'action': data.get('action', ''),
        'type': data.get('type', 'sys')
    })
    return jsonify({'success': True})

@app.route('/api/command-result')
@login_required
def api_command_result():
    cmd = request.args.get('cmd', '')
    results = {
        'whois': 'PC: DESKTOP-ALPHA | IP: 192.168.1.10 | OS: Windows 10 Pro',
        'screenshot': '📸 Screenshot captured and saved',
        'scan': '🔍 Found 5 crypto wallets | Total: $578,124',
        'status': '✅ Victim is Online | 2h remaining',
        'steal': '🕵️ Browser data stolen from 5 browsers',
        'destroy': '💀 SYSTEM CORRUPTED - IRREVERSIBLE',
        'flash': '💥 Screen flashed 10 times',
        'persist': '🔒 Persistence installed in 3 locations'
    }
    return jsonify({'result': results.get(cmd, 'Command executed successfully')})

# ============================================
# RUN
# ============================================

if __name__ == '__main__':
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   VIRTUALS C2 - ULTRA OPTIMIZED      ║
    ║   Running on http://localhost:{PORT}  ║
    ╠═══════════════════════════════════════╣
    ║   Users:                             ║
    ║   adam    : virtuals2024 (viewer)    ║
    ║   jerry   : virtuals2024 (operator)  ║
    ║   haunt   : virtuals2024 (viewer)    ║
    ║   owner   : whiteknight (owner)      ║
    ╚═══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)