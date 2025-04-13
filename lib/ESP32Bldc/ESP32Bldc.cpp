#include "ESP32Bldc.h"

BLDCMotor::BLDCMotor() : 
    pinNumber(-1), 
    frequency(50), 
    resolution(10), 
    min(700),
    max(2000)
    {}

int BLDCMotor::attach(int pin)
{
    this->pinNumber = pin;
    pwm.attachPin(this->pinNumber,this->frequency ,this->resolution);   // GPIO pin assigned to channel
    return pwm.getChannel();
}

void BLDCMotor::config(float pwmFreq, uint8_t pwmResolution, int _min, int _max) {
    this->frequency = pwmFreq;
    this->resolution = pwmResolution;
    this->min = _min;
    this->max = _max;
}

void BLDCMotor::detach() {
    if (this->attached())
    {
        //keep track of detached servos channels so we can reuse them if needed
        pwm.detachPin(this->pinNumber);

        this->pinNumber = -1;
    }
}

bool BLDCMotor::attached()
{
    return (pwm.attached());
}

void BLDCMotor::setPower(float power) {
    Serial.println(attached());
    if (!attached()) return;
    if (power < -1) power = -1;
    if (power > 1) power = 1;

    int us = map((int)(power*1000) , -1000, 1000, min, max); // map power to us
    int duty = map(us, 0, 1000000/this->frequency, 0, pow(2,resolution)-1); // map us to duty cycle

    pwm.write(duty); // write duty cycle to PWM channel
    
    Serial.print("power : ");
    Serial.print(power);
    Serial.print("\tus : ");
    Serial.print(us);
    Serial.print("\tduty : ");
    Serial.println(duty);
}


