#ifndef INC_CONVERT_H_
#define INC_CONVERT_H_

#include <stdint.h>
#include <math.h>
#include "motor.h"

#define MOTOR_PPR 772 //encoder pulses per revolution
#define WHEEL_R_CM 3.25f
#define CHASSIS_CM 14.5f
#define WHEELBASE_CM 16.2f

uint16_t get_uint16(char *buf, uint16_t size);
uint16_t parse_uint16_t_until(uint8_t **buf_ptr, uint8_t until, uint8_t sizeExpected);
float parse_float_until(uint8_t **buf_ptr, uint8_t until, uint8_t sizeExpected);
float get_turning_r_back_cm(float steeringAngle);
float get_turning_r_robot_cm(float steeringAngle);
float get_w_ms(float speed_cm_ms, float turning_r_robot_cm);
float add_angle(float old, float change);
float angle_diff(float a1, float a2);
float get_distance_cm(uint16_t pulses);

#endif /* INC_CONVERT_H_ */
