#ifndef INC_COMMANDS_FLAGS_H_
#define INC_COMMANDS_FLAGS_H_

/* COMMAND FORMAT (IN ASCII)
 * NOTE: MAXIMUM LENGTH OF 20 characters.
 * <flag><speed><SEP><angle><SEP><dist><END>
 *
 * <flag>: 1 char
 * - use one of the characters below to specify which action to take.
 *
 * <speed>: 1-3 chars
 * - specify speed to drive, from 0 to 100 (integer).
 *
 * <angle>: 1+ chars, in degrees
 * - specify angle to steer, from -25 to 25 (float).
 * - negative angle: steer left, positive angle: steer right.
 *
 *
 * <dist>: 1+ chars, in cm
 * - specify distance to drive, from 0 to 500 (float).
 *
 * <SEP>: character specified below as CMD_SEP ('|').
 * <END>: character specified below as CMD_END ('\n').
 *
 * e.g., to drive forward at speed 50 for 30cm going straight:
 * send 'T50|0|30\n'
 *
 * e.g., to drive backward at speed 20 until within 5cm while wheels are steering left 10 degrees:
 * send 'w20|-10|5\n'
 * */

#define CMD_FULL_STOP 'S'				//bring car to a complete stop. (all other fields are not required, i.e., send 'S\0')

#define CMD_FORWARD_DIST_TARGET 'T'		//go forward for a target distance.
#define CMD_FORWARD_DIST_WITHIN 'W'		//go forward until within a certain distance.
#define CMD_BACKWARD_DIST_TARGET 't'	//go backward for a target distance.
#define CMD_BACKWARD_DIST_WITHIN 'w'	//go backward until within a certain distance.

#define CMD_SEP '|'						//separator.
#define CMD_END '\n'					//end character.
#endif /* INC_COMMANDS_FLAGS_H_ */
