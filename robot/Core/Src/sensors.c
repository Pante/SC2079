#include "sensors.h"

static const uint8_t GYRO_SENS = GYRO_FULL_SCALE_250DPS;
static const uint8_t ACCEL_SENS = ACCEL_FULL_SCALE_2G;
static const float a_irDist = 0.95;
static const float a_usDist = 0.75;
static const float a_accel = 0.8;
static const float a_mag = 0.9;
static float magOld[2];
static float headingRaw, headingOld;

static float lpf(float a, float old, float new) {
	return a * old + (1 - a) * new;
}

static I2C_HandleTypeDef *hi2c_ptr;
static ADC_HandleTypeDef *hadc_ptr;
static TIM_HandleTypeDef *hic_ptr;
static Sensors *sensors_ptr;

static float read_mag_angle() {
	//Calculate angle from X and Y
	float mag[2];
	ICM20948_readMagnetometer_XY(hi2c_ptr, mag);
	for (uint8_t i = 0; i < 2; i++) {
		mag[i] = lpf(a_mag, magOld[i], mag[i]);
		magOld[i] = mag[i];
	}
	magcal_adjust(mag);
	return -atan2(mag[1], mag[0]) * 180 / M_PI;
}

void sensors_init(I2C_HandleTypeDef *i2c_ptr, ADC_HandleTypeDef *adc_ptr, TIM_HandleTypeDef *ic_ptr, Sensors *sens_ptr) {
	hi2c_ptr = i2c_ptr;
	hadc_ptr = adc_ptr;
	hic_ptr = ic_ptr;
	sensors_ptr = sens_ptr;

	ICM20948_init(hi2c_ptr, ICM_I2C_ADDR, GYRO_SENS, ACCEL_SENS);
	ICM20948_readMagnetometer_XY(hi2c_ptr, magOld); //pre-load magOld values.

	HAL_TIM_IC_Start_IT(ic_ptr, US_IC_CHANNEL);

	sens_ptr->gyroZ_bias = 0;
	sens_ptr->accel_bias[0] = sens_ptr->accel_bias[1] = sens_ptr->accel_bias[2] = 0;

	float mag_angle = read_mag_angle();
	sens_ptr->heading_bias = mag_angle;
	angle_init(mag_angle);
}

void sensors_us_trig() {
	US_TRIG_CLR();
	delay_us_wait(5);

	//1. 10us pulse
	US_TRIG_SET();
	delay_us_wait(10);
	US_TRIG_CLR();
}

void sensors_read_usDist(float pulse_s) {
	sensors_ptr->usDist = lpf(a_usDist, sensors_ptr->usDist, pulse_s * 34300 / 2);
}

void sensors_read_irDist() {
	HAL_ADC_Start(hadc_ptr);
	HAL_ADC_PollForConversion(hadc_ptr, HAL_MAX_DELAY);

	uint16_t value = (uint16_t) HAL_ADC_GetValue(hadc_ptr);
	float div = pow(((float) value) / 4095, 1.226);
	float dist = (div < 6.3028 / DIST_IR_MAX)
		? DIST_IR_MAX
		: 6.3028 / div;

	dist -= DIST_IR_OFFSET;
	if (dist < DIST_IR_MIN) dist = DIST_IR_MIN;

	sensors_ptr->irDist = lpf(a_irDist, sensors_ptr->irDist, dist);
}

void sensors_read_gyroZ() {
	float val;
	ICM20948_readGyroscope_Z(hi2c_ptr, ICM_I2C_ADDR, GYRO_SENS, &val);
	sensors_ptr->gyroZ = (val - sensors_ptr->gyroZ_bias) / 1000; //convert to ms
}


void sensors_read_accel() {
	float accel_new[3];
	ICM20948_readAccelerometer_all(hi2c_ptr, ICM_I2C_ADDR, ACCEL_SENS, accel_new);
	for (int i = 0; i < 3; i++) {
		sensors_ptr->accel[i] = (accel_new[i] - sensors_ptr->accel_bias[i]) * GRAVITY;
	}
}

void sensors_read_heading(float msElapsed, float gyroZ) {
	sensors_ptr->heading = angle_diff_180(
		angle_get(msElapsed, gyroZ, read_mag_angle()),
		sensors_ptr->heading_bias
	);
}

void sensors_set_bias(uint16_t count) {
	uint16_t i;
	uint8_t j;
	float gyroZTotal = 0, gyroZ = 0,
		accelTotal[3] = {0}, accel[3],
		headingTotal = 0;

	for (i = 0; i < count; i++) {
		ICM20948_readGyroscope_Z(hi2c_ptr, ICM_I2C_ADDR, GYRO_SENS, &gyroZ); //gyroscope bias
		gyroZTotal += gyroZ;

		ICM20948_readAccelerometer_all(hi2c_ptr, ICM_I2C_ADDR, ACCEL_SENS, accel); //accelerometer bias
		for (j = 0; j < 3; j++) accelTotal[j] += accel[j];

		headingTotal += read_mag_angle(); //heading bias
	}

	sensors_ptr->gyroZ_bias = gyroZTotal / count;

	for (i = 0; i < 3; i++) sensors_ptr->accel_bias[i] = accelTotal[i] / count;
	sensors_ptr->accel_bias[2] -= GRAVITY; //normally z accelerometer should read gravity.

	float heading_bias = headingTotal / count;
	sensors_ptr->heading_bias = heading_bias;
	angle_reset(heading_bias);
}

void sensors_dist_warmup(uint16_t count) {
	for (uint16_t i = 0; i < count; i++) {
		sensors_us_trig();
		sensors_read_irDist();
		HAL_Delay(20);
	}
}
