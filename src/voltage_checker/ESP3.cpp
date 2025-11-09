#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "QuadKenBLE.h"
#include "QuadKenDataManager.h"

using namespace Quadken;

// ==================== 設定パラメータ ====================
constexpr int CELL_COUNT = 3;          // 今回は3セル分測定（4セル目はオプション）
constexpr float R_HIGH = 98600.0f;    // 分圧上側抵抗 (例: 100kΩ)
constexpr float R_LOW  = 23600.0f;     // 分圧下側抵抗 (例: 20kΩ)
constexpr float ADC_REF = 2.916f;        // ADC基準電圧
constexpr float ADC_RES = 4095.0f;          // 12bit ADC

// ピン設定（A0～A2を利用）
constexpr int ADC_PINS[CELL_COUNT] = {2, 3, 4};  // XIAO C3 のADC対応ピン

// BLE設定
constexpr const char *SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab";
constexpr const char *CHARACTERISTIC_UUID = "abcd1234-5678-90ab-cdef-123456789003";

DataManager<uint8_t> lipo_data(4, CELL_COUNT);  // ID=4 として登録（セル電圧データ）

void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data);
BLE ble("ESP32C3-BLE-LiPo", SERVICE_UUID, CHARACTERISTIC_UUID, receiveCallback);

// ==================== 関数定義 ====================

// 分圧計算：ADC値 → 実電圧[V]
float adcToVoltage(int raw) {
  float v_adc = (raw / ADC_RES) * ADC_REF;
  float v_batt = v_adc * ((R_HIGH + R_LOW) / R_LOW);
  return v_batt;
}

// BLE受信（今のところ特に処理なし）
void receiveCallback(const uint8_t identifier, const std::vector<uint8_t>& data) {
  Serial.printf("📩 Received (ID=%d): ", identifier);
  for (auto b : data) Serial.printf("%02X ", b);
  Serial.println();
}

// セル電圧の読み取り
void readVoltages() {
  std::vector<uint8_t> voltages;
  voltages.reserve(CELL_COUNT);

  for (int i = 0; i < CELL_COUNT; i++) {
    int raw = analogRead(ADC_PINS[i]);
    float v = adcToVoltage(raw);
    uint8_t v_int = static_cast<uint8_t>(v * 10); // 0.1V単位で格納
    voltages.push_back(v_int);
  }

//   // BLE送信
  lipo_data.update(voltages);
  Serial.printf("data size:%d\n",lipo_data.pack().size());
  ble.send(lipo_data.identifier(),lipo_data.pack());

  // デバッグ出力
  Serial.print("📡 Cell Voltages: ");
  for (uint8_t v : voltages) Serial.printf("%.1fV ", v/10.0f);
  Serial.println();
}
void onBLEDisconnected() {
  Serial.println("🔴 BLE接続が切断されました");
}
// ==================== セットアップ ====================
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("🔋 LiPo電圧監視 BLEデバイス起動");
  ble.setDisconnectCallback(onBLEDisconnected);
  
  ble.connect();
  delay(1000); // Wait for BLE connection to stabilize
  Serial.println("✅ BLE接続準備完了 - configメッセージを待機中...");

  // ADC設定
  for (int i = 0; i < CELL_COUNT; i++) {
    pinMode(ADC_PINS[i], INPUT);
  }
}

// ==================== メインループ ====================
void loop() {
  readVoltages();
  delay(1000);  // 1秒周期で送信
}
