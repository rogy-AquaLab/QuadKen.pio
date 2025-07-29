#include <Arduino.h>
#include "QuadKenDataManager.h"

using namespace Quadken;

// 異なる型のDataManagerを作成
DataManager<uint8_t> servo_data(1, 4);     // サーボ用（uint8_t）
DataManager<int8_t> sensor_data(2, 3);        // センサー用（int）
DataManager<float> imu_data(3, 6);         // IMU用（float）

void setup() {
    Serial.begin(115200);
    delay(2000); // シリアル接続の安定化
    Serial.println("ESP32 DataManager Test");
    
    // 初期データ設定
    std::vector<uint8_t> servo_values = {90, 45, 135, 180};
    std::vector<int8_t> sensor_values = {-128, 0, 127};
    std::vector<float> imu_values = {0.1f, 0.2f, 0.3f, 1.0f, 0.0f, 0.0f};
    
    servo_data.update(servo_values);
    sensor_data.update(sensor_values);
    imu_data.update(imu_values);
    
    Serial.println("✅ DataManager initialization complete");
}

void loop() {
    // データをパック
    auto servo_packed = servo_data.pack();
    auto sensor_packed = sensor_data.pack();
    auto imu_packed = imu_data.pack();
    
    Serial.println("--- Packed Data Sizes ---");
    Serial.printf("Servo: %d bytes\n", servo_packed.size());
    Serial.printf("Sensor: %d bytes\n", sensor_packed.size());
    Serial.printf("IMU: %d bytes\n", imu_packed.size());
    
    // 受信データのシミュレーション（汎用unpack使用）
    Serial.println("📦 Testing generic unpack...");
    
    // 型を気にせずデータを更新
    DataManager<uint8_t>::unpackAny(1, servo_packed);
    DataManager<int>::unpackAny(2, sensor_packed);
    DataManager<float>::unpackAny(3, imu_packed);
    
    Serial.println("✅ Generic unpack successful");
    
    // データを取得して表示
    const auto& servo_values = servo_data.get();
    const auto& sensor_values = sensor_data.get();
    const auto& imu_values = imu_data.get();
    
    Serial.print("Servo values: ");
    for (size_t i = 0; i < servo_values.size(); i++) {
        Serial.printf("%d ", servo_values[i]);
    }
    Serial.println();
    
    Serial.print("Sensor values: ");
    for (size_t i = 0; i < sensor_values.size(); i++) {
        Serial.printf("%d ", sensor_values[i]);
    }
    Serial.println();
    
    Serial.print("IMU values: ");
    for (size_t i = 0; i < imu_values.size(); i++) {
        Serial.printf("%.2f ", imu_values[i]);
    }
    Serial.println();
    
    delay(2000);
}