# include <ESP32Servo.h>
# include <Arduino.h>

Servo servo1;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("Hello, world!");
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println("servo");
  delay(1000); // wait for a second 
}

