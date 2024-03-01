#include "motion.h"
#include <math.h>

#define I2C_ADDR 0

const uint8_t GYRO_SENS = GYRO_FULL_SCALE_2000DPS;
const uint8_t ACCEL_SENS = ACCEL_FULL_SCALE_2G;

I2C_HandleTypeDef *hi2c1_ptr;
volatile int16_t gyroZ_raw;
volatile float accel_raw[3];
volatile int16_t magZ_raw;

//bias.
float accel_bias[3];
volatile float heading_bias;

void motion_init(I2C_HandleTypeDef *i2c_ptr) {
	hi2c1_ptr = i2c_ptr;
	ICM20948_init(hi2c1_ptr, I2C_ADDR, GYRO_SENS, ACCEL_SENS);
}


void read_gyroZ(float *gyroZ) {
	ICM20948_readGyroscope_Z(hi2c1_ptr, I2C_ADDR, GYRO_SENS, gyroZ);
}


void read_accel(float accel[3]) {
	ICM20948_readAccelerometer_all(hi2c1_ptr, I2C_ADDR, ACCEL_SENS, accel);
	for (int i = 0; i < 3; i++) accel[i] -= accel_bias[i];
}

float read_mag() {
	//Calculate angle from X and Y
	float xy[2];
	ICM20948_readMagnetometer_XY(hi2c1_ptr, xy);
	return atan2(xy[1], xy[0]) * 180 / M_PI;
}
void read_heading(float *heading) {
	*heading = read_mag() - heading_bias;
	if (*heading < 0) *heading += 360;
}

void init_bias() {
	for (int i = 0; i < 500; i++) {
		ICM20948_readAccelerometer_all(hi2c1_ptr, I2C_ADDR, ACCEL_SENS, accel_bias); //accelerometer bias
		heading_bias = read_mag(); //heading bias
	}
}
