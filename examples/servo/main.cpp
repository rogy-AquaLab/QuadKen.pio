# include <ESP32Servo.h>
# include <Arduino.h>

constexpr int Pin1 = 13; // GPIO pin for the servo
constexpr int Pin2 = 14; // GPIO pin for the servo
constexpr int Pin3 = 15; // GPIO pin for the servo

Servo servo1;
Servo servo2;
Servo servo3;

void input() {
  if (Serial.available() > 0) {
    char input = Serial.read();   // 1文字読み取る

    if (input == 'c') {
      // 'c'が来たときの処理
      servo3.write(180); // 180度に回転
      Serial.println("Servo 3 is now at 180 degrees.");
    } else if (input == 'd') {
      // 'd'が来たときの処理
      servo3.write(0); // 0度に回転
      Serial.println("Servo 3 is now at 0 degrees.");
    } else if (input == 's') {
      // 's'が来たときの処理
      servo3.write(90); // 90度に回転
      Serial.println("Servo 3 is now at 90 degrees.");
    } else if (input == 'q') {
      // 'q'が来たときの処理
      servo3.write(45); // 45度に回転
      Serial.println("Servo 3 is now at 45 degrees.");
    } else if (input == 'a') {
      // 'a'が来たときの処理
      servo3.write(135); // 135度に回転
      Serial.println("Servo 3 is now at 135 degrees.");
    } else if (input == 'z') {
      // 'z'が来たときの処理
      servo3.write(90); // 90度に回転
      Serial.println("Servo 3 is now at 90 degrees.");
    }
  }
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
}

void loop() {
  input();


  // for (int val = 0; val < 90; val += 10) { // Sweep from 0 degrees to 180 degrees
  //   Serial.print("val1: ");
  //   Serial.println(val);
  //   Serial.print("val2: ");
  //   Serial.println(180-val);
  //   Serial.print("val3: ");
  //   Serial.println(val*2);
  //   servo1.write(val);
  //   servo2.write(180-val);
  //   servo3.write(val*2);
  //   delay(500);
  // }
  delay(1000); // wait for a second 
}

