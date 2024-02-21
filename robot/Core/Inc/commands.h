#ifndef INC_COMMANDS_H_
#define INC_COMMANDS_H_

#include "main.h"
#include <stdlib.h>
#include "commands_FLAGS.h"
#include "convert.h"

typedef enum {
	TARGET,			//drive for this distance
	STOP_AWAY		//stop when roughly this distance away from front.
} CmdDistType;

struct command_t {
	//command string
	uint8_t *str;
	uint8_t str_size;

	//motor directives
	int8_t dir;			//-1: backward, 0: stop, 1: forward
	uint8_t speed;			//0 to 100
	float steeringAngle;	//-25 to 25

	//distance directives
	CmdDistType distType;
	float dist;

	struct command_t *next;
};

typedef struct command_t Command;

void commands_process(UART_HandleTypeDef *uart, uint8_t *buf, uint8_t size);
Command *commands_pop();
void commands_end(UART_HandleTypeDef *uart, Command *cmd);
#endif /* INC_COMMANDS_H_ */
