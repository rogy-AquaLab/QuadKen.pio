# PC <-> RasPi <-> 複数ESP32
### 仮想環境
bleak , opencv-python
### PC <-> RasPi
- asyncioってやつを使ってる。async/await使えてPORTも開けるっぽい
- あんまり理解してないからふわふわコード

### RasPi <-> 複数ESP32
- RasPi側ではbleakなるものを使ってる。async/await使えて複数Bluetooth接続できるっぽい

## テストコード
1. PCで8個のuint8データを作ってRasPiに送り、RasPiがESPに送る
2. ESPがuint8のデータを足したりして、適当な3個のint8のデータを作る
3. ESPからRasPi、RasPiからPCに送る。

- 基本receiveは常に監視、sendは全部数秒おきに送ってる。
- PC、RasPi、ESPがそれぞれuint8×8、int8×3のデータを持ち、それをreceiveで書き換え、sendで取得してる。

## 課題
- 1つでも接続が切れたら、全部再起動(ファイルの再実行)が必要
- ctr+cで実行停止したとき、エラーログが流れる。(理屈が分かってない)
- 時間が余ったらubuntu+ros2もやりたい。けどたぶんできない。
