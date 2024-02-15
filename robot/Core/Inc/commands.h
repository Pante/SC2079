#ifndef INC_COMMANDS_H_
#define INC_COMMANDS_H_

#include <stdlib.h>
#include "commands_FLAGS.h"
#include "convert.h"

typedef enum {
	TARGET,			//drive for this distance
	STOP_WITHIN		//stop when within this distance
} CmdDistType;

struct command_t {
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

void commands_process(uint8_t *buf, uint8_t size);
Command *commands_pop();

#endif /* INC_COMMANDS_H_ */
