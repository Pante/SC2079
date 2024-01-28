
#include "ICM20948.h"

#define X 0
#define Y 1
#define Z 2

#define X_HIGH_BYTE 0
#define X_LOW_BYTE 1
#define Y_HIGH_BYTE 2
#define Y_LOW_BYTE 3
#define Z_HIGH_BYTE 4
#define Z_LOW_BYTE 5

#define T_HIGH_BYTE 0
#define T_LOW_BYTE 1

#define ONE_BYTE 8

#define ICM20948_RESET 0x80
#define ICM20948_DISABLE_SENSORS 0x00
#define ICM20948_ENABLE_SENSORS 0x3F
#define ICM20948_AUTO_SELECT_CLOCK 0x01

HAL_StatusTypeDef _ICM20948_SelectUserBank(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, int userBankNum) {
	HAL_StatusTypeDef status = HAL_OK;
	uint8_t writeData = userBankNum << BIT_4;
	uint8_t deviceI2CAddress = (selectI2cAddress == 0)? ICM20948__I2C_SLAVE_ADDRESS_1: ICM20948__I2C_SLAVE_ADDRESS_2;

	status = HAL_I2C_Mem_Write(
			hi2c,
			deviceI2CAddress << 1,
			ICM20948__USER_BANK_ALL__REG_BANK_SEL__REGISTER,
			I2C_MEMADD_SIZE_8BIT,
			&writeData,
			I2C_MEMADD_SIZE_8BIT,
			10);

	return status;
}

HAL_StatusTypeDef _ICM20948_WriteByte(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const registerAddress, uint8_t writeData) {
	HAL_StatusTypeDef status = HAL_OK;
	uint8_t deviceI2CAddress = (selectI2cAddress == 0)? ICM20948__I2C_SLAVE_ADDRESS_1: ICM20948__I2C_SLAVE_ADDRESS_2;

	status = HAL_I2C_Mem_Write(
			hi2c,
			deviceI2CAddress << 1,
			registerAddress,
			I2C_MEMADD_SIZE_8BIT,
			&writeData,
			I2C_MEMADD_SIZE_8BIT,
			10);

	return status;
}

HAL_StatusTypeDef _ICM20948_ReadByte(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const registerAddress, uint8_t * readData) {
	HAL_StatusTypeDef status = HAL_OK;
	uint8_t deviceI2CAddress = (selectI2cAddress == 0)? ICM20948__I2C_SLAVE_ADDRESS_1: ICM20948__I2C_SLAVE_ADDRESS_2;

	status = HAL_I2C_Mem_Read(
			hi2c,
			deviceI2CAddress << 1,
			registerAddress,
			I2C_MEMADD_SIZE_8BIT,
			readData,
			I2C_MEMADD_SIZE_8BIT,
			10);

	return status;
}

HAL_StatusTypeDef _ICM20948_BrustRead(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const startAddress, uint16_t const amountOfRegistersToRead, uint8_t * readData) {
	HAL_StatusTypeDef status = HAL_OK;
	uint8_t deviceI2CAddress = (selectI2cAddress == 0)? ICM20948__I2C_SLAVE_ADDRESS_1: ICM20948__I2C_SLAVE_ADDRESS_2;

	status = HAL_I2C_Mem_Read(
			hi2c,
			deviceI2CAddress << 1,
			startAddress,
			I2C_MEMADD_SIZE_8BIT,
			readData,
			amountOfRegistersToRead * I2C_MEMADD_SIZE_8BIT,
			10);

	return status;
}

HAL_StatusTypeDef _AK09916_WriteByte(I2C_HandleTypeDef * hi2c, uint8_t const registerAddress, uint8_t writeData) {
	HAL_StatusTypeDef status = HAL_OK;

	status = HAL_I2C_Mem_Write(
			hi2c,
			AK09916__I2C_SLAVE_ADDRESS << 1,
			registerAddress,
			I2C_MEMADD_SIZE_8BIT,
			&writeData,
			I2C_MEMADD_SIZE_8BIT,
			10);

	return status;
}

HAL_StatusTypeDef _AK09916_ReadByte(I2C_HandleTypeDef * hi2c, uint8_t const registerAddress, uint8_t *readData) {
	HAL_StatusTypeDef status = HAL_OK;

	status = HAL_I2C_Mem_Read(
			hi2c,
			AK09916__I2C_SLAVE_ADDRESS << 1,
			registerAddress,
			I2C_MEMADD_SIZE_8BIT,
			readData,
			I2C_MEMADD_SIZE_8BIT,
			10);

	return status;
}

HAL_StatusTypeDef _AK09916_BrustRead(I2C_HandleTypeDef * hi2c, uint8_t const startAddress, uint16_t const amountOfRegistersToRead, uint8_t * readData) {
	HAL_StatusTypeDef status = HAL_OK;

	status = HAL_I2C_Mem_Read(
			hi2c,
			AK09916__I2C_SLAVE_ADDRESS << 1,
			startAddress,
			I2C_MEMADD_SIZE_8BIT,
			readData,
			amountOfRegistersToRead * I2C_MEMADD_SIZE_8BIT,
			10);

	return status;
}

uint8_t ICM20948_isI2cAddress1(I2C_HandleTypeDef * hi2c) {
	HAL_StatusTypeDef addressStatus = HAL_I2C_IsDeviceReady(hi2c, ICM20948__I2C_SLAVE_ADDRESS_1 << 1, 2, 10);

	if (addressStatus == HAL_OK) {
		return 1;
	}
	
	return 0;
}

uint8_t ICM20948_isI2cAddress2(I2C_HandleTypeDef * hi2c) {
	HAL_StatusTypeDef addressStatus = HAL_I2C_IsDeviceReady(hi2c, ICM20948__I2C_SLAVE_ADDRESS_2 << 1, 2, 10);

	if (addressStatus == HAL_OK) {
		return 1;
	}
	
	return 0;
}

void ICM20948_init(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const selectGyroSensitivity, uint8_t const selectAccelSensitivity) {
	HAL_StatusTypeDef status = HAL_OK;

	status = _ICM20948_SelectUserBank(hi2c, selectI2cAddress, USER_BANK_0);

	status = _ICM20948_WriteByte(
			hi2c,
			selectI2cAddress,
			ICM20948__USER_BANK_0__PWR_MGMT_1__REGISTER,
			ICM20948_RESET);

	HAL_Delay(200);

	status = _ICM20948_WriteByte(
			hi2c,
			selectI2cAddress,
			ICM20948__USER_BANK_0__PWR_MGMT_1__REGISTER,
			ICM20948_AUTO_SELECT_CLOCK);

	//enable both gyroscope and accelerometer
	status = _ICM20948_WriteByte(
			hi2c,
			selectI2cAddress,
			ICM20948__USER_BANK_0__PWR_MGMT_2__REGISTER,
			ICM20948_DISABLE_SENSORS); // For some reason this needs to be tested

	status = _ICM20948_SelectUserBank(hi2c, selectI2cAddress, USER_BANK_2);

	////temperature configuration.
	//	status = _ICM20948_WriteByte(
	//			hi2c,
	//			selectI2cAddress,
	//			ICM20948__USER_BANK_2__TEMP_CONFIG__REGISTER,
	//			0x03);

	//gyroscope sampling rate settings.
	status = _ICM20948_WriteByte(
			hi2c,
			selectI2cAddress,
			ICM20948__USER_BANK_2__GYRO_CONFIG_1__REGISTER,
			4 << GYRO_DLPFCFG_BIT|selectGyroSensitivity << GYRO_FS_SEL_BIT|EN_GRYO_DLPF << GYRO_FCHOICE_BIT);
	status = _ICM20948_WriteByte(
			hi2c,
			selectI2cAddress,
			ICM20948__USER_BANK_2__GYRO_SMPLRT_DIV__REGISTER,
			4);

	//accelerometer sampling rate settings.
	status = _ICM20948_WriteByte(
			hi2c,
			selectI2cAddress,
			ICM20948__USER_BANK_2__ACCEL_CONFIG__REGISTER,
			4 << ACCEL_DLPFCFG_BIT|selectAccelSensitivity << ACCEL_FS_SEL_BIT|0x01 << ACCEL_FCHOICE_BIT);
	status = _ICM20948_WriteByte(
			hi2c,
			selectI2cAddress,
			ICM20948__USER_BANK_2__ACCEL_SMPLRT_DIV_2__REGISTER,
			4);


	status = _ICM20948_SelectUserBank(hi2c, selectI2cAddress, USER_BANK_0);

	status = _ICM20948_WriteByte(
			hi2c,
			selectI2cAddress,
			ICM20948__USER_BANK_0__INT_PIN_CFG__REGISTER,
			0x02); // Don't understand how this works

	status = _AK09916_WriteByte(
			hi2c,
			AK09916__CNTL2__REGISTER,
			0x08);
}


// moving average trackers.
int16_t gyroZ_a[5];
int16_t accel_a[3][5];
int16_t mag_a[2][5];

float movingAvg(int16_t src, int16_t dst[5]) {
	int32_t total = 0;

	for (int i = 0; i < 4; i++) {
		total += dst[i+1];
		dst[i] = dst[i+1];
	}

	total += dst[4];
	dst[4] = src;

	return ((float) total) / 5;
}

void ICM20948_readGyroscope_Z(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const selectGyroSensitivity, float *gyroZ) {
	uint8_t readData[2];

//	_ICM20948_SelectUserBank(hi2c, selectI2cAddress, USER_BANK_0);
	_ICM20948_BrustRead(hi2c, selectI2cAddress, ICM20948__USER_BANK_0__GYRO_ZOUT_H__REGISTER, 2, readData);

	*gyroZ = movingAvg(readData[0]<<8 | readData[1], gyroZ_a);
	switch (selectGyroSensitivity) {
		case GYRO_FULL_SCALE_250DPS:
			*gyroZ /= GRYO_SENSITIVITY_SCALE_FACTOR_250DPS;
			break;
		case GYRO_FULL_SCALE_500DPS:
			*gyroZ /= GRYO_SENSITIVITY_SCALE_FACTOR_500DPS;
			break;
		case GYRO_FULL_SCALE_1000DPS:
			*gyroZ /= GRYO_SENSITIVITY_SCALE_FACTOR_1000DPS;
			break;
		case GYRO_FULL_SCALE_2000DPS:
			*gyroZ /= GRYO_SENSITIVITY_SCALE_FACTOR_2000DPS;
			break;
	}

}

void ICM20948_readAccelerometer_all(I2C_HandleTypeDef * hi2c, uint8_t const selectI2cAddress, uint8_t const selectAccelSensitivity, float readings[3]) {
	uint8_t readData[6];

//	_ICM20948_SelectUserBank(hi2c, selectI2cAddress, USER_BANK_0);
	_ICM20948_BrustRead(hi2c, selectI2cAddress, ICM20948__USER_BANK_0__ACCEL_XOUT_H__REGISTER, 6, readData);


	float rD[3];
	rD[X] = movingAvg(readData[X_HIGH_BYTE]<<8|readData[X_LOW_BYTE], accel_a[X]);
	rD[Y] = movingAvg(readData[Y_HIGH_BYTE]<<8|readData[Y_LOW_BYTE], accel_a[Y]);
	rD[Z] = movingAvg(readData[Z_HIGH_BYTE]<<8|readData[Z_LOW_BYTE], accel_a[Z]);


	switch (selectAccelSensitivity) {
		case ACCEL_FULL_SCALE_2G:
			readings[X] = rD[X] / ACCEL_SENSITIVITY_SCALE_FACTOR_2G;
			readings[Y] = rD[Y] / ACCEL_SENSITIVITY_SCALE_FACTOR_2G;
			readings[Z] = rD[Z] / ACCEL_SENSITIVITY_SCALE_FACTOR_2G;
			break;
		case ACCEL_FULL_SCALE_4G:
			readings[X] = rD[X] / ACCEL_SENSITIVITY_SCALE_FACTOR_4G;
			readings[Y] = rD[Y] / ACCEL_SENSITIVITY_SCALE_FACTOR_4G;
			readings[Z] = rD[Z] / ACCEL_SENSITIVITY_SCALE_FACTOR_4G;
			break;
		case ACCEL_FULL_SCALE_8G:
			readings[X] = rD[X] / ACCEL_SENSITIVITY_SCALE_FACTOR_8G;
			readings[Y] = rD[Y] / ACCEL_SENSITIVITY_SCALE_FACTOR_8G;
			readings[Z] = rD[Z] / ACCEL_SENSITIVITY_SCALE_FACTOR_8G;
			break;
		case ACCEL_FULL_SCALE_16G:
			readings[X] = rD[X] / ACCEL_SENSITIVITY_SCALE_FACTOR_16G;
			readings[Y] = rD[Y] / ACCEL_SENSITIVITY_SCALE_FACTOR_16G;
			readings[Z] = rD[Z] / ACCEL_SENSITIVITY_SCALE_FACTOR_16G;
			break;
	}
}

void ICM20948_readMagnetometer_XY(I2C_HandleTypeDef * hi2c, float magXY[2]) {
	uint8_t readData[4];
	_AK09916_BrustRead(hi2c, AK09916__XOUT_L__REGISTER, 4, readData);

	//read status register to mark end of data read.
	uint8_t st2;
	_AK09916_ReadByte(hi2c, AK09916__ST2__REGISTER, &st2);

	for (int i = 0; i < 2; i++) magXY[i] = movingAvg(readData[1+2*i]<<8|readData[2*i], mag_a[i]) * MAG_SENSITIVITY_SCALE_FACTOR;
}

