#include "motor.h"

//Timers for: PWM, L/R Encoders
static TIM_HandleTypeDef *motor_pwm_tim, *l_enc_tim, *r_enc_tim;

//for matching motor speeds.
static uint16_t pwmValAccel = 0, pwmValTarget = 0,
	lPwmVal = 0, rPwmVal = 0;

static PidDef pidMatch;
const static float Kp_match = 27;
const static float Ki_match = 0.03;
const static float Kd_match = 0.02;

static PidDef pidDist;
const static float Kp_dist = 0.47;
const static float Ki_dist = 0;
const static float Kd_dist = 0.05;

void motor_init(TIM_HandleTypeDef *pwm, TIM_HandleTypeDef *l_enc, TIM_HandleTypeDef *r_enc) {
	//assign timer pointers.
	motor_pwm_tim = pwm;
	l_enc_tim = l_enc;
	r_enc_tim = r_enc;

	//start Encoders and PWM for L, R motors.
	HAL_TIM_Encoder_Start_IT(l_enc, TIM_CHANNEL_ALL);
	HAL_TIM_Encoder_Start_IT(r_enc, TIM_CHANNEL_ALL);
	HAL_TIM_PWM_Start(pwm, L_CHANNEL);
	HAL_TIM_PWM_Start(pwm, R_CHANNEL);

	//initialize PID values.
	pid_init(&pidMatch, Kp_match, Ki_match, Kd_match);
	pid_init(&pidDist, Kp_dist, Ki_dist, Kd_dist);
}

static void timer_reset(TIM_HandleTypeDef *htim) {
	__HAL_TIM_SET_COUNTER(htim, 0);
}

static void setPwmLR() {
	//set L, R channels.
	__HAL_TIM_SetCompare(motor_pwm_tim, L_CHANNEL,
		lPwmVal > MOTOR_PWM_MAX
		? MOTOR_PWM_MAX
		: lPwmVal);
	__HAL_TIM_SetCompare(motor_pwm_tim, R_CHANNEL,
		rPwmVal > MOTOR_PWM_MAX
		? MOTOR_PWM_MAX
		: rPwmVal);
}

static void resetPwmParams() {
	pid_reset(&pidMatch);
	pid_reset(&pidDist);
}

static void resetEncoders() {
	timer_reset(l_enc_tim);
	timer_reset(r_enc_tim);
}

float motor_getDist() {
	uint32_t lCounter = __HAL_TIM_GET_COUNTER(l_enc_tim),
			rCounter = __HAL_TIM_GET_COUNTER(r_enc_tim);
	int16_t lCount = (int16_t) lCounter,
			rCount = (int16_t) rCounter;
	if (lCount < 0) lCount = -lCount;
	if (rCount < 0) rCount = -rCount;

	uint16_t pulses = ((uint16_t) lCount) + ((uint16_t) rCount);
	pulses >>= 2;

	return get_distance_cm(pulses);
}

//PWM at fixed intervals.
void motor_pwmCorrection(int8_t dir, float wDiff, float distDiff, float brakingDist) {
	//adjust speed based on distance to drive.
	if (distDiff < brakingDist) {
		pwmValAccel = MOTOR_PWM_MIN + pid_adjust(&pidDist, distDiff) / brakingDist * (pwmValTarget - MOTOR_PWM_MIN);
	} else if (pwmValAccel < pwmValTarget) pwmValAccel += MOTOR_PWM_ACCEL;
	if (pwmValAccel > pwmValTarget) pwmValAccel = pwmValTarget;

	float offset = pid_adjust(&pidMatch, wDiff) * pwmValAccel / pwmValTarget;
	if (dir < 0) offset = -offset;

	lPwmVal = pwmValAccel - offset;
	rPwmVal = pwmValAccel + offset;

	setPwmLR();
}

static void setDriveDir(int8_t dir) {
	if (dir > 0) {
		//forward.
		HAL_GPIO_WritePin(MOTORA_IN1_GPIO_Port, MOTORA_IN1_Pin, GPIO_PIN_SET);
		HAL_GPIO_WritePin(MOTORA_IN2_GPIO_Port, MOTORA_IN2_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(MOTORB_IN1_GPIO_Port, MOTORB_IN1_Pin, GPIO_PIN_SET);
		HAL_GPIO_WritePin(MOTORB_IN2_GPIO_Port, MOTORB_IN2_Pin, GPIO_PIN_RESET);
	} else if (dir < 0) {
		//backward.
		HAL_GPIO_WritePin(MOTORA_IN1_GPIO_Port, MOTORA_IN1_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(MOTORA_IN2_GPIO_Port, MOTORA_IN2_Pin, GPIO_PIN_SET);
		HAL_GPIO_WritePin(MOTORB_IN1_GPIO_Port, MOTORB_IN1_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(MOTORB_IN2_GPIO_Port, MOTORB_IN2_Pin, GPIO_PIN_SET);
	} else {
		//full stop.
		HAL_GPIO_WritePin(MOTORA_IN1_GPIO_Port, MOTORA_IN1_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(MOTORA_IN2_GPIO_Port, MOTORA_IN2_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(MOTORB_IN1_GPIO_Port, MOTORB_IN1_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(MOTORB_IN2_GPIO_Port, MOTORB_IN2_Pin, GPIO_PIN_RESET);
	}
}

//speed: 0 - 100
void motor_setDrive(int8_t dir, uint8_t speed) {
	if (dir == 0) {
		setDriveDir(0);
		return;
	}

	//derive PWM value.
	pwmValTarget = MOTOR_PWM_MAX / 100 * speed;
	if (pwmValTarget > 0) pwmValTarget--;

	pwmValAccel = speed > 0
		? MOTOR_PWM_MIN
		: 0;
	lPwmVal = rPwmVal = pwmValAccel;

	//reset.
	resetEncoders();
	resetPwmParams();

	setDriveDir(dir);
	setPwmLR();
}
