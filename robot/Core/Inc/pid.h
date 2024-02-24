#ifndef INC_PID_H_
#define INC_PID_H_

typedef struct {
	float errorOld;
	float errorArea;
	float Kp;
	float Ki;
	float Kd;
} PidDef;

void pid_reset(PidDef *def);
void pid_init(PidDef *def, float Kp, float Ki, float Kd);
float pid_adjust(PidDef *def, float error, float scale);

#endif /* INC_PID_H_ */
