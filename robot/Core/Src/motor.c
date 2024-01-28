#include "motor.h"

//Timers for: PWM, L/R Encoders
TIM_HandleTypeDef *pwm_tim, *l_enc_tim, *r_enc_tim;

//for tracking encoder data.
uint32_t lCounter = 0, rCounter = 0;
int16_t lCount = 0, rCount = 0;
uint16_t lAngle = 0, rAngle = 0;
uint8_t readL = 0, readR = 0;

//for matching motor speeds.
uint16_t pwmValTarget = 0,
	lPwmVal = 0, rPwmVal = 0;

//error in PID control: deviation from right angle.
//-ve: should increase left, 0: perfect, +ve: should increase right.
float offset = 0;		//-ve: increase left, +ve: increase right.
float error;           // error between target and actual
int32_t error_area = 0;  // area under error - to calculate I for PI implementation
int32_t error_old, error_change;
float error_rate; // to calculate D for PID control
int32_t millisOld, millisNow, dt; // to calculate I and D for PID control
const float Kp = 1;
const float Kd = 0;
const float Ki = 0;

void timer_reset(TIM_HandleTypeDef *htim) {
	__HAL_TIM_SET_COUNTER(htim, 0);
}

void setPwmLR() {
	//set L, R channels.
	__HAL_TIM_SetCompare(pwm_tim, L_CHANNEL, lPwmVal > PWM_MAX ? PWM_MAX
		: lPwmVal < PWM_MIN ? PWM_MIN
		: lPwmVal);
	__HAL_TIM_SetCompare(pwm_tim, R_CHANNEL, rPwmVal > PWM_MAX ? PWM_MAX
			: rPwmVal < PWM_MIN ? PWM_MIN
			: rPwmVal);
}

void resetPwmParams() {
	millisOld = HAL_GetTick();
	error_old = 0;
	offset = 0;
}

void pwmCorrection() {
	//time storage.
	millisNow = HAL_GetTick();
	dt = millisNow - millisOld;
	millisOld = millisNow;

	//error calculation.
	error = (lAngle - rAngle) / 260;
	error_area = error_area + dt * error;
	error_change = error - error_old; // change in error
	error_old = error; //store the error for next round
	error_rate = error_change/dt; // for Kd

	offset += (error*Kp + error_area*Ki + error_rate*Kd); //final offset.

	lPwmVal = pwmValTarget - offset/2;
	rPwmVal = pwmValTarget + offset/2;

	if (lAngle > ANGLE_REFRESH && rAngle > ANGLE_REFRESH) {
		timer_reset(l_enc_tim);
		timer_reset(r_enc_tim);
	}

	setPwmLR();
}

//to pass into HAL_TIM_IC_CaptureCallback for PWM at fixed intervals.
void triggerPwmCorrection() {
	lCounter = __HAL_TIM_GET_COUNTER(l_enc_tim);
	lCount = (int16_t) lCounter;
	lAngle = lCount < 0 ? -(lCount >> 1) : lCount >> 1;

	rCounter = __HAL_TIM_GET_COUNTER(r_enc_tim);
	rCount = (int16_t) rCounter;
	rAngle = rCount < 0 ? -(rCount >> 1) : rCount >> 1;

	pwmCorrection();
}

void motor_init(TIM_HandleTypeDef *pwm, TIM_HandleTypeDef *l_enc, TIM_HandleTypeDef *r_enc) {
	//assign timer pointers.
	pwm_tim = pwm;
	l_enc_tim = l_enc;
	r_enc_tim = r_enc;

	//start Encoders and PWM for L, R motors.
	HAL_TIM_Encoder_Start_IT(l_enc, TIM_CHANNEL_ALL);
	HAL_TIM_Encoder_Start_IT(r_enc, TIM_CHANNEL_ALL);
	HAL_TIM_PWM_Start(pwm, L_CHANNEL);
	HAL_TIM_PWM_Start(pwm, R_CHANNEL);
}

void setDriveDir(uint8_t isForward) {
	//reset counters.
	timer_reset(l_enc_tim);
	timer_reset(r_enc_tim);

	resetPwmParams();

	if (isForward) {
		SET_LIN1();
		RESET_LIN2();
		SET_RIN1();
		RESET_RIN2();
	} else {
		RESET_LIN1();
		SET_LIN2();
		RESET_RIN1();
		SET_RIN2();
	}
}

//speed: 0 - 100
void setDriveSpeed(uint8_t speed) {
	//derive PWM value.
	pwmValTarget = PWM_MAX / 100 * speed;
	if (pwmValTarget > 0) pwmValTarget--;

	lPwmVal = rPwmVal = pwmValTarget;
	resetPwmParams();
	setPwmLR();
}

void getMotorVals(uint16_t *lAnglePtr, uint16_t *rAnglePtr, uint16_t *lPwmValPtr, uint16_t *rPwmValPtr, int32_t *offsetPtr) {
	*lAnglePtr = lAngle;
	*rAnglePtr = rAngle;
	*lPwmValPtr = lPwmVal;
	*rPwmValPtr = rPwmVal;
	*offsetPtr = offset;
}

