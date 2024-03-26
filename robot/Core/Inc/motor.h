#ifndef INC_MOTOR_H_
#define INC_MOTOR_H_

#include "main.h"
#include "pid.h"
#include "convert.h"
#include "commands.h"

//PWM Parameters
#define MOTOR_PWM_PERIOD 7200
#define MOTOR_PWM_MAX 6000 //safe value!
#define MOTOR_PWM_MIN 375 //minimum speed
#define MOTOR_PWM_ACCEL 20 //maximum change in PWM value allowed (smooth transitioning)
//#define MOTOR_PWM_DECCEL 100 //maximum negative change in PWM value allowed (smooth transitioning)
#define MOTOR_PWM_OFFSET_MAX_PERCENT 0.05f //maximum offset allowed (percentage of target PWM)
#define MOTOR_BRAKING_DIST_CM_TARGET 30.0f //30.0cm at max speed
#define MOTOR_BRAKING_DIST_CM_AWAY 40.0f //40.0cm at max speed
#define MOTOR_CORRECTION_PERIOD 10.0f //correct every 20ms (accumulate encoder)

//L, R PWM Channels
#define L_CHANNEL TIM_CHANNEL_1
#define R_CHANNEL TIM_CHANNEL_2

typedef enum _cmdDistType CmdDistType;

void motor_init(TIM_HandleTypeDef *pwm, TIM_HandleTypeDef *l_enc, TIM_HandleTypeDef *r_enc);
float motor_getDist();
void motor_pwmCorrection(float wDiff, float rBack, float distDiff, float brakingDist, CmdDistType distType, uint8_t speedNext);
void motor_setDrive(int8_t dir, uint8_t speed);

#endif /* INC_MOTOR_H_ */
