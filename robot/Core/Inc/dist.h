#ifndef INC_DIST_H_
#define INC_DIST_H_

#include "kalman.h"

#define DIST_S_ACCEL 9.80665e-6f
#define DIST_S_MOTOR 0.25f

//accurate range of IR sensor.
#define DIST_IR_MIN 10
#define DIST_IR_MAX 70

typedef struct {
	float dist;
	float v;
	float s_v;
} DistState;

void dist_init();
void dist_reset(float v);
float dist_get_cm(float msElapsed, float accel, float motorDist);
float dist_get_front(float usDist, float irDist);

#endif /* INC_DIST_H_ */
