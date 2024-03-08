#include "convert.h"

float abs_float(float a) {
	return a < 0 ? -a : a;
}
float min_float(float a, float b) {
	return a < b ? a : b;
}
float square_float(float a) {
	return a * a;
}
float dist_squared(float x1, float x2, float y1, float y2) {
	return square_float(x1 - x2) + square_float(y1 - y2);
}

uint8_t min_uint8(uint8_t a, uint8_t b) {
	return a < b ? a : b;
}
uint8_t max_uint8(uint8_t a, uint8_t b) {
	return a > b ? a : b;
}

uint8_t lcm_uint8(uint8_t x, uint8_t y) {
	uint8_t max = (x > y) ? x : y;

    // While loop to check if max variable
    // is divisible by x and y
    while (max < 255) {
        if (max % x == 0 && max % y == 0) {
            return max;
        }

        ++max;
    }

    return max;
}

uint16_t get_uint16(char *buf, uint16_t size) {
	uint16_t ret = 0, i = 0;
	while (i < size) {
		uint8_t d = *(buf + i++) - '0';
		if (d < 0 || d > 9) break;
		ret = ret * 10 + d;
	}

	return ret;
}

//get a uint16_t from a string until terminating character.
uint16_t parse_uint16_t_until(uint8_t **buf_ptr, uint8_t until, uint8_t sizeExpected) {
	uint8_t i = 0, c = **buf_ptr;
	uint16_t res = 0;

	while (i < sizeExpected && c != until) {
		if (c <= '9' && c >= '0') res = res * 10 + (c - '0');

		c = *(++(*buf_ptr)); i++;
	}

	return res;
}

//get a float from a string until terminating character.
float parse_float_until(uint8_t **buf_ptr, uint8_t until, uint8_t sizeExpected) {
	uint8_t i = 0, c = **buf_ptr, isFrac = 0;
	int8_t sign = 1;
	uint32_t whole = 0;
	float frac = 0, div = 0.1;

	while (i < sizeExpected && c != until) {
		if (i == 0 && c == '-') sign *= -1;
		else if (c == '.') isFrac = 1;
		else if (c <= '9' && c >= '0') {
			uint8_t d = c - '0';
			if (isFrac) {
				frac += div * d;
				div *= 0.1;
			}
			else whole = whole * 10 + d;
		}

		c = *(++(*buf_ptr)); i++;
	}

	return (whole + frac) * sign;
}


static float get_turning_r_steer_cm(float steeringAngle) {
	return CHASSIS_CM / sin(steeringAngle * M_PI / 180);
}
float get_turning_r_back_cm(float steeringAngle) {
	return CHASSIS_CM / tan(steeringAngle * M_PI / 180);
}
float get_turning_r_robot_cm(float steeringAngle) {
	float r_steer = get_turning_r_steer_cm(steeringAngle);
	float L2 = CHASSIS_CM / 4;
	float r = sqrt(r_steer * r_steer + L2 * L2);
	if (steeringAngle < 0) r = -r;
	return r;
}

//angular velocity (with actual translational speed).
float get_w_ms(float speed_cm_ms, float turning_r_robot_cm) {
	return speed_cm_ms / turning_r_robot_cm *  180 / M_PI;
}

static float mod_360(float angle) {
	while (angle < -180) angle += 360;
	while (angle > 180) angle -= 360;
	return angle;
}

float add_angle(float old, float change) {
	return mod_360(old + change);
}

float angle_diff_180(float a1, float a2) {
	return mod_360(a1 - a2);
}
float angle_diff_dir(float a1, float a2, int8_t dir) {
	float diff = a1 - a2;

	if (diff < 0 && dir > 0) diff += 360;
	else if (diff > 0 && dir < 0) diff -= 360;

	return diff;
}

float get_distance_cm(uint16_t pulses) {
	return ((float) pulses) / MOTOR_PPR * 2 * M_PI * WHEEL_R_CM;
}

float get_arc_length(float angle, float r) {
	return 2 * M_PI * r * angle / 360;
}
