# QuadKen用platformIOプログラム
- VsCodeの一番下のバーにあるenv:default(QuadKen.pio)から実行ファイルを切り替え
- 今現在書き込んでいるファイルはexamples/ble/ の全部
- pythonディレクトリにラズパイとPCのプログラムを保存
- ディレクトリごとにREADMEを入れてる時がある。

## 問題点
- BNO反応してない
- ESPのBLDC intでできない
- PCのコード見ずらい
- 設定yamlでやりたい
- ラズパイとのBLE、2つないとできない問題

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
