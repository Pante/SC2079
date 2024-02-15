#include "pid.h"

void pid_reset(PidDef *def) {
	def->errorArea = 0;
	def->errorOld = 0;
}

void pid_init(PidDef *def, float Kp, float Ki, float Kd) {
	pid_reset(def);

	def->Kp = Kp;
	def->Ki = Ki;
	def->Kd = Kd;
}

float pid_adjust(PidDef *def, float error) {
	def->errorArea += error;
	float errorRate = (error - def->errorOld);
	def->errorOld = error;

	return error * def->Kp + def->errorArea * def->Ki + errorRate * def->Kd;
}
