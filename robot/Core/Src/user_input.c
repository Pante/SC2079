#include "user_input.h"

uint8_t user_is_pressed() {
	return HAL_GPIO_ReadPin(BTN_USER_GPIO_Port, BTN_USER_Pin) != GPIO_PIN_SET;
}
