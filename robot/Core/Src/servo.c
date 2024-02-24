#include "servo.h"

static TIM_HandleTypeDef *pwm_tim;

void servo_init(TIM_HandleTypeDef *pwm) {
	pwm_tim = pwm;
	HAL_TIM_PWM_Start(pwm, SERVO_PWM_CHANNEL);
}

static void setServoVal(uint32_t val) {
	pwm_tim->Instance->CCR1 = val;
}

void servo_setAngle(float angle) {
	//clamp angle to within width.
	if (angle < -SERVO_WIDTH) angle = -SERVO_WIDTH;
	else if (angle > SERVO_WIDTH) angle = SERVO_WIDTH;

	uint32_t val;
	if (angle < 0) {
		val = SERVO_PULSE_0 + (SERVO_PULSE_0 - SERVO_PULSE_L) * angle / SERVO_WIDTH;
	} else {
		val = SERVO_PULSE_0 + (SERVO_PULSE_R - SERVO_PULSE_0) * angle / SERVO_WIDTH;
	}

	setServoVal(val);
}
