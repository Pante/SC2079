#ifndef INC_SENSORS_H_
#define INC_SENSORS_H_

#include "ICM20948.h"
#include "mag_cal.h"
#include <math.h>

#define ICM_I2C_ADDR 0

typedef struct {
	float gyroZ;
	float accel[3];
	float heading;

	float gyroZ_bias;
	float accel_bias[3];
	float heading_bias;
} Sensors;

void sensors_init(I2C_HandleTypeDef *hi2c1_ptr, Sensors *sensors_ptr);
void sensors_read_gyroZ();
void sensors_read_accel();
void sensors_read_heading(float msElapsed);
void sensors_set_bias(uint16_t count);

#endif /* INC_SENSORS_H_ */
