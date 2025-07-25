# QuadKen BLE Library

A simplified BLE communication library for ESP32 projects.

## Features

- Easy BLE server setup
- Callback-based data reception
- Automatic reconnection handling
- Data transmission with identifier support

## Usage

```cpp
#include "QuadKenBLE.h"

// Define callback function
void onReceive(const uint8_t identifier, const std::vector<uint8_t>& data) {
    Serial.printf("Received ID: %d, Size: %d\n", identifier, data.size());
}

// Create BLE instance
Quadken::BLE ble("MyDevice", "12345678-1234-1234-1234-123456789abc", 
                 "87654321-4321-4321-4321-cba987654321", onReceive);

void setup() {
    Serial.begin(115200);
    ble.connect();
}

void loop() {
    // Send data
    std::vector<uint8_t> data = {1, 2, 3, 4};
    ble.send(1, data);
    delay(1000);
}
```
