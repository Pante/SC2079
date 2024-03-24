#include "motor.h"

//Timers for: PWM, L/R Encoders
static TIM_HandleTypeDef *motor_pwm_tim, *l_enc_tim, *r_enc_tim;

//for matching motor speeds.
static int16_t pwmValAccel = 0, pwmValTarget = 0,
	lPwmVal = 0, rPwmVal = 0;
static int16_t lLastCount = 0, rLastCount = 0;
//for bi-directional correction.
static int8_t curDir = 0;

static PidDef pidMatch;
const static float Kp_match = 5e4;
const static float Ki_match = 7e2;
const static float Kd_match = 3e3;

static PidDef pidDistTarget;

const static float Kp_distTarget = 1.1;
const static float Ki_distTarget = 0.0011;
const static float Kd_distTarget = 0.15;

static PidDef pidDistAway;
const static float Kp_distAway = 1.52;
const static float Ki_distAway = 7e-5;
const static float Kd_distAway = 0.25;

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
	pid_init(&pidDistTarget, Kp_distTarget, Ki_distTarget, Kd_distTarget);
	pid_init(&pidDistAway, Kp_distAway, Ki_distAway, Kd_distAway);
}

static void timer_reset(TIM_HandleTypeDef *htim) {
	__HAL_TIM_SET_COUNTER(htim, 0);
}

static void setPwmLR() {
	//set L, R channels.
	__HAL_TIM_SetCompare(motor_pwm_tim, L_CHANNEL,
		lPwmVal > MOTOR_PWM_MAX
		? MOTOR_PWM_MAX
		: lPwmVal < MOTOR_PWM_MIN
		? MOTOR_PWM_MIN
		: lPwmVal);
	__HAL_TIM_SetCompare(motor_pwm_tim, R_CHANNEL,
		rPwmVal > MOTOR_PWM_MAX
		? MOTOR_PWM_MAX
		: rPwmVal < MOTOR_PWM_MIN
		? MOTOR_PWM_MIN
		: rPwmVal);
}

static void resetPwmParams() {
	pid_reset(&pidMatch);
	pid_reset(&pidDistTarget);
	pid_reset(&pidDistAway);
}

static void resetEncoders() {
	timer_reset(l_enc_tim);
	timer_reset(r_enc_tim);

	lLastCount = rLastCount = 0;
}

static int16_t getSpeedPwm(uint8_t speed) {
	int16_t val = MOTOR_PWM_MAX / 100 * speed;

	return val;
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
		HAL_GPIO_WritePin(MOTORA_IN1_GPIO_Port, MOTORA_IN1_Pin, GPIO_PIN_SET);
		HAL_GPIO_WritePin(MOTORA_IN2_GPIO_Port, MOTORA_IN2_Pin, GPIO_PIN_SET);
		HAL_GPIO_WritePin(MOTORB_IN1_GPIO_Port, MOTORB_IN1_Pin, GPIO_PIN_SET);
		HAL_GPIO_WritePin(MOTORB_IN2_GPIO_Port, MOTORB_IN2_Pin, GPIO_PIN_SET);
	}
}

static int16_t getCount(TIM_HandleTypeDef *enc_tim) {
	uint32_t counter = __HAL_TIM_GET_COUNTER(enc_tim);
	return (int16_t) counter;
}

float motor_getDist() {
	int16_t lCount = getCount(l_enc_tim),
			rCount = getCount(r_enc_tim);

	//left motor is opposite in direction to right motor.
	lCount = -lCount;

	int16_t pulses = (lCount + rCount) / 2; //average.
//	if (pulses < 0) pulses = -pulses; //flip.

	return get_distance_cm(pulses);
}

static float motor_getSpeed(TIM_HandleTypeDef *enc_tim, int16_t *lastCount) {
	int16_t count = getCount(enc_tim);
	int16_t diff = abs_int16(count - *lastCount);
	*lastCount = count;
	return (float) diff;
}

//PWM at fixed intervals.
void motor_pwmCorrection(float wDiff, float rBack, float distDiff, float brakingDist, CmdDistType distType, uint8_t speedNext) {
	//adjust speed based on distance to drive.
	if (distDiff < brakingDist) {
		PidDef *pidBrake = distType == TARGET ? &pidDistTarget : &pidDistAway;
		int16_t pwmValNext = getSpeedPwm(speedNext);
		if (pwmValNext < pwmValTarget) {
			 pwmValNext += pid_adjust(pidBrake, distDiff / brakingDist, 1) * (pwmValTarget - pwmValNext);
			 pwmValAccel = pwmValNext;
			 int16_t diff = pwmValNext - pwmValAccel;
			 if (abs_int16(diff) > MOTOR_PWM_ACCEL) {
				 //gently accelerate to intercept.
				 pwmValAccel += diff < 0 ? -MOTOR_PWM_ACCEL : MOTOR_PWM_ACCEL;
			 } else {
				 //allow for change.
				 pwmValAccel += diff;
			 }
		}
	} else if (pwmValAccel < pwmValTarget) pwmValAccel += MOTOR_PWM_ACCEL;
	if (pwmValAccel > pwmValTarget) pwmValAccel = pwmValTarget;

	if (pwmValAccel < 0) {
		setDriveDir(-curDir);
		wDiff = -wDiff;
		pwmValAccel = -pwmValAccel;
	} else {
		setDriveDir(curDir);
	}

	float lScale = 1, rScale = 1;
	if (rBack != 0) {
		float B2 = WHEELBASE_CM_BACK / 2;
		if (rBack < 0) {
			lScale =  (-rBack - B2) / -rBack;
			rScale = (-rBack + B2) / -rBack;
		} else {
			lScale = (rBack + B2) / rBack;
			rScale = (rBack - B2) / rBack;
		}
	}

	float offset = pid_adjust(&pidMatch, wDiff, 1) * pwmValAccel / pwmValTarget;
//	offset = 0;
	if (offset > MOTOR_PWM_OFFSET_MAX) offset = offset < 0 ? -MOTOR_PWM_OFFSET_MAX : MOTOR_PWM_OFFSET_MAX;


	lPwmVal = pwmValAccel * lScale - offset;
	rPwmVal = pwmValAccel * rScale + offset;

	if (lPwmVal > MOTOR_PWM_MAX || rPwmVal > MOTOR_PWM_MAX) {
		float scale;
		if (lPwmVal > rPwmVal) {
			scale = rPwmVal / lPwmVal;
			lPwmVal = MOTOR_PWM_MAX;
			rPwmVal = MOTOR_PWM_MAX * scale;
		} else {
			scale = lPwmVal / rPwmVal;
			lPwmVal = MOTOR_PWM_MAX * scale;
			rPwmVal = MOTOR_PWM_MAX;
		}
	}

	setPwmLR();
}

//speed: 0 - 100
void motor_setDrive(int8_t dir, uint8_t speed) {
	if (dir == 0) {
		setDriveDir(0);
		pwmValAccel = 0;
		return;
	}

	//derive PWM value.
	pwmValTarget = getSpeedPwm(speed);

//	pwmValAccel = speed > 0
//		? MOTOR_PWM_MIN
//		: 0;
//	lPwmVal = rPwmVal = pwmValAccel;

	//reset.
	resetEncoders();
	resetPwmParams();

	curDir = dir;
	setDriveDir(dir);
	setPwmLR();
}
