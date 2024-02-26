package com.example.mdp_grp_21;

import android.util.Log;
import android.widget.Toast;

// To translate the relayed path given from algo to rpi and then to android to update robot position in "real-time"
// Basically will involve converting stm commands into its 'equivalent' on the 20x20 grid map
public class PathTranslator {
    private static final String TAG = "PathTranslator";
    private static GridMap gridMap;
    private static final int CELL_LENGTH = 10;
    private static final int MILLI_DELAY = 200;    // delay between movement commands

    // Turning radius differs for each turn :/
    private static final int LEFT_TURNING_RADIUS = 24;
    private static final int RIGHT_TURNING_RADIUS = 34;
    private static final int BLEFT_TURNING_RADIUS = 25;
    private static final int BRIGHT_TURNING_RADIUS = 35;
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
                Home.refreshMessageReceivedNS("==========================\nForward " + commandValue);
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
                Home.refreshMessageReceivedNS("==========================\nBackward " + commandValue);
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
                Home.refreshMessageReceivedNS("==========================\nRight turn");
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
                Home.refreshMessageReceivedNS("==========================\nLeft turn");
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
                Home.refreshMessageReceivedNS("==========================\nBack-left turn");
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
                Home.refreshMessageReceivedNS("==========================\nBack-right turn");
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
        char commandType = stmCommand.charAt(0);
        int commandValue = 0;
        try {
            commandValue = Integer.parseInt(stmCommand.substring(1));
        } catch(Exception e) {}
        int moves = 0;
        switch(commandType) {
            case 'f':   // forward
                Home.refreshMessageReceivedNS("==========================\nForward " + commandValue);
                moves = commandValue / CELL_LENGTH;  // each cell is (assumed) to be 10 (cm?) long
                for(int i = 0; i < moves; i++) {
                    gridMap.moveRobot("forward");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                break;
            case 'b':   // backwards
                Home.refreshMessageReceivedNS("==========================\nBackward " + commandValue);
                moves = commandValue / CELL_LENGTH;  // each cell is (assumed) to be 10 (cm?) long
                for(int i = 0; i < moves; i++) {
                    gridMap.moveRobot("back");
                    try {
                        Thread.sleep(MILLI_DELAY);
                    } catch(InterruptedException e) {
                        showLog("InterruptedException occurred when calling Thread.sleep()!");
                        e.printStackTrace();
                    }
                }
                break;
            case 'd':   // 90 deg right
                Home.refreshMessageReceivedNS("==========================\nRight turn");
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
                break;
            case 'a':   // 90 deg left
                Home.refreshMessageReceivedNS("==========================\nLeft turn");
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
                break;
            case 'q':   // 90 deg back-left
                Home.refreshMessageReceivedNS("==========================\nBack-left turn");
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
                break;
            case 'e':   // 90 deg back-right
                Home.refreshMessageReceivedNS("==========================\nBack-right turn");
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
