#include <Arduino.h>

constexpr uint8_t LEDC_CHANNEL = 0;
constexpr uint8_t pin = 13;
constexpr uint8_t cycle = 20;
constexpr uint32_t freqency = 1000 / cycle;
constexpr uint8_t resolution = 15;
constexpr uint32_t max_duty = pow(2.0, resolution);
constexpr int zero_point_on_time = 1477;
constexpr int width = 170;

void bldcSetup(void) {
    int duty = map(100, 0, cycle * 1000, 0, max_duty);
    ledcWrite(LEDC_CHANNEL, duty);
}

void bldcDrive(const int power) {
    int on_time = map(power, -256, 255, zero_point_on_time - width, zero_point_on_time + width); //powerからon_time(us)に変換
    int duty = map(on_time, 0, cycle * 1000, 0, max_duty); //one_time(us)からdutyに変換
    ledcWrite(LEDC_CHANNEL, duty);
    Serial.print("power: ");
    Serial.print(power);
    Serial.print(", on_time: ");
    Serial.print(on_time);
    Serial.print("us, ");
    Serial.print("duty: ");
    Serial.println(duty);
}


void setup(void) {
    Serial.begin(115200);
    Serial.print("max duty:");
    Serial.println(max_duty);
    ledcSetup(LEDC_CHANNEL, freqency, resolution); 
    ledcAttachPin(pin, LEDC_CHANNEL);
    bldcSetup();
    delay(3000);
    for (int i = 0; i < 256; i++) {
        bldcDrive(i);
        delay(50);
    }
    for (int i = 256; i >= 0; i--) {
        bldcDrive(i);
        delay(2);
    }
    bldcDrive(0);
    delay(3000);

    for (int i = 0; i >= -256; i--) {
        bldcDrive(i);
        delay(50);
    }
    for (int i = -256; i <= 0; i++) {
        bldcDrive(i);
        delay(2);
    }
    bldcDrive(0);
}

void loop(void) {
    delay(10);
}