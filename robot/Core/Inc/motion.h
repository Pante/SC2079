#include "ICM20948.h"

void motion_init(I2C_HandleTypeDef *hi2c1_ptr);
void read_gyroZ(float *gyroZ);
void read_accel(float accel[3]);
void read_heading(float *heading);
void init_bias();
