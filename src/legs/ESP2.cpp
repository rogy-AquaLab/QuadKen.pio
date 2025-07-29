#include <Arduino.h>
#include <cstring>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "QuadKenBLE.h"
#include "QuadKenDataManager.h"
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
DataManager<int8_t> bldc_data(2, 2); // Identifier 2, length 2 (int8_t型に変更)
DataManager<uint8_t> config_data(0xFF, 1); // Config identifier 0xFF, length 1

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

// セットアップ関数の宣言
void setupServos();
void setupBLDCMotors();
void setupAll();
void detachServos();
void detachBLDCMotors();
void detachAll();
void onBLEDisconnected();


// サーボのセットアップ関数
void setupServos() {
  Serial.println("🔄 サーボのセットアップを開始...");
  
  // Attach all servos to their respective pins and set initial position
  for (uint8_t i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(servo_pins[i]);
    servos[i].write(90); // Set initial position to 90 degrees
    Serial.printf("サーボ%d (ピン%d) 初期化完了\n", i+1, servo_pins[i]);
  }
  
  Serial.println("✅ サーボのセットアップ完了");
}

// BLDCモーターのセットアップ関数
void setupBLDCMotors() {
  Serial.println("🔄 BLDCモーターのセットアップを開始...");
  
  // Attach all BLDC motors to their respective pins and configure
  for (uint8_t i = 0; i < BLDC_COUNT; i++) {
    bldcs[i].attach(bldc_pins[i]);
    Serial.printf("BLDCモーター%d (ピン%d) 初期化完了\n", i+1, bldc_pins[i]);
  }
  
  Serial.println("✅ BLDCモーターのセットアップ完了");
}

// 全てのセットアップ関数
void setupAll() {
  setupServos();
  setupBLDCMotors();
}

// サーボのdetach関数
void detachServos() {
  Serial.println("🔄 サーボをdetachしています...");
  
  for (uint8_t i = 0; i < SERVO_COUNT; i++) {
    if (servos[i].attached()) {
      servos[i].detach();
      Serial.printf("サーボ%d (ピン%d) detach完了\n", i+1, servo_pins[i]);
    }
  }
  
  Serial.println("✅ 全サーボのdetach完了");
}

// BLDCモーターのdetach関数
void detachBLDCMotors() {
  Serial.println("🔄 BLDCモーターをdetachしています...");
  
  for (uint8_t i = 0; i < BLDC_COUNT; i++) {
    bldcs[i].setPower(0); // まずパワーを0に設定
    bldcs[i].detach();
    Serial.printf("BLDCモーター%d (ピン%d) detach完了\n", i+1, bldc_pins[i]);
  }
  
  Serial.println("✅ 全BLDCモーターのdetach完了");
}

// 全てのdetach関数
void detachAll() {
  detachServos();
  detachBLDCMotors();
}

// BLE切断時の処理
void onBLEDisconnected() {
  Serial.println("🔴 BLE接続が切断されました - サーボとBLDCモーターをdetachします");
  detachAll();
}




void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data) {
  Serial.print("受信したデータ (ID: ");  Serial.print(identifier);
  Serial.print(") : ");
  Serial.println(data.size());
  for (const auto& byte : data) {
    Serial.print(byte);
    Serial.print(" ");
  }
  DataManager::unpackAny(identifier, data);
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
        setupAll();
      } else if (config_command == 3) {
        // Config 3 command - サーボとBLDCモーター切断
        Serial.println("📨 Config 3 command received - サーボとBLDCモーターを切断します");
        detachAll();
      } else if (config_command == 0) {
        Serial.println("🛑 Shutdown command received");
        detachAll();
      }
    }
  }
  else if (identifier == 1) {
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
      // Convert int8_t (-128~127) to power percentage (-1 to +1)
      float power = bldc_values[i] / 127.0f;
      // Clamp to [-1, 1] range for safety
      if (power > 1.0f) power = 1.0f;
      if (power < -1.0f) power = -1.0f;
      bldcs[i].setPower(power);
      Serial.printf("BLDC%d: raw=%d, power=%.3f\n", i+1, bldc_values[i], power);
    }
    Serial.println("BLDC motors updated");
  }
}

void setup() {
  Serial.begin(115200);

  // 初期状態ではサーボとBLDCのセットアップは行わない
  // configメッセージを待つ
  
  
  // BLE切断時のコールバックを設定
  ble.setDisconnectCallback(onBLEDisconnected);
  
  ble.connect();
  delay(1000); // Wait for BLE connection to stabilize
  Serial.println("✅ BLE接続準備完了 - configメッセージを待機中...");
}


void loop() {
  // Update bno data
  delay(100);
}

