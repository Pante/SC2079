#ifndef INC_ANGLE_H_
#define INC_ANGLE_H_

#include "kalman.h"
#include "convert.h"

#define ANGLE_S_W 14.0f
#define ANGLE_S_HEADING 9.0f

void angle_init(float heading);
void angle_reset(float heading);
float angle_get(float msElapsed, float w, float heading);

#endif /* INC_ANGLE_H_ */
