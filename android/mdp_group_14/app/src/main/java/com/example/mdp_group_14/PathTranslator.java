package com.example.mdp_group_14;

import android.util.Log;
import android.widget.Toast;

// To translate the relayed path given from algo to rpi and then to android to update robot position in "real-time"
// Basically will involve converting stm commands into its 'equivalent' on the 20x20 grid map
public class PathTranslator {
    private static final String TAG = "PathTranslator";
    private static GridMap gridMap;
    private static final int CELL_LENGTH = 10; //length of each cell in cm
    private static final int MILLI_DELAY = 200;    // delay between movement commands

    // Turning radius differs for each turn :/
    private static final int LEFT_TURNING_RADIUS = 40;
    private static final int RIGHT_TURNING_RADIUS = 41;
    private static final int BLEFT_TURNING_RADIUS = 37;
    private static final int BRIGHT_TURNING_RADIUS = 41;
//    private static final int TURNING_RADIUS = 33;   // to estimate the cells covered in an executed turn (removed because turning radius differs for all turns)

    // for altTranslation
    private int curX, curY;
    private String dir;

    public PathTranslator() {
        this.gridMap = Home.getGridMap();
    }

    public PathTranslator(GridMap gridMap) {
        this.gridMap = gridMap;
        this.curX = 2;
        this.curY = 1;
        this.dir = "up";    // up,down,left,right
    }

    public void altTranslation(String stmCommand) {
        showLog("Entered translatePath");
        char commandType = stmCommand.charAt(0);
        int commandValue = 0;
        try {
            commandValue = Integer.parseInt(stmCommand.substring(1));
        } catch(Exception e) {}
        int moves = 0;
        switch(commandType) {
            case 'f':   // forward
//                Home.refreshMessageReceivedNS("==========================\nForward " + commandValue);
                moves = commandValue / CELL_LENGTH;
                switch(dir) {
                    case "up":
                        curY += moves;
                        break;
                    case "down":
                        curY -= moves;
                        break;
                    case "left":
                        curX -= moves;
                        break;
                    case "right":
                        curX += moves;
                        break;
                }
//                gridMap.setCurCoord(curX, curY, dir);
                break;
            case 'b':   // backward
//                Home.refreshMessageReceivedNS("==========================\nBackward " + commandValue);
                moves = commandValue / CELL_LENGTH;
                switch(dir) {
                    case "up":
                        curY -= moves;
                        break;
                    case "down":
                        curY += moves;
                        break;
                    case "left":
                        curX += moves;
                        break;
                    case "right":
                        curX -= moves;
                        break;
                }
//                gridMap.setCurCoord(curX, curY, dir);
                break;
            case 'd':   // 90 deg right
//                Home.refreshMessageReceivedNS("==========================\nRight turn");
                moves = RIGHT_TURNING_RADIUS / CELL_LENGTH;   // floor div. of turning radius against cell len
                switch(dir) {
                    case "up":
                        curY += moves;
                        curX += moves;
                        dir = "right";
                        break;
                    case "down":
                        curY -= moves;
                        curX -= moves;
                        dir = "left";
                        break;
                    case "left":
                        curX -= moves;
                        curY += moves;
                        dir = "up";
                        break;
                    case "right":
                        curX += moves;
                        curY -= moves;
                        dir = "down";
                        break;
                }
//                gridMap.setCurCoord(curX, curY, dir);
                break;
            case 'a':   // 90 deg left
//                Home.refreshMessageReceivedNS("==========================\nLeft turn");
                moves = LEFT_TURNING_RADIUS / CELL_LENGTH;   // floor div. of turning radius against cell len
                switch(dir) {
                    case "up":
                        curY += moves;
                        curX -= moves;
                        dir = "left";
                        break;
                    case "down":
                        curY -= moves;
                        curX += moves;
                        dir = "right";
                        break;
                    case "left":
                        curX -= moves;
                        curY -= moves;
                        dir = "down";
                        break;
                    case "right":
                        curX += moves;
                        curY += moves;
                        dir = "up";
                        break;
                }
//                gridMap.setCurCoord(curX, curY, dir);
                break;
            case 'q':   // 90 deg back-left
//                Home.refreshMessageReceivedNS("==========================\nBack-left turn");
                moves = BLEFT_TURNING_RADIUS / CELL_LENGTH;   // floor div. of turning radius against cell len
                switch(dir) {
                    case "up":
                        curY -= moves;
                        curX -= moves;
                        dir = "right";
                        break;
                    case "down":
                        curY += moves;
                        curX += moves;
                        dir = "left";
                        break;
                    case "left":
                        curX += moves;
                        curY -= moves;
                        dir = "up";
                        break;
                    case "right":
                        curX -= moves;
                        curY += moves;
                        dir = "down";
                        break;
                }
//                gridMap.setCurCoord(curX, curY, dir);
                break;
            case 'e':   // 90 deg back-right
//                Home.refreshMessageReceivedNS("==========================\nBack-right turn");
                moves = BRIGHT_TURNING_RADIUS / CELL_LENGTH;   // floor div. of turning radius against cell len
                switch(dir) {
                    case "up":
                        curY -= moves;
                        curX += moves;
                        dir = "left";
                        break;
                    case "down":
                        curY += moves;
                        curX -= moves;
                        dir = "right";
                        break;
                    case "left":
                        curX += moves;
                        curY += moves;
                        dir = "down";
                        break;
                    case "right":
                        curX -= moves;
                        curY -= moves;
                        dir = "up";
                        break;
                }
//                gridMap.setCurCoord(curX, curY, dir);
                break;
            case 's':   // stop to scan (might be redundant)
                Toast.makeText(gridMap.getContext(), "Scanning image...",Toast.LENGTH_SHORT).show();
                try {
                    Thread.sleep(1000);
                } catch(InterruptedException e) {
                    showLog("InterruptedException occurred when calling Thread.sleep()!");
                    e.printStackTrace();
                }
                break;
            default:
                showLog("Invalid commandType!");
        }
        gridMap.setCurCoord(curX, curY, dir);
        showLog("Exited altTranslation");
    }

    public void translatePath(String stmCommand) {
        showLog("Entered translatePath");
        char commandType = 'z'; //commandType is a single character for switch case
        int commandValue = 0; //commandValue represents the value to move forwards or backwards.

        //Case 1: is a MOVE command. Expects a syntax of eg. MOVE,<DISTANCE IN CM>,<DIRECTION>.
        if(stmCommand.contains("MOVE")){

            try { //set commandValue to <DISTANCE IN CM>
                commandValue = Integer.parseInt(stmCommand.split(",")[1]);

            } catch(Exception e) {}

//            try { //set commandValue to <DISTANCE IN CM>
//                 commandValue = Integer.parseInt(stmCommand.split(",")[2]);
//
//            } catch(Exception e) {}

            //set commandType for <DIRECTION>
            String direction = stmCommand.split(",")[1];
            showLog("directions"+direction);

            commandValue = Integer.valueOf(stmCommand.split(",")[2].replace("\n",""));

//showLog(String.valueOf(Integer.parseInt(stmCommand.split(",")[2])));

            if(direction.equals("FORWARD")){
                commandType = 'f';
            }
            else if (direction.equals("BACKWARD")){
                commandType = 'b';
            }
        }
        //Case 2: is a TURN command. Expects a syntax of eg. TURN,<DIRECTION>.
        else if (stmCommand.contains("TURN")){
            String direction = stmCommand.split(",")[1];
            //set commandType for <DIRECTION> for Turns
            if(direction.equals("FORWARD_RIGHT")){
                commandType = 'd';
            }
            if(direction.equals("FORWARD_LEFT")){
                commandType = 'a';
            }
            if (direction.equals("BACKWARD_RIGHT")){
                commandType = 'e';
            }
            if (direction.equals("BACKWARD_LEFT")){
                commandType = 'q';
            }
        }

        int moves = 0;
        switch(commandType) {
            case 'f':   // forward
//                Home.refreshMessageReceivedNS("==========================\nForward " + commandValue);
                moves = commandValue / CELL_LENGTH;
                for(int i = 0; i < moves; i++) {
                    gridMap.moveRobot("forward");


                    Home.refreshLabel();    // update x and y coordinate displayed
                    // display different statuses depending on validity of robot action
                    if (gridMap.getValidPosition()){
                        showLog("moving forward");}
                    else {
//                        Home.printMessage("obstacle");
                        showLog("Unable to move forward");
                    }

                    Home.printMessage("f");

                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                break;
            case 'b':   // backwards
//                Home.refreshMessageReceivedNS("==========================\nBackward " + commandValue);
                moves = commandValue / CELL_LENGTH;
                for(int i = 0; i < moves; i++) {
                    gridMap.moveRobot("back");
                    Home.refreshLabel();
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                break;
            case 'd':   // 90 deg right
//                Home.refreshMessageReceivedNS("==========================\nForward_Right turn");
                gridMap.moveRobot("right");
                Home.refreshLabel();
                /*
                moves = RIGHT_TURNING_RADIUS / CELL_LENGTH;   // floor div. of turning radius against cell len
                // forward movement
                for(int i = 0; i < moves - 1; i++) {
                    gridMap.moveRobot("forward");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                // right movement
                gridMap.moveRobot("right");
                try {
                    Thread.sleep(MILLI_DELAY);
                } catch(InterruptedException e) {
                    showLog("InterruptedException occurred when calling Thread.sleep()!");
                    e.printStackTrace();
                }
                // forward movement
                for(int i = 0; i < moves - 1; i++) {
                    gridMap.moveRobot("forward");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                 */
                break;
            case 'a':   // 90 deg left
//                Home.refreshMessageReceivedNS("==========================\nForward_Left turn");
                gridMap.moveRobot("left");
                /*
                moves = LEFT_TURNING_RADIUS / CELL_LENGTH;   // floor div. of turning radius against cell len
                // forward movement
                for(int i = 0; i < moves - 1; i++) {
                    gridMap.moveRobot("forward");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                // left movement
                gridMap.moveRobot("left");
                try {
                    Thread.sleep(MILLI_DELAY);
                } catch(InterruptedException e) {
                    showLog("InterruptedException occurred when calling Thread.sleep()!");
                    e.printStackTrace();
                }
                // forward movement
                for(int i = 0; i < moves - 1; i++) {
                    gridMap.moveRobot("forward");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                 */
                break;
            case 'q':   // 90 deg back-left
//                Home.refreshMessageReceivedNS("==========================\nBackward_Left turn");
                gridMap.moveRobot("backleft");
                /*
                moves = BLEFT_TURNING_RADIUS / CELL_LENGTH;   // floor div. of turning radius against cell len
                // backward movement
                for(int i = 0; i < moves - 1; i++) {
                    gridMap.moveRobot("back");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                //back-left movement
                gridMap.moveRobot("backleft");
                try {
                    Thread.sleep(MILLI_DELAY);
                } catch(InterruptedException e) {
                    showLog("InterruptedException occurred when calling Thread.sleep()!");
                    e.printStackTrace();
                }
                // backward movement
                for(int i = 0; i < moves - 1; i++) {
                    gridMap.moveRobot("back");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                 */
                break;
            case 'e':   // 90 deg back-right
//                Home.refreshMessageReceivedNS("==========================\nBackward_Right turn");
                gridMap.moveRobot("backright");
                /*
                moves = BRIGHT_TURNING_RADIUS / CELL_LENGTH;   // floor div. of turning radius against cell len
                // backward movement
                for(int i = 0; i < moves - 1; i++) {
                    gridMap.moveRobot("back");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                //back-right movement
                gridMap.moveRobot("backright");
                try {
                    Thread.sleep(MILLI_DELAY);
                } catch(InterruptedException e) {
                    showLog("InterruptedException occurred when calling Thread.sleep()!");
                    e.printStackTrace();
                }
                // backward movement
                for(int i = 0; i < moves - 1; i++) {
                    gridMap.moveRobot("back");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                 */
                break;
            case 's':   // stop to scan (might be redundant)
                Toast.makeText(gridMap.getContext(), "Scanning image...",Toast.LENGTH_SHORT).show();
                try {
                    Thread.sleep(1000);
                } catch(InterruptedException e) {
                    showLog("InterruptedException occurred when calling Thread.sleep()!");
                    e.printStackTrace();
                }
                break;
            default:
                showLog("Invalid commandType!");
        }
        showLog("Exited translatePath");
    }

    private static void showLog(String message) {
        Log.d(TAG, message);
    }
}
