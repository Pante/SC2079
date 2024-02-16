#ifndef INC_MOTOR_H_
#define INC_MOTOR_H_

#include "main.h"
#include "pid.h"
#include "convert.h"

//PWM Parameters
#define MOTOR_PWM_PERIOD 7200
#define MOTOR_PWM_MAX 6000 //safe value!
#define MOTOR_PWM_MIN 250 //minimum speed
#define MOTOR_PWM_ACCEL 15
#define MOTOR_BRAKING_DIST_CM 20 //20cm at max speed

//L, R PWM Channels
#define L_CHANNEL TIM_CHANNEL_1
#define R_CHANNEL TIM_CHANNEL_2

void motor_init(TIM_HandleTypeDef *pwm, TIM_HandleTypeDef *l_enc, TIM_HandleTypeDef *r_enc);
float motor_getDist();
void motor_pwmCorrection(int8_t dir, float wDiff, float rBack, float rRobot, float distDiff, float brakingDist);
void motor_setDrive(int8_t dir, uint8_t speed);

#endif /* INC_MOTOR_H_ */
