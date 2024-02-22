#ifndef INC_SENSORS_H_
#define INC_SENSORS_H_

#include "main.h"
#include "ICM20948.h"
#include "mag_cal.h"
#include <math.h>
#include "delay_us.h"
#include "angle.h"

#define ICM_I2C_ADDR 0
#define GRAVITY 9.80665e-4f //in cm/ms^2
typedef struct {
	float irDist;			//distance from IR sensor.
	volatile float usDist;	//distance from ultrasound sensor.

	float gyroZ;			//gyroscope Z reading.
	float accel[3];			//accelerometer [X, Y, Z] readings.
	float heading;			//heading from -180 to 180 degrees.

	float gyroZ_bias;
	float accel_bias[3];
	float heading_bias;
} Sensors;

#define US_IC_CHANNEL TIM_CHANNEL_1
#define US_TRIG_SET() HAL_GPIO_WritePin(US_TRIG_GPIO_Port,US_TRIG_Pin,GPIO_PIN_SET)
#define US_TRIG_CLR() HAL_GPIO_WritePin(US_TRIG_GPIO_Port,US_TRIG_Pin,GPIO_PIN_RESET)


void sensors_init(I2C_HandleTypeDef *hi2c1_ptr, ADC_HandleTypeDef *adc_ptr, TIM_HandleTypeDef *ic_ptr, Sensors *sensors_ptr);
void sensors_read_irDist();
void sensors_us_trig();
void sensors_read_usDist(float pulse_s);
void sensors_read_gyroZ();
void sensors_read_accel();
void sensors_read_heading(float msElapsed, float gyroZ);
void sensors_set_bias(uint16_t count);
void sensors_dist_warmup(uint16_t count);

#endif /* INC_SENSORS_H_ */
