#ifndef INC_MAG_CAL_H_
#define INC_MAG_CAL_H_

#include <user_input.h>
#include "main.h"
#include "ICM20948.h"
#include "oled.h"

#define MAGCAL_POINTS 100 //points to take along the ellipse.

typedef struct {
	float offset_HI[2];
	float matrix_SI[2][2];
} MagCalParams;

void magcal_init(I2C_HandleTypeDef *hi2c_ptr, MagCalParams *params_ptr);
void magcal_calc_params();
void magcal_adjust(float magXY[2]);

#endif /* INC_MAG_CAL_H_ */
