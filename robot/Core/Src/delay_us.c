#include "delay_us.h"

static TIM_HandleTypeDef *htim;

void delay_us_init(TIM_HandleTypeDef *tim_ptr) {
	htim = tim_ptr;
	HAL_TIM_Base_Start(htim);
}

void delay_us_wait(uint16_t us) {
	__HAL_TIM_SET_COUNTER(htim, 0);

	while (__HAL_TIM_GET_COUNTER(htim) < us);
}
