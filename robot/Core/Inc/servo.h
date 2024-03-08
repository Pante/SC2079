#ifndef INC_SERVO_H_
#define INC_SERVO_H_

#include "main.h"
#include "convert.h"

#define SERVO_WIDTH 25.0f //degrees L/R
#define SERVO_TURN_PERIOD 20.0f //ms before turn is updated
#define SERVO_TURN_STEP 3.5f //degrees to turn
#define SERVO_PULSE_L 3600 //-SERVO_WIDTH
#define SERVO_PULSE_0 4850
#define SERVO_PULSE_R 7200 //+SERVO_WIDTH
#define SERVO_PWM_CHANNEL TIM_CHANNEL_1

void servo_init(TIM_HandleTypeDef *pwm);
void servo_setVal(uint32_t val);
void servo_setAngle(float angle);

#endif /* INC_SERVO_H_ */
