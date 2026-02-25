/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2019 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "i2c.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "ina219.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
INA219 ina1(0x40);
INA219 ina2(0x41);
INA219 ina3(0x42);
INA219 ina4(0x43);
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
	float bus_voltage1 = 0;
	float bus_voltage2 = 0;
	float bus_voltage3 = 0;
	float bus_voltage4 = 0;
	float shunt_voltage1 = 0;
	float shunt_voltage2 = 0;
	float shunt_voltage3 = 0;
	float shunt_voltage4 = 0;
	float power1 = 0;
	float power2 = 0;
	float power3 = 0;
	float power4 = 0;
	float current1 = 0;
	float current2 = 0;
	float current3 = 0;
	float current4 = 0;
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
  MX_USART2_UART_Init();
  MX_I2C1_Init();
  /* USER CODE BEGIN 2 */
	printf("INA219 TEST !!!\r\n");
	ina1.begin();
	ina2.begin();
	ina3.begin();
	ina4.begin();

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */
    bus_voltage1 = ina1.getBusVoltage_V();         // voltage on V- (load side)
    shunt_voltage1 = ina1.getShuntVoltage_mV()/1000;    // voltage between V+ and V- across the shunt
    power1 = ina1.getPower_mW()/1000;
    current1 = ina1.getCurrent_mA()/1000;               // current in mA

    bus_voltage2 = ina2.getBusVoltage_V();         // voltage on V- (load side)
    shunt_voltage2 = ina2.getShuntVoltage_mV()/1000;    // voltage between V+ and V- across the shunt
    power2 = ina2.getPower_mW()/1000;
    current2 = ina2.getCurrent_mA()/1000;               // current in mA
    
    bus_voltage3 = ina3.getBusVoltage_V();         // voltage on V- (load side)
    shunt_voltage3 = ina3.getShuntVoltage_mV()/1000;    // voltage between V+ and V- across the shunt
    power3 = ina3.getPower_mW()/1000;
    current3 = ina3.getCurrent_mA()/1000;               // current in mA
    
    bus_voltage4 = ina4.getBusVoltage_V();         // voltage on V- (load side)
    shunt_voltage4 = ina4.getShuntVoltage_mV()/1000;    // voltage between V+ and V- across the shunt
    power4 = ina4.getPower_mW()/1000;
    current4 = ina4.getCurrent_mA()/1000;               // current in mA
		
		//sprintf(s,"  %.1fV  %.2fV",bus,busvoltage);
		printf("PSU Voltage:%6.3fV    Shunt Voltage:%9.6fV    Load Voltage:%6.3fV    Power:%9.6fW    Current:%9.6fA\r\n",(bus_voltage1 + shunt_voltage1),(shunt_voltage1),(bus_voltage1),(power1),(current1));
		printf("PSU Voltage:%6.3fV    Shunt Voltage:%9.6fV    Load Voltage:%6.3fV    Power:%9.6fW    Current:%9.6fA\r\n",(bus_voltage2 + shunt_voltage2),(shunt_voltage2),(bus_voltage2),(power2),(current2));
		printf("PSU Voltage:%6.3fV    Shunt Voltage:%9.6fV    Load Voltage:%6.3fV    Power:%9.6fW    Current:%9.6fA\r\n",(bus_voltage3 + shunt_voltage3),(shunt_voltage3),(bus_voltage3),(power3),(current3));
		printf("PSU Voltage:%6.3fV    Shunt Voltage:%9.6fV    Load Voltage:%6.3fV    Power:%9.6fW    Current:%9.6fA\r\n",(bus_voltage4 + shunt_voltage4),(shunt_voltage4),(bus_voltage4),(power4),(current4));
    printf("\r\n");
		printf("\r\n");
		HAL_Delay(500);
		/* USER CODE BEGIN 3 */
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

  /** Initializes the CPU, AHB and APB busses clocks 
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB busses clocks 
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
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
     tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
