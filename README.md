# QuadKen用platformIOプログラム
- VsCodeの一番下のバーにあるenv:default(QuadKen.pio)から実行ファイルを切り替え
- 今現在書き込んでいるファイルはexamples/ble/ の全部
- pythonディレクトリにラズパイとPCのプログラムを保存
- ディレクトリごとにREADMEを入れてる時がある。

## 問題点
- ESPのBLDC intでできない
- setup 手動で
- ble datamanager ライブラリ化
- 有線接続の手順説明
- ラズパイのサーボの送信分割雑すぎ-> DataManager分けちゃう
- バラストボタンで制御
- 足とBLDCをアナログで


### platformio.ini
- [esp32dev(defalut)]
  - ビルドファイル：src/main.cpp
  - メイン書き込み

- [Eservo]
  - ビルドファイル：examples/servo/main.cpp
  - servoサンプルコード

- [Ebldc]
  - ビルドファイル：examples/bldc/main.cpp
  - bldcサンプルコード

etc..
