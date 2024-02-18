#ifndef INC_DIST_H_
#define INC_DIST_H_

#include "kalman.h"

#define DIST_S_ACCEL 9.80665e-6f
#define DIST_S_MOTOR 1.0f

typedef struct {
	float dist;
	float v;
	float s_v;
} DistState;

void dist_init();
void dist_reset();
float dist_get_cm(float msElapsed, float accel, float motorDist);

#endif /* INC_DIST_H_ */
