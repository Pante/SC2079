#include "display_status.h"

uint8_t oled_buf[25];

void write_arr(uint8_t x, uint8_t y, uint8_t label, float r[3]) {
	snprintf(oled_buf, 25, "%c%+.3f|%+.3f|%+.3f", label, r[0], r[1], r[2]);
	OLED_ShowString(x, y, oled_buf);
	OLED_Refresh_Gram();
}

void write_motion(float accel[3], float gyroZ, float heading) {
	snprintf(oled_buf, 25, "Z%+.3f|%+.3f", heading, gyroZ);
	OLED_ShowString(0, 0, oled_buf);

	write_arr(0, 30, 'A', accel);
}

void write_motors(uint16_t lAngle, uint16_t rAngle, uint16_t lPwmVal, uint16_t rPwmVal, int32_t offset) {
	snprintf(oled_buf, 25, "%5i", lAngle - rAngle);
	OLED_ShowString(0, 0, oled_buf);
	snprintf(oled_buf, 25, "%5i|%5i", lPwmVal, rPwmVal);
	OLED_ShowString(0, 20, oled_buf);
	snprintf(oled_buf, 25, "%10d", offset);
	OLED_ShowString(0, 40, oled_buf);
	OLED_Refresh_Gram();
}

void display_init() {
	OLED_Init();
}
