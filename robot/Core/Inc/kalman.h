#ifndef INC_KALMAN_H_
#define INC_KALMAN_H_

typedef struct {
	float last_est;
	float s_est;
	float s_mea;
	float gain;
} KalmanParams;

void kalman_init(KalmanParams *params, float s_est, float s_mea);
void kalman_update(KalmanParams *params, float est, float mea);

#endif /* INC_KALMAN_H_ */
