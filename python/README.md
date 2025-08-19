# PC <-> RasPi <-> 複数ESP32
## インストール
#### PC側
opencv-python , simple_pid , pygame
#### Rasp側
apt install python3.11-dev build-essential
bleak , opencv-python , Picamera2 , pyyaml , adafruit-circuitpython-busdevice , adafruit-blinka
- Picamera2は仮想環境内にインストールできないため(多分)、ラズパイ本体にインストールして、仮想環境を本体のライブラリも使える状態で立ち上げて使用中

## PC <-> RasPi
- asyncioってやつを使ってる。async/await使えてPORTも開けるっぽい

## RasPi <-> 複数ESP32
- RasPi側ではbleakなるものを使ってる。async/await使えて複数Bluetooth接続できるっぽい
- ラズパイ側から送信するとき送信チェックをしてないため、時々遅れていないかも

## フォルダ
#### test
- サンプルコード置き場、実験用
- Platformio側で使ってるexamplesフォルダと一緒

#### tools
- 自作ライブラリ置き場
- data_managerが今後消えるかも

# 現時点コード説明 7/7
- Raspは受け取ったものをただ流すだけ
- PCでコントローラーの左スティックの角度を検知 -> Rasp -> ESP
- PCのSTART,SELECT,HOMEボタンでESPとの接続を開始したりRaspを停止したりできる(Proコン用として設定)
- ラグはほぼなくなった
- カメラは死んだ

## 今後
- 自動でBLDCオフにす津
- RaspでBNOを取得してPCに送信
- PCで接続状態や機体の角度が一目見てわかるようにGUIを作成
- カメラの蘇生
- PCでESPの状態確認
