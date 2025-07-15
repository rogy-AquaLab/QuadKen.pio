# include <ESP32Servo.h>
# include <Arduino.h>

constexpr int Pin1 = 23; // GPIO pin for the servo
constexpr int Pin2 = 22; // GPIO pin for the servo
constexpr int Pin3 = 21; // GPIO pin for the servo
constexpr int Pin4 = 19; // GPIO pin for the servo
constexpr int Pin5 = 18; // GPIO pin for the servo
constexpr int Pin6 = 32; // GPIO pin for the servo
constexpr int Pin7 = 25; // GPIO pin for the servo
constexpr int Pin8 = 5; // GPIO pin for the servo
constexpr int Pin9 = 26; // GPIO pin for the servo
constexpr int Pin10 = 27; // GPIO pin for the servo
constexpr int Pin11 = 14; // GPIO pin for the servo
constexpr int Pin12 = 13; // GPIO pin for the servo

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;
Servo servo7;
Servo servo8;
Servo servo9;
Servo servo10;
Servo servo11;
Servo servo12;

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
	ESP32PWM::allocateTimer(4);
	ESP32PWM::allocateTimer(5);
	ESP32PWM::allocateTimer(6);
	ESP32PWM::allocateTimer(7);
	ESP32PWM::allocateTimer(8);
	ESP32PWM::allocateTimer(9);
	ESP32PWM::allocateTimer(10);
	ESP32PWM::allocateTimer(11);
	ESP32PWM::allocateTimer(12);

  //セットアップ
  servo1.setPeriodHertz(50);// Standard 50hz servo
  servo1.attach(Pin1, 500, 2400);
  servo2.setPeriodHertz(50);// Standard 50hz servo
  servo2.attach(Pin2, 500, 2400);
  servo3.setPeriodHertz(50);// Standard 50hz servo
  servo3.attach(Pin3, 500, 2400);
  servo4.setPeriodHertz(50);// Standard 50hz servo
  servo4.attach(Pin4, 500, 2400);
  servo5.setPeriodHertz(50);// Standard 50hz servo
  servo5.attach(Pin5, 500, 2400);
  servo6.setPeriodHertz(50);// Standard 50hz servo
  servo6.attach(Pin6, 500, 2400);
  servo7.setPeriodHertz(50);// Standard 50hz servo
  servo7.attach(Pin7, 500, 2400);
  servo8.setPeriodHertz(50);// Standard 50hz servo
  servo8.attach(Pin8, 500, 2400);
  servo9.setPeriodHertz(50);// Standard 50hz servo
  servo9.attach(Pin9, 500, 2400);
  servo10.setPeriodHertz(50);// Standard 50hz servo
  servo10.attach(Pin10, 500, 2400);
  servo11.setPeriodHertz(50);// Standard 50hz servo
  servo11.attach(Pin11, 500, 2400);
  servo12.setPeriodHertz(50);// Standard 50hz servo
  servo12.attach(Pin12, 500, 2400);
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
  servo2.write(180-val);
  servo3.write(val);
  servo4.write(180-val);
  servo5.write(val);
  servo6.write(180-val);
  servo7.write(val);
  servo8.write(180-val);
  servo9.write(val);
  servo10.write(180-val);
  servo11.write(val);
  servo12.write(180-val);
  //   delay(500);
  // }
  delay(1000); // wait for a second 
}

