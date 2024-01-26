#include "ICM20948_ADDR.h"
#include "ICM20948_OPTIONS.h"
#include <stdio.h>
#include "stm32f4xx_hal.h"

#define GRYO_SENSITIVITY_SCALE_FACTOR_250DPS 131
#define GRYO_SENSITIVITY_SCALE_FACTOR_500DPS 65.5
#define GRYO_SENSITIVITY_SCALE_FACTOR_1000DPS 32.8
#define GRYO_SENSITIVITY_SCALE_FACTOR_2000DPS 16.4

#define ACCEL_SENSITIVITY_SCALE_FACTOR_2G 16384
#define ACCEL_SENSITIVITY_SCALE_FACTOR_4G 8192
#define ACCEL_SENSITIVITY_SCALE_FACTOR_8G 4096
#define ACCEL_SENSITIVITY_SCALE_FACTOR_16G 2048

#define MAG_SENSITIVITY_SCALE_FACTOR 0.15

HAL_StatusTypeDef _ICM20948_BrustRead(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const startAddress, uint16_t const amountOfRegistersToRead, uint8_t * readData);
HAL_StatusTypeDef _AK09916_WriteByte(I2C_HandleTypeDef * hi2c, uint8_t const registerAddress, uint8_t writeData);
HAL_StatusTypeDef _AK09916_BrustRead(I2C_HandleTypeDef * hi2c, uint8_t const startAddress, uint16_t const amountOfRegistersToRead, uint8_t * readData);

uint8_t ICM20948_isI2cAddress1(I2C_HandleTypeDef * hi2c);
uint8_t ICM20948_isI2cAddress2(I2C_HandleTypeDef * hi2c);

void ICM20948_init(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const selectGyroSensitivity, uint8_t const selectAccelSensitivity);

void ICM20948_readGyroscope_Z(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const selectGyroSensitivity, float *gyroZ);
void ICM20948_readAccelerometer_all(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const selectAccelSensitivity, float readings[3]);
void ICM20948_readMagnetometer_XY(I2C_HandleTypeDef * hi2c, float magXY[2]);
