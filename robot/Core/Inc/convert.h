#ifndef INC_CONVERT_H_
#define INC_CONVERT_H_

#include <stdint.h>
#include <math.h>
#include "motor.h"
#include "sensors.h"

#define MOTOR_PPR 1535 //encoder pulses per revolution
#define WHEEL_R_CM 3.25f
#define CHASSIS_CM 15.0f
#define WHEELBASE_CM_FRONT 16.5f
#define WHEELBASE_CM_BACK 16.4f
#define GYRO_CENTER_OFFSET_CM 0.85f //offset of gyro from center of robot.

float abs_float(float a);
float min_float(float a, float b);
float square_float(float a);
float dist_squared(float x1, float x2, float y1, float y2);

uint8_t min_uint8(uint8_t a, uint8_t b);
uint8_t max_uint8(uint8_t a, uint8_t b);
uint8_t lcm_uint8(uint8_t x, uint8_t y);

int16_t abs_int16(int16_t a);

uint16_t get_uint16(char *buf, uint16_t size);
uint16_t parse_uint16_t_until(uint8_t **buf_ptr, uint8_t until, uint8_t sizeExpected);
float parse_float_until(uint8_t **buf_ptr, uint8_t until, uint8_t sizeExpected);
float get_turning_r_back_cm(float steeringAngle);
float get_turning_r_robot_cm(float steeringAngle);
float get_w_ms(float speed_cm_ms, float turning_r);
float get_w_gyro(float speed_cm_ms, float gyro);
float add_angle(float old, float change);
float angle_diff_180(float a1, float a2);
float angle_diff_dir(float a1, float a2, int8_t dir);
float get_distance_cm(int16_t pulses);
float get_arc_length(float angle, float r);

#endif /* INC_CONVERT_H_ */
