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

void commands_process(UART_HandleTypeDef *uart, uint8_t *buf, uint8_t size) {
	Command *next = get_new_cmd();

	uint8_t c = *buf, *temp = buf;

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
		temp++;
		next->speed = parse_uint16_t_until(&temp, CMD_SEP, 3);
		temp++;
		next->steeringAngle = parse_float_until(&temp, CMD_SEP, 6);
		temp++;
		next->dist = parse_float_until(&temp, CMD_END, 6);
	}

	//copy command.
	uint8_t str_size = temp - buf;
	next->str_size = str_size;
	next->str = (uint8_t *) malloc(str_size * sizeof(uint8_t));
	memcpy(cmd->str, buf, str_size);

	//acknowledge command.
	commands_ack(uart, next, CMD_RCV);

	if (cur == NULL) {
		cur = next;
		return;
	}

	while (cur->next != NULL) cur = cur->next;
	cur->next = next;
}

static void commands_ack(UART_HandleTypeDef *uart, Commands *cmd, uint8_t indicator) {
	uint8_t buf_size = cmd->str_size + 1;
	uint8_t *buf = (uint8_t *) malloc(buf_size * sizeof(uint8_t));
	*buf = indicator;
	memcpy(++buf, cmd->str, buf_size - 1);

	HAL_UART_Transmit(uart, buf, buf_size, HAL_MAX_DELAY);
	free(buf);
}

Command *commands_pop() {
	Command *ret = cur;
	if (cur != NULL) cur = cur->next;
	return ret;
}

void commands_end(UART_HandleTypeDef *uart, Command *cmd) {
	commands_ack(uart, cmd, CMD_FIN);
	free(cmd->str);
	free(cmd);
}
