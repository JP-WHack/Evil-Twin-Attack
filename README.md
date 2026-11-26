# Evil-Twin-Attack

> Evil Twin 攻撃の仕組みを、手を動かして理解するための研究ツール。

`Python`&nbsp;&nbsp;`Linux`&nbsp;&nbsp;`MIT`

───────────────

## Overview

Evil Twin 攻撃の仕組みと防御策を学ぶための教育・研究用ツール。偽の Wi-Fi アクセスポイントと Captive Portal を立て、認証情報が収集される流れを隔離環境で再現する。あくまで防御側の理解を深めるための教材として提供する。

## Features

- 偽アクセスポイントの作成（hostapd）
- Captive Portal（Python HTTPServer）
- DHCP / DNS（dnsmasq）
- 終了時の自動クリーンアップ

## Requirements

- Linux（Debian / Ubuntu / Kali 推奨）
- root 権限
- モニターモード対応の Wi-Fi アダプター
- hostapd, dnsmasq, iptables

## Usage

```bash
sudo apt install -y hostapd dnsmasq iptables
sudo python3 eviltwin.py
```

停止時は Ctrl+C。自動的にクリーンアップが実行される。設定（SSID・チャンネル・ログファイル）はスクリプト先頭の変数で変更する。

## Notice

本ツールは、自分が所有する機器と、書面による明示的な許可を得た隔離環境でのみ使用すること。無許可のネットワークへの使用は多くの国で違法となる。適用される法律・規制の遵守は利用者の責任となる。

### 防御の指針

- 信頼できない Wi-Fi に接続しない、VPN を常用する
- 管理者側は WPA3 / 802.1X 認証、不正 AP 検出の導入を検討する

## License

MIT License — 誰でも自由に利用・改変・再配布できる。詳細は [LICENSE](LICENSE) を参照。

───────────────

<sub>MIT License · JP-WHack</sub>
