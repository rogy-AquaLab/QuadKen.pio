#include <Wire.h>
#include <Adafruit_BNO055.h>

Adafruit_BNO055 bno(55, 0x28);

void setup() {
  Serial.begin(115200);
    Wire.begin(21, 22); // SDA, SCL pins for ESP32
    int retryCount = 5;
    while (!bno.begin() && retryCount > 0) {
        Serial.println("Failed to initialize BNO055, retrying...");
        delay(1000);
        retryCount--;
    }
    if (retryCount == 0) {
        Serial.println("No BNO055 detected after multiple attempts");
    }
    bno.setExtCrystalUse(true);
    // xTaskCreateUniversal(bnoTask, "bno", 8192, NULL, 0, NULL, APP_CPU_NUM);
    
    delay(1000);
}

void loop() {
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  Serial.print("Yaw: ");
  Serial.println(euler.x()); // 軽量読み出し
  delay(1000); // 100Hzまで
}
