#include "servo.h"

static TIM_HandleTypeDef *pwm_tim;

#define SERVO_LOOKUP_SIZE 13
static float lookup[13][2] = {
	{-25, 3800},
	{-23, 3850},
	{-21, 3900},
	{-17, 4000},
	{-14, 4200},
	{-8.5, 4350},
	{-7, 4500},
	{0, 4800},
	{2, 5100},
	{7, 5400},
	{11, 5700},
	{16, 6000},
	{22.5, 6300},
	{24, 6600},
	{25, 6900}
};

void servo_init(TIM_HandleTypeDef *pwm) {
	pwm_tim = pwm;
	HAL_TIM_PWM_Start(pwm, SERVO_PWM_CHANNEL);
}

void servo_setVal(uint32_t val) {
	pwm_tim->Instance->CCR1 = val;
}

void servo_setAngle(float angle) {
	//clamp angle to within width.
	uint32_t val = 0;
	if (angle <= -SERVO_WIDTH) val = lookup[0][1];
	else if (angle >= SERVO_WIDTH) val = lookup[SERVO_LOOKUP_SIZE - 1][1];
	else {
		uint8_t i;
		float min_val, max_val;
		float min_angle, max_angle;
		for (i = 0; i < SERVO_LOOKUP_SIZE - 1; i++) {
			min_angle = lookup[i][0];
			max_angle = lookup[i+1][0];
			min_val = lookup[i][1];
			max_val = lookup[i+1][1];

			if (angle >= min_angle && angle <= max_angle) {
				val = min_val + (max_val - min_val) * (angle - min_angle) / (max_angle - min_angle);
				break;
			}
		}
	}

	if (val == 0) val = lookup[SERVO_LOOKUP_SIZE - 1][1];
	servo_setVal(val);
}
