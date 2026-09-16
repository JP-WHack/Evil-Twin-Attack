<div align="center">

# Evil Twin Attack 研究ツール

**Wi-Fi セキュリティ研究用 Evil Twin 攻撃シミュレーター**

![Python](https://img.shields.io/badge/Python-3.6+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![License](https://img.shields.io/badge/License-Educational-FF8C00?style=for-the-badge)

</div>

---

## 📖 概要

Evil Twin 攻撃の仕組みを理解し、防御策を研究するための教育用ツールです。偽の Wi-Fi アクセスポイント（Evil Twin）を作成し、Captive Portal を通じてクレデンシャルを収集する手法を学習できます。

> ⚠️ **重要**: 本ソフトウェアは許可された実験環境での教育利用専用に設計されています。

---

## ✨ 主な機能

* 偽の Wi-Fi アクセスポイント作成
* Captive Portal 実装
* DNS スプーフィング
* HTTPS リダイレクト対応
* クレデンシャル収集とログ記録
* 自動クリーンアップ機能

---

## 🛠️ 技術仕様

| 項目 | 詳細 |
|------|------|
| アクセスポイント | hostapd |
| DHCP/DNS | dnsmasq |
| Web サーバー | Python HTTPServer |
| トラフィック制御 | iptables |
| デフォルトポート | 80 (HTTP) |
| 言語 | Python 3.6 以上 |

---

## 📋 システム要件

* Linux（Debian/Ubuntu/Kali 推奨）
* root 権限
* Wi-Fi アダプター（モニターモード対応）
* 必要なパッケージ: hostapd, dnsmasq, iptables

---

## 📥 インストール

必要なパッケージをインストール:

```bash
sudo apt update
sudo apt install -y hostapd dnsmasq iptables
```

---

## 💻 使用方法

### 基本的な使い方

1. Wi-Fi インターフェースを確認:

```bash
iwconfig
```

2. スクリプトを編集して設定を変更（必要に応じて）:

```python
INTERFACE = "wlan0"                # 使用する Wi-Fi インターフェース
EVIL_TWIN_SSID = "Research_Wifi"   # 偽装する SSID 名
CHANNEL = "6"                      # Wi-Fi チャンネル
```

3. スクリプトを実行:

```bash
sudo python3 server.py
```

4. 停止する場合:

```
Ctrl+C
```

自動的にクリーンアップが実行されます。

---

## 🏗️ アーキテクチャ

```
デバイス
    |
    v
偽の Wi-Fi AP (Evil Twin)
    |
    v
Captive Portal (偽ログインページ)
    |
    v
クレデンシャル収集
    |
    v
ログファイルに保存
```

### 処理フロー

1. hostapd で偽の Wi-Fi アクセスポイントを作成
2. dnsmasq で DHCP/DNS サーバーを起動
3. iptables で全 HTTPS トラフィックを HTTP にリダイレクト
4. Captive Portal で偽ログインページを表示
5. 入力されたクレデンシャルをログファイルに記録
6. ユーザーを正規の Web サイトにリダイレクト

---

## ⚙️ 設定

### SSID 変更

```python
EVIL_TWIN_SSID = "Free_WiFi"  # 任意の SSID 名に変更
```

### チャンネル変更

```python
CHANNEL = "11"  # 1-13 の範囲で設定
```

### ログファイル変更

```python
LOG_FILE = "credentials.txt"
```

---

## 📝 ログの確認

収集されたクレデンシャルは指定したログファイルに保存されます:

```bash
cat stolen_test_credentials.txt
```

出力例:

```
[2024-12-11 10:30:45] USER: testuser PASS: testpass123
[2024-12-11 10:31:20] USER: demo PASS: password
```

---

## 🔍 トラブルシューティング

### Wi-Fi アダプターが認識されない

```bash
# 利用可能なインターフェースを確認
iwconfig

# インターフェース名を確認して、スクリプトの INTERFACE 変数を更新
```

### hostapd が起動しない

```bash
# NetworkManager を停止
sudo systemctl stop NetworkManager

# 再度実行
sudo python3 server.py
```

### iptables エラー

```bash
# iptables ルールをリセット
sudo iptables -t nat -F
sudo iptables -F
```

### クリーンアップが必要な場合

スクリプトが異常終了した場合、手動でクリーンアップ:

```bash
# プロセスを停止
sudo pkill hostapd
sudo pkill dnsmasq

# iptables をリセット
sudo iptables -t nat -F
sudo sysctl -w net.ipv4.ip_forward=0

# NetworkManager を再起動
sudo systemctl start NetworkManager
```

---

## 🛡️ 防御策の研究

このツールを使用して、以下の防御策を研究できます:

### ユーザー側の防御

* 信頼できない Wi-Fi ネットワークに接続しない
* VPN を常時使用する
* HTTPS サイトのみ利用する
* 証明書エラーを無視しない
* 公共 Wi-Fi での重要な操作を避ける

### ネットワーク管理者側の防御

* WPA3 暗号化の使用
* 802.1X 認証の実装
* 不正なアクセスポイント検出システムの導入
* クライアント証明書認証
* セキュリティ教育の実施

---

## ✅ 許可された使用範囲

本ソフトウェアは以下の文脈でのみ使用できます:

**許可される用途:**

* 個人の実験環境
* 教育機関のセキュリティ実習室（許可を得た上で）
* 自己所有のデバイスでのテスト
* セキュリティ研究と防御策の開発

**禁止される用途:**

* 無許可のネットワークへの攻撃
* 公共の場所での使用
* 他者のデバイスへの攻撃
* あらゆる悪意ある活動

ユーザーは適用される法律および規制の遵守を確保する全責任を負います。

---

## ⚖️ 法的考慮事項

Evil Twin 攻撃は多くの国で違法です。このツールは以下の条件下でのみ使用してください:

* 自己所有のデバイスとネットワーク
* 書面による明示的な許可がある環境
* 法的に許可された教育機関の実習室
* セキュリティ研究目的で適切な倫理審査を経た研究

無許可での使用は、コンピューター不正アクセス禁止法、電波法、その他の法律に違反する可能性があります。

---

## 🧪 推奨実験環境

* 隔離されたネットワーク環境
* ファラデーケージまたは電波遮蔽室
* VirtualBox/VMware 仮想マシン
* 教育機関の認可されたセキュリティラボ

---

## 📚 参考資料

* Wi-Fi Alliance: https://www.wi-fi.org/
* hostapd Documentation: https://w1.fi/hostapd/
* OWASP Wireless Security: https://owasp.org/www-community/vulnerabilities/

---

## 🌐 教育理念

本プロジェクトは、ネットワークセキュリティの理解を深め、効果的な防御策を開発するための教育リソースとして提供されています。すべての機能は無料で利用でき、教育目的での使用は常に無料です。

---

## ⚠️ 免責事項

本ソフトウェアは教育目的でのみ提供されています。ユーザーは、使用が適用される法律、規制、倫理基準に準拠していることを確保する完全な責任を負います。作成者は本ソフトウェアの誤用、違法使用、または本ソフトウェアの使用によって生じたいかなる損害に対しても一切の責任を負いません。

本ツールの使用は、ユーザー自身のリスクで行ってください。違法行為には使用しないでください。

---

<div align="center">

*ネットワークセキュリティ研究のための教育ツール*

</div>
