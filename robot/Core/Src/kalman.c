#include "kalman.h"

void kalman_init(KalmanParams *params, float initial_est, float s_est, float s_mea){
	params->last_est = initial_est;
	params->s_est = s_est;
	params->s_mea = s_mea;
}

void kalman_update(KalmanParams *params, float est, float mea){
	//calculate Kalman gain.
	float G = (params->s_est) / (params->s_est + params->s_mea);

	//update estimate.
	params->last_est += G * (mea - est);
}
