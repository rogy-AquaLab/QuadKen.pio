#include <Arduino.h>
#include "QuadKenDataManager.h"

// 異なる型のデータマネージャーを作成
Quadken::DataManager<float> floatData(1, 5);       // 浮動小数点データ
Quadken::DataManager<int> intData(2, 3);           // 整数データ
Quadken::DataManager<uint16_t> sensorData(3, 4);   // センサーデータ

void setup() {
    Serial.begin(115200);
    Serial.println("QuadKen DataManager Sample");
    Serial.println("===========================");
    
    // 初期データの設定
    std::vector<float> initialFloats = {1.1f, 2.2f, 3.3f, 4.4f, 5.5f};
    std::vector<int> initialInts = {10, 20, 30};
    std::vector<uint16_t> initialSensors = {100, 200, 300, 400};
    
    try {
        floatData.update(initialFloats);
        intData.update(initialInts);
        sensorData.update(initialSensors);
        
        Serial.println("Initial data set successfully!");
    } catch (const std::exception& e) {
        Serial.printf("Error setting initial data: %s\n", e.what());
    }
}

void loop() {
    static unsigned long lastUpdate = 0;
    static int counter = 0;
    
    if (millis() - lastUpdate >= 3000) {
        lastUpdate = millis();
        counter++;
        
        Serial.printf("\n--- Update #%d ---\n", counter);
        
        // データの更新
        std::vector<float> newFloats = {
            counter * 1.1f,
            counter * 2.2f,
            counter * 3.3f,
            counter * 4.4f,
            counter * 5.5f
        };
        
        std::vector<int> newInts = {
            counter * 10,
            counter * 20,
            counter * 30
        };
        
        std::vector<uint16_t> newSensors = {
            static_cast<uint16_t>(counter * 100),
            static_cast<uint16_t>(counter * 200),
            static_cast<uint16_t>(counter * 300),
            static_cast<uint16_t>(counter * 400)
        };
        
        try {
            // データ更新
            floatData.update(newFloats);
            intData.update(newInts);
            sensorData.update(newSensors);
            
            // 現在のデータを表示
            Serial.println("Current data:");
            
            auto floats = floatData.get();
            Serial.print("  Float data: ");
            for (size_t i = 0; i < floats.size(); i++) {
                Serial.printf("%.1f ", floats[i]);
            }
            Serial.println();
            
            auto ints = intData.get();
            Serial.print("  Int data: ");
            for (size_t i = 0; i < ints.size(); i++) {
                Serial.printf("%d ", ints[i]);
            }
            Serial.println();
            
            auto sensors = sensorData.get();
            Serial.print("  Sensor data: ");
            for (size_t i = 0; i < sensors.size(); i++) {
                Serial.printf("%u ", sensors[i]);
            }
            Serial.println();
            
            // パック/アンパックのテスト
            Serial.println("\nPack/Unpack test:");
            
            // フロートデータのパック
            auto packedFloat = floatData.pack();
            Serial.printf("  Packed float data size: %d bytes\n", packedFloat.size());
            
            // 新しいインスタンスでアンパック
            auto unpackedFloat = Quadken::DataManager<float>::unpack(1, packedFloat);
            Serial.print("  Unpacked float data: ");
            for (size_t i = 0; i < unpackedFloat.size(); i++) {
                Serial.printf("%.1f ", unpackedFloat[i]);
            }
            Serial.println();
            
            // 整数データのパック
            auto packedInt = intData.pack();
            Serial.printf("  Packed int data size: %d bytes\n", packedInt.size());
            
            auto unpackedInt = Quadken::DataManager<int>::unpack(2, packedInt);
            Serial.print("  Unpacked int data: ");
            for (size_t i = 0; i < unpackedInt.size(); i++) {
                Serial.printf("%d ", unpackedInt[i]);
            }
            Serial.println();
            
        } catch (const std::exception& e) {
            Serial.printf("Error: %s\n", e.what());
        }
        
        // カウンターリセット
        if (counter >= 10) {
            counter = 0;
            Serial.println("\n--- Counter reset ---");
        }
    }
    
    delay(100);
}
