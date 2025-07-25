#ifndef QUADKEN_BLE_H
#define QUADKEN_BLE_H

#include <cstring>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <functional>
#include <vector>
#include <Arduino.h>

namespace Quadken {

class BLE {
public:
  using ReceiveCallback = std::function<void(const uint8_t, const std::vector<uint8_t>&)>;

  BLE(const char* deviceName,
      const char* serviceUUID,
      const char* charUUID,
      ReceiveCallback cb)
    : deviceName(deviceName),
      serviceUUID(serviceUUID),
      charUUID(charUUID),
      receiveCallback(cb),
      pCharacteristic(nullptr),
      pServer(nullptr),
      pAdvertising(nullptr) {}

  void connect() {
    BLEDevice::init(deviceName);
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new InternalServerCallbacks(this));

    BLEService* pService = pServer->createService(serviceUUID);

    pCharacteristic = pService->createCharacteristic(
      charUUID,
      BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY
    );

    pCharacteristic->addDescriptor(new BLE2902());
    pCharacteristic->setCallbacks(new InternalCallback(this));

    pService->start();

    pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->start();
  }

  void send(const uint8_t identifier, const std::vector<uint8_t>& data) {
    if (pCharacteristic && !data.empty()) {
      uint8_t* send_data = new uint8_t[data.size() + 1];
      send_data[0] = identifier;
      std::memcpy(send_data + 1, data.data(), data.size());
      pCharacteristic->setValue(send_data, data.size() + 1);
      pCharacteristic->notify();
      delete[] send_data;
    }
  }

private:
  // 受信時の処理
  class InternalCallback : public BLECharacteristicCallbacks {
  public:
    InternalCallback(BLE* wrapper) : wrapper(wrapper) {}
    void onWrite(BLECharacteristic* pChar) override {
      std::string value = pChar->getValue();
      if (value.empty()) return;

      const uint8_t identifier = static_cast<uint8_t>(value[0]);
      std::vector<uint8_t> vec(value.size() - 1);
      std::memcpy(vec.data(), value.data() + 1, value.size() - 1);
      if (wrapper->receiveCallback) {
        wrapper->receiveCallback(identifier, vec);
      }
    }

  private:
    BLE* wrapper;
  };

  // 接続/切断イベント処理
  class InternalServerCallbacks : public BLEServerCallbacks {
  public:
    InternalServerCallbacks(BLE* wrapper) : wrapper(wrapper) {}
    void onConnect(BLEServer* server) override {
    }

    void onDisconnect(BLEServer* server) override {
      delay(100); // 少し待ってから再アドバタイズ
      if (wrapper->pAdvertising) {
        wrapper->pAdvertising->start();
      }
    }

  private:
    BLE* wrapper;
  };

  const char* deviceName;
  const char* serviceUUID;
  const char* charUUID;
  ReceiveCallback receiveCallback;
  BLECharacteristic* pCharacteristic;

  BLEServer* pServer;
  BLEAdvertising* pAdvertising;

  friend class InternalServerCallbacks; // pAdvertisingへアクセスさせる
};

} // namespace Quadken

#endif // QUADKEN_BLE_H
