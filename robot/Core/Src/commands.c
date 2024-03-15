#include "commands.h"

static Command *cur = NULL;

static Command *get_new_cmd() {
	Command *new = (Command *) malloc(sizeof(Command));
	new->opType = DRIVE;
	new->dir = 0;
	new->speed = 0;
	new->steeringAngle = 0;
	new->val = 0;
	new->distType = TARGET;
	new->next = NULL;

	return new;
}

static void commands_ack(UART_HandleTypeDef *uart, Command *cmd, uint8_t indicator) {
	uint8_t buf_size = cmd->str_size + 1;
	uint8_t *buf = (uint8_t *) malloc(buf_size * sizeof(uint8_t));
	*buf = indicator;
	memcpy(buf + 1, cmd->str, buf_size - 1);

	HAL_UART_Transmit(uart, buf, buf_size, HAL_MAX_DELAY);
	free(buf);
}

void commands_process(UART_HandleTypeDef *uart, uint8_t *buf, uint8_t size) {
	Command *next = get_new_cmd();

	uint8_t c = *buf, *temp = buf;

	//first byte: command flag
	switch (c) {
		case CMD_INFO_DIST:
			next->opType = INFO_DIST;
			break;

		case CMD_FULL_STOP:
			next->dir = 0;
			break;

		case CMD_FORWARD_DIST_TARGET:
			next->dir = 1;
			next->distType = TARGET;
			break;

		case CMD_FORWARD_DIST_AWAY:
			next->dir = 1;
			next->distType = STOP_AWAY;
			break;

		case CMD_BACKWARD_DIST_TARGET:
			next->dir = -1;
			next->distType = TARGET;
			break;

		case CMD_BACKWARD_DIST_AWAY:
			next->dir = -1;
			next->distType = STOP_AWAY;
			break;

		default:
			//invalid command, return.
			return;
	}

	if (next->opType == DRIVE && c != CMD_FULL_STOP) {
		temp++;
		next->speed = parse_uint16_t_until(&temp, CMD_SEP, 3);
		temp++;
		next->steeringAngle = parse_float_until(&temp, CMD_SEP, 6);
		temp++;
		next->val = parse_float_until(&temp, CMD_END, 6);
	} else {
		*(++temp) = CMD_END;
	}

	//copy command.
	uint8_t str_size = temp - buf + 1;
	next->str_size = str_size;
	next->str = (uint8_t *) malloc(str_size * sizeof(uint8_t));
	memcpy(next->str, buf, str_size);


	if (cur == NULL) {
		cur = next;
	} else {
		Command *temp = cur;
		while (temp->next != NULL) {
			temp = temp->next;
		}
		temp->next = next;
	}

	//acknowledge command has been received and queued.
	commands_ack(uart, next, CMD_RCV);
}


Command *commands_pop() {
	Command *ret = cur;
	if (cur != NULL) cur = cur->next;
	return ret;
}

//find the next drive command (for chaining).
Command *commands_peek_next_drive() {
	Command *temp = cur;
	while (temp != NULL && temp->opType != DRIVE) temp = temp->next;
	return temp;
}

void commands_end(UART_HandleTypeDef *uart, Command *cmd) {
	commands_ack(uart, cmd, CMD_FIN);
	free(cmd->str);
	free(cmd);
}

uint8_t commands_type_match(Command *a, Command *b) {
	return (a->dir == b->dir)
			&& (a->speed == b->speed)
			&& (a->steeringAngle == b->steeringAngle)
			&& (a->distType == b->distType);
}
