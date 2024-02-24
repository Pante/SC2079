#ifndef INC_SERVO_H_
#define INC_SERVO_H_

#include "main.h"

#define SERVO_WIDTH 25.0f //degrees L/R
#define SERVO_PULSE_L 3600 //-SERVO_WIDTH
#define SERVO_PULSE_0 4850
#define SERVO_PULSE_R 7200 //+SERVO_WIDTH
#define SERVO_PWM_CHANNEL TIM_CHANNEL_1

void servo_init(TIM_HandleTypeDef *pwm);
void servo_setAngle(float angle);

#endif /* INC_SERVO_H_ */
