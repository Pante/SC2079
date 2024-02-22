#include "angle.h"

static KalmanParams kParams;

void angle_init(float heading) {
	angle_reset(heading);
}

void angle_reset(float heading) {
	kalman_init(&kParams, heading, ANGLE_S_W, ANGLE_S_HEADING);
}
float angle_get(float msElapsed, float w, float heading) {
	float angle_w = add_angle(kParams.last_est, w * msElapsed);

	kParams.s_est += msElapsed * msElapsed * ANGLE_S_W;
	kalman_update(&kParams, angle_w, heading);

	if (angle_w < -90 && (heading - angle_w) > 180 || heading < -90 && (angle_w - heading) > 180) {
		//detect discontinuous wrapping; adjust accordingly.
		kParams.last_est = add_angle(kParams.last_est, 180);
	}
	return kParams.last_est;
}
