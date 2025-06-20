#include <Arduino.h>
#include <cstring>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ESP32Servo.h>

Servo servo; // Create a Servo object

BLECharacteristic *pCharacteristic;
bool deviceConnected = false;

constexpr uint8_t SERVO_PIN = 13; // GPIO pin for servo control

#define SERVICE_UUID        "12345678-1234-1234-1234-1234567890ab"
#define CHARACTERISTIC_UUID "abcd1234-5678-90ab-cdef-1234567890ab"

struct data_t {
  uint8_t servo_data[8] = {0}; 
  int8_t bno_data[3] = {0};
}data;

class MyCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pChar) {
    std::string received = pChar->getValue();
    if (received.length() != 8) {
      Serial.println("Invalid data length");
      return;
    }
    Serial.print("From Raspberry Pi (uint8): ");
    for (int i = 0; i < 8; i++) {
      data.servo_data[i] = (uint8_t)received[i];
      Serial.print(data.servo_data[i]);
      Serial.print(" , ");
    }
    Serial.println();
  }
};

void setup() {
  Serial.begin(115200);

  servo.attach(SERVO_PIN); // Attach the servo to the specified pin
  servo.write(90); // Set initial position to 90 degrees
  
  BLEDevice::init("ESP32-BLE-Servo2");

  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY
  );

  pCharacteristic->setCallbacks(new MyCallbacks());
  pCharacteristic->addDescriptor(new BLE2902());
  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->start();

  Serial.println("✅ BLE servo Test Ready");
}


void loop() {
  data.bno_data[0] = data.servo_data[0]+data.servo_data[1];
  data.bno_data[1] = data.servo_data[2]+data.servo_data[3];
  data.bno_data[2] = data.servo_data[4]+data.servo_data[5];
  Serial.print("BNO Data (int8) : ");
  for (int i = 0; i < 3; i++) {
    Serial.print(data.bno_data[i]);
    Serial.print(" , ");
  }
  Serial.println();
  uint8_t send_data[3];
  std::memcpy(send_data, data.bno_data, sizeof(data.bno_data));
  Serial.println();
  pCharacteristic->setValue(send_data,3);
  pCharacteristic->notify();

  servo.write(data.servo_data[0]); // Set servo position based on received data
  Serial.print("Servo Position: ");
  
  delay(100);
}
