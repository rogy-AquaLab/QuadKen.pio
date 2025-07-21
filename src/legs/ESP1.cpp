#include <Arduino.h>
#include <cstring>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "data_manager.cpp"
#include "ble.cpp"
#include <ESP32Servo.h>

using namespace Quadken;

// Create 4 Servo objects as array
constexpr int SERVO_COUNT = 4;
Servo servos[SERVO_COUNT];

DataManager<uint8_t> servo_data(1, 4); // Identifier 1, length 4

constexpr const char *SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab";
constexpr const char *CHARACTERISTIC_UUID = "abcd1234-5678-90ab-cdef-123456789001";

// receiveCallback関数は後で定義
void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data);
BLE ble("ESP32-BLE-Servo4", 
        SERVICE_UUID, 
        CHARACTERISTIC_UUID,
        receiveCallback
);

// GPIO pins for 4 servos
constexpr uint8_t SERVO_PINS[SERVO_COUNT] = {14, 15, 16, 17};




void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data) {
  DataManager<uint8_t>::unpack(identifier, data);
  Serial.print("受信したデータ : ");
  for (const auto& byte : data) {
    Serial.print(byte);
    Serial.print(" ");
  }
  Serial.println();
  
  // Control 4 servos based on received data using for loop
  const auto& servo_positions = servo_data.get();
  if (servo_positions.size() >= SERVO_COUNT) {
    Serial.print("サーボ位置: ");
    for (int i = 0; i < SERVO_COUNT; i++) {
      servos[i].write(servo_positions[i]);
      Serial.printf("S%d=%d ", i+1, servo_positions[i]);
    }
    Serial.println();
  }
}

void setup() {
  Serial.begin(115200);

  // Attach all servos using for loop
  for (int i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(SERVO_PINS[i]);
    servos[i].write(90); // Set initial position to 90 degrees
    Serial.printf("サーボ%d (ピン%d) 初期化完了\n", i+1, SERVO_PINS[i]);
  }
  
  ble.connect();
  Serial.println("✅ BLE 4-Servo Test Ready");
}


void loop() {
  // Update bno data
  delay(100);
}

