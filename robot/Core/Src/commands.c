#include "commands.h"

static Command *cur = NULL;

static Command *get_new_cmd() {
	Command *new = (Command *) malloc(sizeof(Command));
	new->dir = 0;
	new->speed = 0;
	new->steeringAngle = 0;
	new->dist = 0;
	new->distType = TARGET;
	new->next = NULL;

	return new;
}

void commands_process(uint8_t *buf, uint8_t size) {
	Command *next = get_new_cmd();

	uint8_t c = *buf;

	//first byte: command flag
	switch (c) {
		case CMD_FULL_STOP:
			next->dir = 0;
			break;

		case CMD_FORWARD_DIST_TARGET:
			next->dir = 1;
			next->distType = TARGET;
			break;

		case CMD_FORWARD_DIST_WITHIN:
			next->dir = 1;
			next->distType = STOP_WITHIN;
			break;

		case CMD_BACKWARD_DIST_TARGET:
			next->dir = -1;
			next->distType = TARGET;
			break;

		case CMD_BACKWARD_DIST_WITHIN:
			next->dir = -1;
			next->distType = STOP_WITHIN;
			break;

		default:
			//invalid command, return.
			return;
	}

	if (c != CMD_FULL_STOP) {
		buf++;
		next->speed = parse_uint16_t_until(&buf, CMD_SEP, 3);
		buf++;
		next->steeringAngle = parse_float_until(&buf, CMD_SEP, 6);
		buf++;
		next->dist = parse_float_until(&buf, CMD_END, 6);
	}

	if (cur == NULL) {
		cur = next;
		return;
	}

	while (cur->next != NULL) cur = cur->next;
	cur->next = next;
}

Command *commands_pop() {
	Command *ret = cur;
	if (cur != NULL) cur = cur->next;
	return ret;
}
