#include "ESP32Bldc.h"

BLDCMotor::BLDCMotor() : 
    pinNumber(-1), 
    frequency(50), 
    resolution(10), 
    zero(1490),
    width(200)
    {}

int BLDCMotor::attach(int pin)
{
    this->pinNumber = pin;
    pwm.attachPin(this->pinNumber,this->frequency ,this->resolution);
    int init_duty = map(100,  0, 1000000/this->frequency, 0, pow(2,resolution)-1);
    pwm.write(init_duty);

    return pwm.getChannel();
}

void BLDCMotor::config(float pwmFreq, uint8_t pwmResolution, int _zero, int _width) {
    this->frequency = pwmFreq;
    this->resolution = pwmResolution;
    this->zero = _zero;
    this->width = _width;
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
    if (!attached()) return;
    if (power < -1) power = -1;
    if (power > 1) power = 1;

    int us = map((int)(power*1000) , -1000, 1000, zero-width, zero+width); // map power to us
    int duty = map(us, 0, 1000000/this->frequency, 0, pow(2,resolution)-1); // map us to duty cycle

    pwm.write(duty); // write duty cycle to PWM channel
    
    Serial.print("power : ");
    Serial.print(power);
    Serial.print("\tus : ");
    Serial.print(us);
    Serial.print("\tduty : ");
    Serial.println(duty);
}


