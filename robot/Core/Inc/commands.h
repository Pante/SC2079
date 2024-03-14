#ifndef INC_COMMANDS_H_
#define INC_COMMANDS_H_

#include "main.h"
#include <stdlib.h>
#include <string.h>
#include "commands_FLAGS.h"
#include "convert.h"

enum _cmdOpType {
	DRIVE,			//is a drive command, i.e., robot will move.

	//Commands related to relaying information.
	INFO_DIST		//toggle start/stop of accumulative distance tracking.
};
enum _cmdDistType {
	TARGET,			//drive for this distance
	STOP_AWAY		//stop when roughly this distance away from front.
};

typedef enum _cmdOpType CmdOpType;
typedef enum _cmdDistType CmdDistType;

struct command_t {
	//command op type
	CmdOpType opType;

	//command string
	uint8_t *str;
	uint8_t str_size;

	/* start: DRIVE parameters */
	//motor directives
	int8_t dir;				//-1: backward, 0: stop, 1: forward
	uint8_t speed;			//0 to 100
	float steeringAngle;	//-25 to 25

	//distance directives
	CmdDistType distType;
	float val;				//for angle != 0: angle to turn; for angle = 0: distance to drive.
	/* end: DRIVE parameters */

	struct command_t *next;
};

typedef struct command_t Command;

void commands_process(UART_HandleTypeDef *uart, uint8_t *buf, uint8_t size);
Command *commands_pop();
Command *commands_peek_next_drive();
void commands_end(UART_HandleTypeDef *uart, Command *cmd);
uint8_t commands_type_match(Command *a, Command *b);
#endif /* INC_COMMANDS_H_ */
