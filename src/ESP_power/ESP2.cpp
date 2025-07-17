#include <Arduino.h>
#include <cstring>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "data_manager.cpp"
#include "ble.cpp"
#include <ESP32Servo.h>
#include "ESP32Bldc.h"

using namespace Quadken;

// Servo array for cleaner code management
constexpr uint8_t SERVO_COUNT = 12;
Servo servos[SERVO_COUNT];

// BLDC motor array for cleaner code management
constexpr uint8_t BLDC_COUNT = 2;
BLDCMotor bldcs[BLDC_COUNT];

DataManager<uint8_t> servo_data(1, 12); // Identifier 1, length 12
DataManager<int8_t> bldc_data(2, 2); // Identifier 2, length 4

constexpr const char* SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab";
constexpr const char* CHARACTERISTIC_UUID = "abcd1234-5678-90ab-cdef-123456789002";

// receiveCallback関数は後で定義
void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data);
BLE ble("ESP32-BLE-Servo2", 
        SERVICE_UUID, 
        CHARACTERISTIC_UUID,
        receiveCallback
);


// Servo pin definitions
constexpr uint8_t servo_pins[SERVO_COUNT] = {
  23, 22, 21, 19, 18, 32,  // servos 1-6
  25, 5, 26, 27, 14, 13    // servos 7-12
};

// BLDC motor pin definitions
constexpr uint8_t bldc_pins[BLDC_COUNT] = {
  2, 4  // BLDC motors 1-2
};




void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data) {
  Serial.print("受信したデータ (ID: ");  Serial.print(identifier);
  Serial.print(") : ");
  Serial.println(data.size());
  for (const auto& byte : data) {
    Serial.print(byte);
    Serial.print(" ");
  }
  DataManager<uint8_t>::unpack(identifier, data);
  Serial.print("受信したデータ (ID: ");
  Serial.print(identifier);
  Serial.print(") : ");
  for (const auto& byte : data) {
    Serial.print(byte);
    Serial.print(" ");
  }
  Serial.println();
  
  if (identifier == 1) {
    // Update servo positions based on received data
    const auto& servo_values = servo_data.get();
    for (uint8_t i = 0; i < SERVO_COUNT && i < servo_values.size(); i++) {
      servos[i].write(servo_values[i]);
    }
    Serial.println("Servos updated");
  }
  else if (identifier == 2) {
    // Update BLDC motor powers based on received data
    const auto& bldc_values = bldc_data.get();
    for (uint8_t i = 0; i < BLDC_COUNT && i < bldc_values.size(); i++) {
      // Convert uint8_t (0-255) to power percentage (-1 to +1)
      float power = bldc_values[i] / 127.5;
      bldcs[i].setPower(power);
    }
    Serial.println("BLDC motors updated");
  }
}

void setup() {
  Serial.begin(115200);

  // Attach all servos to their respective pins and set initial position
  for (uint8_t i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(servo_pins[i]);
    servos[i].write(90); // Set initial position to 90 degrees
  }
  
  // Attach all BLDC motors to their respective pins and configure
  for (uint8_t i = 0; i < BLDC_COUNT; i++) {
    bldcs[i].attach(bldc_pins[i]);
    bldcs[i].config(50.0, 8, 0, 255); // 50Hz, 8-bit resolution, 0-255 range
    bldcs[i].setPower(0.0); // Set initial power to 0%
  }
  
  ble.connect();
  Serial.println("✅ BLE servo & BLDC Test Ready");
}


void loop() {
  // Update bno data
  delay(100);
}

