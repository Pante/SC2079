#include "main.h"

//PWM Parameters
#define PWM_PERIOD 7200
#define PWM_MAX 6000 //safe value!
#define PWM_MIN 225 //minimum speed
#define ANGLE_REFRESH 10000 //value to refresh angles at

//L: Motor A, R: Motor B
#define SET_LIN1() HAL_GPIO_WritePin(GPIOA, MOTORA_IN1_Pin, GPIO_PIN_SET)
#define SET_LIN2() HAL_GPIO_WritePin(GPIOA, MOTORA_IN2_Pin, GPIO_PIN_SET)
#define RESET_LIN1() HAL_GPIO_WritePin(GPIOA, MOTORA_IN1_Pin, GPIO_PIN_RESET)
#define RESET_LIN2() HAL_GPIO_WritePin(GPIOA, MOTORA_IN2_Pin, GPIO_PIN_RESET)

#define SET_RIN1() HAL_GPIO_WritePin(GPIOA, MOTORB_IN1_Pin, GPIO_PIN_SET)
#define SET_RIN2() HAL_GPIO_WritePin(GPIOA, MOTORB_IN2_Pin, GPIO_PIN_SET)
#define RESET_RIN1() HAL_GPIO_WritePin(GPIOA, MOTORB_IN1_Pin, GPIO_PIN_RESET)
#define RESET_RIN2() HAL_GPIO_WritePin(GPIOA, MOTORB_IN2_Pin, GPIO_PIN_RESET)

//L, R PWM Channels
#define L_CHANNEL TIM_CHANNEL_1
#define R_CHANNEL TIM_CHANNEL_2

void triggerPwmCorrection();
void motor_init(TIM_HandleTypeDef *pwm, TIM_HandleTypeDef *l_enc, TIM_HandleTypeDef *r_enc);
void setDriveDir(uint8_t isForward);
void setDriveSpeed(uint8_t speed);
void getMotorVals(uint16_t *lAnglePtr, uint16_t *rAnglePtr, uint16_t *lPwmValPtr, uint16_t *rPwmValPtr, int32_t *offsetPtr);
