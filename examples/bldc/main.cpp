#include <ESP32Bldc.h>
#include <Arduino.h>

constexpr int Pin1 = 13; // GPIO pin for the servo
constexpr int Pin2 = 14; // GPIO pin for the servo
constexpr int Pin3 = 15; // GPIO pin for the servo

BLDCMotor motor1;
BLDCMotor motor2;
BLDCMotor motor3;

void setup() {
    Serial.begin(115200);
    Serial.println("Hello, world!");
  
    //PWM を4つ使うことを明示
    ESP32PWM::allocateTimer(0);
    ESP32PWM::allocateTimer(1);
    ESP32PWM::allocateTimer(2);
    ESP32PWM::allocateTimer(3);
  
    //セットアップ
    motor1.attach(Pin1);
    motor2.attach(Pin2);
    motor3.attach(Pin3);
    // motor1.config(20000, 8, 700, 2000); // Set frequency to 20kHz, resolution to 8 bits, min pulse width to 700us, max pulse width to 2000us}
}
  void loop() {
  
    for (int val = 0; val < 1000; val += 10) { // Sweep from 0 degrees to 180 degrees
        float power = val / 1000.0; // convert to float between 0 and 1
        motor1.setPower(power);
        motor2.setPower(1-power);
        motor3.setPower(-power);
        Serial.print("-------------------------------------");
        delay(2000); 
    }
    delay(1000); // wait for a second 
  }
  