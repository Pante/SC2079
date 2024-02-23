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

float pid_adjust(PidDef *def, float error, float scale) {
	def->errorArea += error;
	float errorRate = (error - def->errorOld);
	def->errorOld = error;

	return error * def->Kp * scale + def->errorArea * def->Ki * scale + errorRate * def->Kd * scale;
}
