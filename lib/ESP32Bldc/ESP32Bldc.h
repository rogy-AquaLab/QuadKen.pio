#ifndef ESP32BLDC_H
#define ESP32BLDC_H

#include <Arduino.h>
#include <ESP32PWM.h>

class BLDCMotor {
private:
    int pinNumber;
    float frequency;
    uint8_t resolution;
    uint8_t channel;
    int zero;
    int width;

    ESP32PWM * getPwm(); // get the PWM object
	ESP32PWM pwm;
public:
    BLDCMotor();

    int attach(int pin);
    void config(float pwmFreq, uint8_t pwmResolution , int _zero , int _width);
    void detach();
    bool attached();

    void setPower(float power);
};

#endif // ESP32BLDC_H