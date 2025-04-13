# include <ESP32Servo.h>
# include <Arduino.h>

constexpr int servoPin = 13; // GPIO pin for the servo

Servo servo1;


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
  servo1.attach(servoPin, 500, 2400);
}

void loop() {

  for (int val = 0; val < 180; val += 1) { // Sweep from 0 degrees to 180 degrees
    Serial.printf("val: %d\n", val);
    servo1.write(val); 
    delay(200); 
  }
  delay(1000); // wait for a second 
}

