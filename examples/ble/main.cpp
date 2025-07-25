#include <Arduino.h>
#include "QuadKenBLE.h"

// 受信データのカウンター
int receivedMessageCount = 0;

// BLE受信コールバック関数
void onBLEReceive(const uint8_t identifier, const std::vector<uint8_t>& data) {
    receivedMessageCount++;
    
    Serial.printf("\n[%d] Received Message:\n", receivedMessageCount);
    Serial.printf("  Identifier: %d\n", identifier);
    Serial.printf("  Data size: %d bytes\n", data.size());
    Serial.print("  Raw data: ");
    
    for (size_t i = 0; i < data.size(); i++) {
        Serial.printf("%02X ", data[i]);
    }
    Serial.println();
    
    // データの内容を文字列として表示（印刷可能な文字のみ）
    Serial.print("  As text: ");
    for (size_t i = 0; i < data.size(); i++) {
        if (data[i] >= 32 && data[i] <= 126) {
            Serial.print((char)data[i]);
        } else {
            Serial.print('.');
        }
    }
    Serial.println();
    
    // エコーバック（受信したデータをそのまま送り返す）
    if (data.size() > 0) {
        // レスポンス用のデータを作成
        std::vector<uint8_t> response;
        response.push_back('O');  // 'O' for OK
        response.push_back('K');
        response.push_back(':');
        response.push_back(' ');
        
        // 元のデータを追加
        for (const auto& byte : data) {
            response.push_back(byte);
        }
        
        // エコーバック送信
        extern Quadken::BLE ble;
        ble.send(identifier + 100, response);  // レスポンス用のIDとして+100
        
        Serial.printf("  Echo sent with ID: %d\n", identifier + 100);
    }
}

// BLEインスタンス
Quadken::BLE ble("QuadKen-BLE-Sample", 
                 "6E400001-B5A3-F393-E0A9-E50E24DCCA9E",  // Nordic UART Service UUID
                 "6E400002-B5A3-F393-E0A9-E50E24DCCA9E",  // TX Characteristic UUID
                 onBLEReceive);

void setup() {
    Serial.begin(115200);
    Serial.println("QuadKen BLE Sample");
    Serial.println("==================");
    Serial.println("This sample demonstrates basic BLE communication.");
    Serial.println("Connect with a BLE client app and send data!");
    Serial.println();
    
    // BLE接続開始
    ble.connect();
    Serial.println("BLE server started and advertising...");
    Serial.println("Device name: QuadKen-BLE-Sample");
    Serial.println("Waiting for client connection...");
}

void loop() {
    static unsigned long lastHeartbeat = 0;
    static unsigned long lastStatusCheck = 0;
    static int heartbeatCounter = 0;
    
    unsigned long now = millis();
    
    // ハートビート送信（10秒毎）
    if (now - lastHeartbeat >= 10000) {
        lastHeartbeat = now;
        heartbeatCounter++;
        
        // ハートビートデータの作成
        String heartbeatMsg = "Heartbeat #" + String(heartbeatCounter) + " at " + String(now);
        std::vector<uint8_t> heartbeatData(heartbeatMsg.begin(), heartbeatMsg.end());
        
        // ハートビート送信（ID: 255）
        ble.send(255, heartbeatData);
        
        Serial.printf("Heartbeat sent #%d\n", heartbeatCounter);
    }
    
    // 接続状態チェック（5秒毎）
    if (now - lastStatusCheck >= 5000) {
        lastStatusCheck = now;
        
        if (ble.isConnected()) {
            Serial.println("Status: BLE client connected");
        } else {
            Serial.println("Status: No BLE client connected");
        }
    }
    
    delay(100);
}
