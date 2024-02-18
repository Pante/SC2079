#include "sensors.h"

static const uint8_t GYRO_SENS = GYRO_FULL_SCALE_250DPS;
static const uint8_t ACCEL_SENS = ACCEL_FULL_SCALE_2G;
static const float a_accel = 0.8;
static const float a_heading = 0.65;
static const float a_mag = 0.9;
static float magOld[2];
static float headingRaw, headingOld;

static float lpf(float a, float old, float new) {
	return a * old + (1 - a) * new;
}

static I2C_HandleTypeDef *hi2c1_ptr;
static Sensors *sensors_ptr;

void sensors_init(I2C_HandleTypeDef *i2c_ptr, Sensors *sens_ptr) {
	hi2c1_ptr = i2c_ptr;
	sensors_ptr = sens_ptr;

	ICM20948_init(hi2c1_ptr, ICM_I2C_ADDR, GYRO_SENS, ACCEL_SENS);
	ICM20948_readMagnetometer_XY(hi2c1_ptr, magOld); //pre-load magOld values.

	sens_ptr->gyroZ_bias = 0;
	sens_ptr->accel_bias[0] = sens_ptr->accel_bias[1] = sens_ptr->accel_bias[2] = 0;
	sens_ptr->heading_bias = 0;
}


void sensors_read_gyroZ() {
	float val;
	ICM20948_readGyroscope_Z(hi2c1_ptr, ICM_I2C_ADDR, GYRO_SENS, &val);
	sensors_ptr->gyroZ = (val - sensors_ptr->gyroZ_bias) / 1000; //convert to ms
}


void sensors_read_accel() {
	float accel_new[3];
	ICM20948_readAccelerometer_all(hi2c1_ptr, ICM_I2C_ADDR, ACCEL_SENS, accel_new);
	for (int i = 0; i < 3; i++) {
//		sensors_ptr->accel[i] = lpf(
//			a_accel,
//			sensors_ptr->accel[i],
//			accel_new[i] - sensors_ptr->accel_bias[i]
//		) * GRAVITY;
		sensors_ptr->accel[i] = (accel_new[i] - sensors_ptr->accel_bias[i]) * GRAVITY;
	}
}

static float read_mag_angle() {
	//Calculate angle from X and Y
	float mag[2];
	ICM20948_readMagnetometer_XY(hi2c1_ptr, mag);
	for (uint8_t i = 0; i < 2; i++) {
		mag[i] = lpf(a_mag, magOld[i], mag[i]);
		magOld[i] = mag[i];
	}
	magcal_adjust(mag);
	return -atan2(mag[1], mag[0]) * 180 / M_PI;
}
void sensors_read_heading(float msElapsed) {
	//complementary fusion.
	sensors_read_gyroZ();
	headingRaw = (1 - a_heading) * (read_mag_angle())
							+ a_heading * (headingOld + sensors_ptr->gyroZ * msElapsed / 1000);

	sensors_ptr->heading = (headingOld + headingRaw) / 2 - sensors_ptr->heading_bias;
	headingOld = headingRaw;

	if (sensors_ptr->heading < -180) sensors_ptr->heading += 360;
	else if (sensors_ptr->heading > 180) sensors_ptr->heading -= 360;
}

void sensors_set_bias(uint16_t count) {
	uint16_t i;
	uint8_t j;
	float gyroZTotal = 0, gyroZ = 0,
		accelTotal[3] = {0}, accel[3],
		headingTotal = 0;

	for (i = 0; i < count; i++) {
		ICM20948_readGyroscope_Z(hi2c1_ptr, ICM_I2C_ADDR, GYRO_SENS, &gyroZ); //gyroscope bias
		gyroZTotal += gyroZ;

		ICM20948_readAccelerometer_all(hi2c1_ptr, ICM_I2C_ADDR, ACCEL_SENS, accel); //accelerometer bias
		for (j = 0; j < 3; j++) accelTotal[j] += accel[j];

		headingTotal += read_mag_angle(); //heading bias
	}

	sensors_ptr->gyroZ_bias = gyroZTotal / count;

	for (i = 0; i < 3; i++) sensors_ptr->accel_bias[i] = accelTotal[i] / count;
	sensors_ptr->accel_bias[2] -= GRAVITY; //normally z accelerometer should read gravity.

	sensors_ptr->heading_bias = headingTotal / count;
}
