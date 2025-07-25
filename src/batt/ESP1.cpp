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
DataManager<uint8_t> config_data(0xFF, 1); // Config identifier 0xFF, length 1

constexpr const char *SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab";
constexpr const char *CHARACTERISTIC_UUID = "abcd1234-5678-90ab-cdef-123456789001";

// receiveCallback関数は後で定義
void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data);
BLE ble("ESP32-BLE-Servo1", 
        SERVICE_UUID, 
        CHARACTERISTIC_UUID,
        receiveCallback
);

// GPIO pins for 4 servos
constexpr uint8_t SERVO_PINS[SERVO_COUNT] = {14, 15, 16, 17};

// セットアップ関数の宣言
void setupServos();


// サーボのセットアップ関数
void setupServos() {
  Serial.println("🔄 サーボのセットアップを開始...");
  
  // Attach all servos using for loop
  for (int i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(SERVO_PINS[i]);
    servos[i].write(90); // Set initial position to 90 degrees
    Serial.printf("サーボ%d (ピン%d) 初期化完了\n", i+1, SERVO_PINS[i]);
  }
  
  Serial.println("✅ サーボのセットアップ完了");
}




void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data) {
  DataManager<uint8_t>::unpack(identifier, data);
  Serial.print("受信したデータ (ID: ");
  Serial.print(identifier);
  Serial.print(") : ");
  for (const auto& byte : data) {
    Serial.print(byte);
    Serial.print(" ");
  }
  Serial.println();
  
  if (identifier == 0xFF) {
    // Config message received
    const auto& config_values = config_data.get();
    if (config_values.size() > 0) {
      uint8_t config_command = config_values[0];
      Serial.printf("📨 Config command received: %d\n", config_command);
      
      if (config_command == 1) {
        // Setup command
        setupServos();
      } else if (config_command == 0) {
        Serial.println("🛑 Shutdown command received");
      }
    }
  }
  else if (identifier == 1) {
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
}

void setup() {
  Serial.begin(115200);

  // 初期状態ではサーボのセットアップは行わない
  // configメッセージを待つ
  setupServos();
  ble.connect();
  Serial.println("✅ BLE接続準備完了 - configメッセージを待機中...");
}


void loop() {
  // Update bno data
  delay(100);
}

