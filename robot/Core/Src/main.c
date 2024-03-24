/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdlib.h>
#include <math.h>
#include "convert.h"
#include "commands.h"
#include "dist.h"
#include "angle.h"
#include "delay_us.h"
#include "oled.h"
#include "sensors.h"
#include "motor.h"
#include "servo.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
//8MHz / 16000 = 2.0ms frame.
#define MS_FRAME 2.0f
#define SERIAL_BUF_SIZE 20
#define SERIAL_RING_SIZE 1000
#define DIST_DIFF_DEFAULT 50
#define BRAKE_SPEED 20
#define TICKS_ES_MAX 8
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
ADC_HandleTypeDef hadc2;

I2C_HandleTypeDef hi2c1;

TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim4;
TIM_HandleTypeDef htim6;
TIM_HandleTypeDef htim7;
TIM_HandleTypeDef htim8;

UART_HandleTypeDef huart3;

/* USER CODE BEGIN PV */
//sensors variables.
Sensors sensors;
MagCalParams magCalParams;

//serial buffers.
volatile uint16_t ring_i = 0, track_i = 0;
uint16_t buf_i = 0;

uint8_t buf_serial[SERIAL_BUF_SIZE];
uint8_t ring_serial[SERIAL_RING_SIZE];

//ultrasound pulse width measurement.
volatile uint8_t isRisingCaptured = 0;
volatile uint8_t usCaptureComplete = 0;
volatile uint16_t usWrap = 0;
volatile uint32_t counter;

//paced loop.
volatile uint8_t newTick = 0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART3_UART_Init(void);
static void MX_I2C1_Init(void);
static void MX_TIM8_Init(void);
static void MX_TIM2_Init(void);
static void MX_TIM3_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM4_Init(void);
static void MX_ADC1_Init(void);
static void MX_TIM6_Init(void);
static void MX_TIM7_Init(void);
static void MX_ADC2_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

//increment index in a ring.
static void serial_inc_ring(volatile uint16_t *i) {
	*i = (*i + 1) % SERIAL_RING_SIZE;
}

//serial in.
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
	serial_inc_ring(&ring_i);
	HAL_UART_Receive_IT(&huart3, &ring_serial[ring_i], 1);
}

/* --- Start: Timer Management --- */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
	if (htim == &htim4) {
		usWrap++;
	}

	else if (htim == &htim7) {
		newTick = 1;
	}
}
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
	if (htim != &htim4) return;

	if (!isRisingCaptured) {
		//rising edge
		usCaptureComplete = 0;

		usWrap = 0;
		__HAL_TIM_SET_COUNTER(htim, 0);

		isRisingCaptured = 1;
		__HAL_TIM_SET_CAPTUREPOLARITY(htim, US_IC_CHANNEL, TIM_INPUTCHANNELPOLARITY_FALLING);
	} else {
		//falling edge
		counter = HAL_TIM_ReadCapturedValue(htim, US_IC_CHANNEL);
		counter += usWrap * 65536;
		sensors_read_usDist((float) counter * 1e-6);

		isRisingCaptured = 0;
		__HAL_TIM_SET_CAPTUREPOLARITY(htim, US_IC_CHANNEL, TIM_INPUTCHANNELPOLARITY_RISING);

		usCaptureComplete = 1;
	}
}
/* --- End: Timer Management --- */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */
  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART3_UART_Init();
  MX_I2C1_Init();
  MX_TIM8_Init();
  MX_TIM2_Init();
  MX_TIM3_Init();
  MX_TIM1_Init();
  MX_TIM4_Init();
  MX_ADC1_Init();
  MX_TIM6_Init();
  MX_TIM7_Init();
  MX_ADC2_Init();
  /* USER CODE BEGIN 2 */

  /* ----- Start: Initialize libraries ----- */
  OLED_Init();												//initialize OLED display.
  magcal_init(&hi2c1, &magCalParams);						//initialize magnetometer calibration.
  sensors_init(&hi2c1, &hadc1, &hadc2, &htim4, &sensors); 	//initialize motion sensors.
  motor_init(&htim8, &htim2, &htim3); 						//initialize motor PWM and encoders.
  servo_init(&htim1); 										//initialize servo PWM.
  delay_us_init(&htim6);									//initialize us timer.

  dist_init();												//initialize distance tracking.
  /* ----- End: Initialize libraries ----- */

  /* ----- Start: Car setup ----- */
//  magcal_calc_params();

  //reset car.
  servo_setAngle(0);
  motor_setDrive(0, 0);

//  OLED_ShowString(0, 0, "Press USER when ready...");
//  OLED_Refresh_Gram();
//  while (!user_is_pressed());	//wait for user to place car.
  HAL_Delay(500);
  OLED_Clear();
  OLED_ShowString(0, 0, "Calibrating...");
  OLED_Refresh_Gram();

  sensors_set_bias(500); 		// set initial bias.

  OLED_ShowString(0, 0, "Calibration done.");
  OLED_Refresh_Gram();

  /* ----- End: Car setup ----- */

  /* ----- Start: OS Parameters ----- */
  //ticking for longer timing requirements for ultrasound, and servo turning.
  uint8_t ticksElapsed = 0,
		  ticksUsElapsed = 0,
		  ticksUs = (uint8_t) (US_MIN_DELAY / MS_FRAME) + 1,
		  ticksServo = (uint8_t) (SERVO_TURN_PERIOD / MS_FRAME),
		  ticksServoFull = (uint8_t) (SERVO_TURN_PERIOD * SERVO_WIDTH / SERVO_TURN_STEP) / MS_FRAME,
		  ticksMotor = (uint8_t) (MOTOR_CORRECTION_PERIOD / MS_FRAME),
		  ticksRefresh = lcm_uint8(lcm_uint8(ticksUs, ticksServo), ticksMotor),
		  ticksDelay = ticksServoFull - 1;

  //ticking for error stabilization.
  uint8_t ticksES = 0;

  Command *cmd = NULL;							//current command.
  float steeringAngle = 0;						//current steering angle.
  float motorDist = 0, estDist = 0,
		  estAngle = 0,
		  estDistOld = 0; 						//distance estimations.

  //for distance tracking (for use with INFO_DIST command).
  float distTrack = 0;
  uint8_t shouldTrackDist = 0;

  float distTarget = 0;							//decide distance target.
  float distDiff = 0, brakingDist = 0; 			//current distance difference.
  float distDiffOld = 0;						//track old distance difference (to see if stationary).
  float wDiff = 0, wTarget = 0;					//current angular velocity difference and target.
  float rBack = 0, rRobot = 0;					//turning radii at the back and centre of robot.
  /* ----- End: OS Parameters ----- */

  /* ----- Start: Interrupts ----- */
  HAL_UART_Receive_IT(&huart3, &ring_serial[ring_i], 1);	//start receiving serial.
  HAL_TIM_Base_Start_IT(&htim7);							//start paced loop timer.
  /* ----- End: Interrupts ----- */

  OLED_Clear();
  OLED_ShowString(0, 0, "Active.");
  OLED_Refresh_Gram();

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
	/* ----- Start: Sensor reading ----- */
	//trigger distance measurement.
	if (!(ticksElapsed % ticksUs)) {
		sensors_us_trig();
	}

	sensors_read_accel();
	sensors_read_gyroZ();
	sensors_read_irDist();
	/* ----- End: Sensor reading ----- */

	/* ----- Start: Get next command (if any) ----- */
	if (cmd == NULL) {
		if (!ticksDelay) {
			cmd = commands_pop();

			if (cmd != NULL) {
				//perform command setup based on
				switch (cmd->opType) {
					case DRIVE:
						estDistOld = 0;
						estAngle = 0;
						motor_setDrive(cmd->dir, cmd->speed);
						if (cmd->dir != 0) {
							distTarget = cmd->val;
							distDiff = DIST_DIFF_DEFAULT;
							brakingDist = (cmd->distType == TARGET
								? MOTOR_BRAKING_DIST_CM_TARGET
								: MOTOR_BRAKING_DIST_CM_AWAY
							) * cmd->speed / 100;


							steeringAngle = cmd->steeringAngle;
							servo_setAngle(steeringAngle);
							if (steeringAngle != 0) {
								rBack = get_turning_r_back_cm(steeringAngle);
								rRobot = get_turning_r_robot_cm(steeringAngle);
								if (cmd->distType == TARGET) {
									distTarget = abs_float(get_arc_length(cmd->val, rBack));
								}
							} else {
								rBack = 0;
								rRobot = 0;
								wTarget = 0;
							}
						} else {
							commands_end(&huart3, cmd);
							cmd = NULL;
						}
						break;

					case INFO_DIST:
						shouldTrackDist = !shouldTrackDist;
						if (shouldTrackDist) {
							distTrack = 0;
						} else {
							//write distance tracked into string.
							free(cmd->str);
							cmd->str_size = 8; //D<6.2f>\n = 8 characters
							cmd->str = malloc(cmd->str_size * sizeof(uint8_t));
							snprintf(cmd->str, cmd->str_size, "D%6.2f\n", distTrack);
						}

						commands_end(&huart3, cmd);
						cmd = NULL;
						break;
				}
			}
		} else {
			Command *peek = commands_peek_next_drive();
			if (peek != NULL) {
				servo_setAngle(peek->steeringAngle);
				if (ticksDelay > 0) ticksDelay--;
			}
		}
	}

	/* ----- End: Get next command (if any) ----- */

	/* ----- Start: Command Control Loop ----- */
	if (cmd != NULL && cmd->dir != 0) {
		//calculate distance.
		motorDist = motor_getDist();
		estDist = cmd->dir * dist_get_cm(MS_FRAME, sensors.accel[1], motorDist);

		//estimate current speed.
		float estSpeed = (estDist - estDistOld) / MS_FRAME;
		estDistOld = estDist;

		//calculate difference in angular velocity.
		float wGyro;
		wGyro = cmd->dir * sensors.gyroZ;

		if (rBack != 0) {
			wTarget = get_w_ms(estSpeed, rBack);
		}
		else wTarget = 0;
		wDiff = (wGyro - wTarget); //gyro is flipped when going backwards.

		float angleChange = wGyro * MS_FRAME;
		if (cmd->steeringAngle < 0) angleChange = -angleChange;
		estAngle += angleChange;

		distDiffOld = distDiff;
		switch (cmd->distType) {
			case TARGET:
				if (rBack != 0) {
					distDiff = get_arc_length(cmd->val - estAngle, abs_float(rBack));
				} else {
					distDiff = distTarget - estDist;
				}
				break;
			case STOP_AWAY:
				if (usCaptureComplete) {
					distDiff = (sensors.usDist - cmd->val) * cmd->dir;
				}
				break;
			case STOP_L:
			case STOP_R:
				uint8_t i = cmd->distType == STOP_L ? 0 : 1;
				float irVal = sensors.irDist[i];
				float cmdVal = cmd->val;
				if (cmdVal < 0) {
					cmdVal = -cmdVal;
					distDiff = irVal > cmdVal ? DIST_DIFF_DEFAULT : 0;
				} else {
					distDiff = irVal < cmdVal ? DIST_DIFF_DEFAULT : 0;
				}
				break;
			default:
				distDiff = DIST_DIFF_DEFAULT;
				break;
		}

		Command *next = commands_peek_next_drive();
		if (next != NULL) {
			if (commands_type_match(cmd, next)) {
				//absorb next command into current command.
				next = commands_pop();

				switch (next->distType) {
					case TARGET:
						cmd->val += next->val;
						break;
					case STOP_AWAY:
						cmd->val = next->val;
						break;
				}

				commands_end(&huart3, next);
				next = commands_peek_next_drive();
			}
		}

		float nextAngle = next != NULL ? next->steeringAngle : 0;
		float nextAngleDiff = abs_float(nextAngle - cmd->steeringAngle);
		uint8_t shouldBrake = cmd->distType == STOP_AWAY
				? 1
				: next != NULL
				? next->dir != cmd->dir
//					|| next->dir < 0 //avoid smooth turning while reversing.
					|| nextAngleDiff > SERVO_WIDTH
				: 1;
		uint8_t turnSpeed = next != NULL ? min_uint8(BRAKE_SPEED, next->speed) : BRAKE_SPEED;

		//motor correction.
		motor_pwmCorrection(
			wDiff, rBack, distDiff,
			brakingDist, cmd->distType,
			shouldBrake ? 0 : turnSpeed
		);

		float timeLeft = estSpeed > 0 ? distDiff / estSpeed : 1e10;

		uint8_t shouldEnd = 0;
		if (!shouldBrake && !(ticksElapsed % ticksServo)) {
			//turn a small angle every SERVO_TURN_PERIOD ms.
			float diff = abs_float(steeringAngle - next->steeringAngle);
			if (diff < 0.01) shouldEnd = 1;
			else if (timeLeft < (SERVO_TURN_PERIOD) * (diff / SERVO_TURN_STEP)) {
				//should increment.
				float step = min_float(SERVO_TURN_STEP, diff);
				if (nextAngle < steeringAngle) step = -step;
				steeringAngle += step;
				servo_setAngle(steeringAngle);

				if (diff < SERVO_TURN_STEP) {
					shouldEnd = 1;
				}
			}
		}

		float absDistDiff = abs_float(distDiff),
				absDistDiffChange = abs_float(distDiff - distDiffOld);

		if (shouldEnd || absDistDiff < 0.05 || (shouldBrake && absDistDiff < 1.0 && absDistDiffChange < 0.25)) {
			//check for stabilization (if not in continuous motion).
			if (shouldEnd || !shouldBrake || ++ticksES >= TICKS_ES_MAX) {
				//target achieved; move to next command.
				ticksES = 0;
				commands_end(&huart3, cmd);
				cmd = NULL;

				servo_setAngle(nextAngle);
				if (shouldBrake) {
					ticksDelay = (SERVO_TURN_PERIOD / MS_FRAME) * (abs_float(nextAngle - steeringAngle) / SERVO_TURN_STEP);
					motor_setDrive(0, 0);
					dist_reset(0);
				} else dist_reset(estSpeed);

				//add estimated travel distance to tracking distance (if tracked).
				if (shouldTrackDist) distTrack += estDist;
			}
		} else {
			ticksES = 0;
		}
	}
	/* ----- End: Command Control Loop ----- */

	/* ----- Start: Paced Loop Control ----- */
	while (!newTick) {									//wait for new tick.
		/* ----- Start: Process Ring Buffer ----- */
		/* We use the down time for paced looping to process commands. */
		if (track_i != ring_i) {
			uint8_t c = ring_serial[track_i];
			buf_serial[buf_i++] = c;
			if (c == CMD_END) {
				uint8_t *temp = buf_serial;
//				float angle = parse_float_until(&temp, CMD_END, 4);
//				servo_setAngle(angle);
				commands_process(&huart3, buf_serial, buf_i);
				buf_i = 0;
			}

			serial_inc_ring(&track_i);
		}
		/* ----- End: Process Ring Buffer ----- */
	}
	newTick = 0;										//acknowledge flag.

	ticksElapsed = (ticksElapsed + 1) % ticksRefresh;	//refresh tick count.
	/* ----- End: Paced Loop Control ----- */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV2;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = DISABLE;
  hadc1.Init.ContinuousConvMode = ENABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_13;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief ADC2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC2_Init(void)
{

  /* USER CODE BEGIN ADC2_Init 0 */

  /* USER CODE END ADC2_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC2_Init 1 */

  /* USER CODE END ADC2_Init 1 */

  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc2.Instance = ADC2;
  hadc2.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV2;
  hadc2.Init.Resolution = ADC_RESOLUTION_12B;
  hadc2.Init.ScanConvMode = DISABLE;
  hadc2.Init.ContinuousConvMode = DISABLE;
  hadc2.Init.DiscontinuousConvMode = DISABLE;
  hadc2.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc2.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc2.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc2.Init.NbrOfConversion = 1;
  hadc2.Init.DMAContinuousRequests = DISABLE;
  hadc2.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  if (HAL_ADC_Init(&hadc2) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_12;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC2_Init 2 */

  /* USER CODE END ADC2_Init 2 */

}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 400000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 5-1;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 64000-1;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim1, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */
  HAL_TIM_MspPostInit(&htim1);

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 65535;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 0;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 0;
  if (HAL_TIM_Encoder_Init(&htim2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 0;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 65535;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 0;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 0;
  if (HAL_TIM_Encoder_Init(&htim3, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */

}

/**
  * @brief TIM4 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM4_Init(void)
{

  /* USER CODE BEGIN TIM4_Init 0 */

  /* USER CODE END TIM4_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_IC_InitTypeDef sConfigIC = {0};

  /* USER CODE BEGIN TIM4_Init 1 */

  /* USER CODE END TIM4_Init 1 */
  htim4.Instance = TIM4;
  htim4.Init.Prescaler = 16-1;
  htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim4.Init.Period = 65536-1;
  htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim4.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim4) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim4, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_IC_Init(&htim4) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim4, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigIC.ICPolarity = TIM_INPUTCHANNELPOLARITY_RISING;
  sConfigIC.ICSelection = TIM_ICSELECTION_DIRECTTI;
  sConfigIC.ICPrescaler = TIM_ICPSC_DIV1;
  sConfigIC.ICFilter = 0;
  if (HAL_TIM_IC_ConfigChannel(&htim4, &sConfigIC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM4_Init 2 */

  /* USER CODE END TIM4_Init 2 */

}

/**
  * @brief TIM6 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM6_Init(void)
{

  /* USER CODE BEGIN TIM6_Init 0 */

  /* USER CODE END TIM6_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM6_Init 1 */

  /* USER CODE END TIM6_Init 1 */
  htim6.Instance = TIM6;
  htim6.Init.Prescaler = 16-1;
  htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim6.Init.Period = 65536-1;
  htim6.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim6) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim6, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM6_Init 2 */

  /* USER CODE END TIM6_Init 2 */

}

/**
  * @brief TIM7 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM7_Init(void)
{

  /* USER CODE BEGIN TIM7_Init 0 */

  /* USER CODE END TIM7_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM7_Init 1 */

  /* USER CODE END TIM7_Init 1 */
  htim7.Instance = TIM7;
  htim7.Init.Prescaler = 2-1;
  htim7.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim7.Init.Period = 16000-1;
  htim7.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim7) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim7, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM7_Init 2 */

  /* USER CODE END TIM7_Init 2 */

}

/**
  * @brief TIM8 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM8_Init(void)
{

  /* USER CODE BEGIN TIM8_Init 0 */

  /* USER CODE END TIM8_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM8_Init 1 */

  /* USER CODE END TIM8_Init 1 */
  htim8.Instance = TIM8;
  htim8.Init.Prescaler = 0;
  htim8.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim8.Init.Period = 7200-1;
  htim8.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim8.Init.RepetitionCounter = 0;
  htim8.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim8) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim8, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim8) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim8, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim8, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim8, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim8, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM8_Init 2 */

  /* USER CODE END TIM8_Init 2 */
  HAL_TIM_MspPostInit(&htim8);

}

/**
  * @brief USART3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART3_UART_Init(void)
{

  /* USER CODE BEGIN USART3_Init 0 */

  /* USER CODE END USART3_Init 0 */

  /* USER CODE BEGIN USART3_Init 1 */

  /* USER CODE END USART3_Init 1 */
  huart3.Instance = USART3;
  huart3.Init.BaudRate = 115200;
  huart3.Init.WordLength = UART_WORDLENGTH_8B;
  huart3.Init.StopBits = UART_STOPBITS_1;
  huart3.Init.Parity = UART_PARITY_NONE;
  huart3.Init.Mode = UART_MODE_TX_RX;
  huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart3.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART3_Init 2 */

  /* USER CODE END USART3_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOE_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOE, OLED_SCLK_Pin|OLED_SDIN_Pin|OLED_RESET__Pin|OLED_DATA_COMMAND__Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, MOTORA_IN2_Pin|MOTORA_IN1_Pin|MOTORB_IN1_Pin|MOTORB_IN2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(US_TRIG_GPIO_Port, US_TRIG_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : OLED_SCLK_Pin OLED_SDIN_Pin OLED_RESET__Pin OLED_DATA_COMMAND__Pin */
  GPIO_InitStruct.Pin = OLED_SCLK_Pin|OLED_SDIN_Pin|OLED_RESET__Pin|OLED_DATA_COMMAND__Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

  /*Configure GPIO pins : MOTORA_IN2_Pin MOTORA_IN1_Pin MOTORB_IN1_Pin MOTORB_IN2_Pin */
  GPIO_InitStruct.Pin = MOTORA_IN2_Pin|MOTORA_IN1_Pin|MOTORB_IN1_Pin|MOTORB_IN2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : BTN_USER_Pin */
  GPIO_InitStruct.Pin = BTN_USER_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(BTN_USER_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : US_TRIG_Pin */
  GPIO_InitStruct.Pin = US_TRIG_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(US_TRIG_GPIO_Port, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
