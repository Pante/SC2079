#ifndef INC_DELAY_US_H_
#define INC_DELAY_US_H_

#include "main.h"

void delay_us_init(TIM_HandleTypeDef *tim_ptr);
void delay_us_wait(uint16_t us);

#endif /* INC_DELAY_US_H_ */
