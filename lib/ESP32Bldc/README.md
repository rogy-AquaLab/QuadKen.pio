# ESP32Bldc (動確済み)
- ESP32Servoライブラリとほぼ同じ使用感のBLDC版
- ESP32Servo同梱のESP32PWMライブラリに依存しているためESP32Servoがないと動かない

- BldcMotor [motor名] で宣言
- [motor名].attach(pin)でピン指定
  - [motor名].config(float pwmFreq, uint8_t pwmResolution , int _zero , int _width) で設定変更
  - デフォルトは frequency(50[Hz]), resolution(10), zero(1490[us]),max(200[us])
- [motor名].setPower(power)で回転速度指定 (power:-1~1)