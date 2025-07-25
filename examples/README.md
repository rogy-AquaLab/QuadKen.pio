# QuadKen Library Examples

このディレクトリには、QuadKenプロジェクトで開発されたライブラリのサンプルプログラムが含まれています。

## ライブラリ

### QuadKenDataManager
型安全なデータ管理ライブラリです。テンプレートベースで、さまざまなデータ型に対応しています。

### QuadKenBLE
ESP32用の簡単なBLE通信ライブラリです。コールバックベースでデータの送受信を行えます。

## サンプルプログラム

### 1. datamanager_basic
DataManagerライブラリの基本的な使用方法を示すサンプルです。

**機能:**
- 異なるデータ型（float, int, uint16_t）のDataManagerインスタンス作成
- データの更新と取得
- pack/unpack機能のデモンストレーション

**ビルド方法:**
```bash
pio run -e datamanager_basic_sample
```

### 2. ble_basic
BLEライブラリの基本的な使用方法を示すサンプルです。

**機能:**
- BLEサーバーの開始
- データの送受信
- エコーバック機能
- ハートビート送信

**ビルド方法:**
```bash
pio run -e ble_basic_sample
```

### 3. ble_datamanager
BLEとDataManagerライブラリを組み合わせたサンプルです。

**機能:**
- BLE経由でのデータ送受信
- DataManagerを使用したデータのパック/アンパック
- センサーデータとモーター制御データのシミュレーション

**ビルド方法:**
```bash
pio run -e ble_datamanager_sample
```

## 既存のサンプル

### bldc
- 適当に作ったBLDCライブラリのサンプルコード
- 動作確認済み(サーボとのPWM干渉は未検証)

### ble
- ラズパイとの通信の時にESPに書き込むやつ

## 使用方法

1. VsCodeの下のバーにある「Switch PlatformIO Project Environment」で任意のサンプルを選択
2. ビルドしてESP32にアップロード
3. シリアルモニターで動作を確認
4. BLEサンプルの場合は、BLEクライアントアプリで接続して通信をテストできます

## BLE接続情報

BLEサンプルでは以下の設定を使用しています：

- **ble_basic**: 
  - デバイス名: "QuadKen-BLE-Sample"
  - サービスUUID: "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" (Nordic UART Service)

- **ble_datamanager**:
  - デバイス名: "QuadKen-Sample"
  - サービスUUID: "12345678-1234-1234-1234-123456789abc"

## 推奨BLEクライアントアプリ

- **Android**: nRF Connect for Mobile
- **iOS**: LightBlue Explorer
- **PC**: nRF Connect for Desktop