#ifndef QUADKEN_BLE_H
#define QUADKEN_BLE_H


// #include <Arduino.h>
#include <cstring>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <functional>
#include <vector>


namespace Quadken {

class BLE {
public:
  using ReceiveCallback = std::function<void(const uint8_t , const std::vector<uint8_t>&)>;

  BLE(const char* deviceName,
                   const char* serviceUUID,
                   const char* charUUID,
                   ReceiveCallback cb)
    : deviceName(deviceName),
      serviceUUID(serviceUUID),
      charUUID(charUUID),
      receiveCallback(cb),
      pCharacteristic(nullptr) {}

  void connect() {
    BLEDevice::init(deviceName);
    BLEServer *pServer = BLEDevice::createServer();

    BLEService *pService = pServer->createService(serviceUUID);

    pCharacteristic = pService->createCharacteristic(
      charUUID,
      BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY
    );

    pCharacteristic->setCallbacks(new InternalCallback(this));
    pCharacteristic->addDescriptor(new BLE2902());

    pService->start();
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->start();
  }

  void send(const uint8_t identifier , const std::vector<uint8_t>& data) {
    if (pCharacteristic && !data.empty()) {
      uint8_t* send_data = new uint8_t[data.size() + 1];
      send_data[0] = identifier; // First byte is the data type
      std::memcpy(send_data + 1, data.data(), data.size());
      pCharacteristic->setValue(send_data, data.size() + 1);
      pCharacteristic->notify();
    }
  }

private:
  class InternalCallback : public BLECharacteristicCallbacks {
  public:
    InternalCallback(BLE *wrapper) : wrapper(wrapper) {}
    void onWrite(BLECharacteristic *pChar) override {
      std::string value = pChar->getValue();
      if (value.empty()) {
        return; // No data received
      }
      const uint8_t identifier = static_cast<uint8_t>(value[0]); // First byte is the identifier
      std::vector<uint8_t> vec(value.size()-1);
      std::memcpy(vec.data(), value.data() + 1, value.size() - 1); // Copy the rest of the data
      if (wrapper->receiveCallback) {
        wrapper->receiveCallback(identifier, vec);
      }
    }
  private:
    BLE *wrapper;
  };

  const char* deviceName;
  const char* serviceUUID;
  const char* charUUID;
  ReceiveCallback receiveCallback;
  BLECharacteristic *pCharacteristic;
};
}
#endif // QUADKEN_BLE_H