#include "oled.h"

void display_init();
void write_motion(float accel[3], float heading, float gyroZ);
void write_motors(uint16_t lAngle, uint16_t rAngle, uint16_t lPwmVal, uint16_t rPwmVal, int32_t offset);
