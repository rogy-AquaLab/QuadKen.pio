#include <Arduino.h>
#include <cstring>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "data_manager.cpp"
#include "ble.cpp"

using namespace Quadken;
#include <ESP32Servo.h>

Servo servo; // Create a Servo object

DataManager<uint8_t> servo_data(1, 8); // Identifier 1, length 8
DataManager<int8_t> bno_data(2, 3); // Identifier 2

constexpr uint8_t SERVO_PIN = 13; // GPIO pin for servo control

#define SERVICE_UUID        "12345678-1234-1234-1234-1234567890ab"
#define CHARACTERISTIC_UUID "abcd1234-5678-90ab-cdef-1234567890cd"


void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data) {
  DataManager<uint8_t>::unpack(identifier, data);
  Serial.print("受信したデータ : ");
  for (const auto& byte : data) {
    Serial.print(byte);
    Serial.print(" ");
  }
  Serial.println();
  servo.write(servo_data.get()[0]); // Set servo position based on received data
}

BLE ble("ESP32-BLE-Servo2", 
        SERVICE_UUID, 
        CHARACTERISTIC_UUID,
        receiveCallback
);

void setup() {
  Serial.begin(115200);

  servo.attach(SERVO_PIN); // Attach the servo to the specified pin
  servo.write(90); // Set initial position to 90 degrees
  
  ble.connect();
  Serial.println("✅ BLE servo Test Ready");
}


void loop() {
  // Update bno data
  delay(100);
}

