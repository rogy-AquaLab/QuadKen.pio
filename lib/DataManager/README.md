# QuadKen DataManager Library

A template-based data management library for ESP32 projects.

## Features

- Type-safe data management with template support
- Identifier-based data registration and retrieval
- Pack/unpack functionality for network transmission
- Automatic instance management

## Usage

```cpp
#include "QuadKenDataManager.h"

// Create a data manager for float values
Quadken::DataManager<float> sensorData(1, 3); // ID=1, 3 float values

// Update data
std::vector<float> values = {1.5f, 2.3f, 4.7f};
sensorData.update(values);

// Pack for transmission
std::vector<uint8_t> packed = sensorData.pack();

// Unpack received data
std::vector<float> unpacked = Quadken::DataManager<float>::unpack(1, packed);
```
