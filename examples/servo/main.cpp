# include <ESP32Servo.h>
# include <Arduino.h>

constexpr int Pin1 = 27; // GPIO pin for the servo
constexpr int Pin2 = 32; // GPIO pin for the servo
constexpr int Pin3 = 21; // GPIO pin for the servo
constexpr int Pin4 = 19; // GPIO pin for the servo

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;

int input() {
  if (Serial.available() > 0) {
    char input = Serial.read();   // 1文字読み取る

    if (input == 'c') {
      // 'c'が来たときの処理
      return 180; // 180度に回転
    } else if (input == 'd') {
      // 'd'が来たと0537きの処理
      return 0; // 0度に回転
    } else if (input == 's') {
      // 's'が来たときの処理
      return 90; // 90度に回転
    } else if (input == 'q') {
      // 'q'が来たときの処理
      return 45; // 45度に回転
    } else if (input == 'a') {
      // 'a'が来たときの処理
      return 135; // 135度に回転
    }
  }
  return -1; // 有効な入力がない場合は-1を返す

}

void setup() {
  Serial.begin(115200);
  Serial.println("Hello, world!");

  //PWM を4つ使うことを明示
  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);

  //セットアップ
  servo1.setPeriodHertz(50);// Standard 50hz servo
  servo1.attach(Pin1, 500, 2400);
  servo2.setPeriodHertz(50);// Standard 50hz servo
  servo2.attach(Pin2, 500, 2400);
  servo3.setPeriodHertz(50);// Standard 50hz servo
  servo3.attach(Pin3, 500, 2400);
  servo4.setPeriodHertz(50);// Standard 50hz servo
  servo4.attach(Pin4, 500, 2400);
}

void loop() {
  int val = input();

  if (val < 0) {
    // Serial.println("No input received");
    delay(1000); // wait for a second before checking again
    return; // No valid input, exit the loop
  }

  Serial.print("val1: ");
  Serial.println(val);
  // Serial.print("val2: ");
  // Serial.println(180-val);
  // Serial.print("val3: ");
  // Serial.println(val*2);
  servo1.write(val);
  servo2.write(-val);
  servo3.write(val);
  servo4.write(-val);
  //   delay(500);
  // }
  delay(1000); // wait for a second 
}

