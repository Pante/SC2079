package com.example.mdpandroidcontroller;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;

import androidx.annotation.Nullable;

import java.util.ArrayList;
import java.util.Arrays;


public class Map extends View { //implements Serializable

    //private static final long serialVersionUID = 1L;
    private Context context;
    private AttributeSet attrs;
    private boolean mapDrawn = false;
    private static ArrayList<String[]> arrowCoord = new ArrayList<>();
    private static Cell[][] cells;
    private static final int COL = Constants.TWENTY;
    private static final int ROW = Constants.TWENTY;
    private static float cellSize;
    private static boolean canDrawRobot = false;
    private static String robotMovement = Constants.NONE; // the direction its going
    private static String robotFacing = Constants.NONE;

    private static boolean robotReverse = false;  // at first always move forward
    private static int robotSize = 3;
    private static int oldFacing;
    private static int newFacing;
    private static String[] robotFacingEnum = new String[] {Constants.NORTH, Constants.EAST, Constants.SOUTH, Constants.WEST};
    private static int[] curCoord = new int[]{1, 1};

    private static ArrayList<int[]> obstacleCoord = new ArrayList<>();

    private static int[] oldCoord = new int[]{-1, -1};

    private Paint black = new Paint();
    private Paint lineColor = new Paint();
    private Paint unexploredCellColor = new Paint();
    private Paint robotColor = new Paint();


    public Map(Context c) {
        super(c);
        black.setStyle(Paint.Style.FILL_AND_STROKE);
        unexploredCellColor.setColor(0xFFe2f2fc); // light teal: 0xFFD4F6F2
        robotColor.setColor(Color.RED); //GREEN
        lineColor.setColor(0xFFBDBDBD); // white / 0xFF757575 / 0xFFBDBDBD LIGHTER
    }

    public Map(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        this.context = context;
        this.attrs = attrs;

        black.setStyle(Paint.Style.FILL_AND_STROKE);
        unexploredCellColor.setColor(0xFFe2f2fc);
        robotColor.setColor(Color.RED);
        lineColor.setColor(0xFFBDBDBD);
    }


    /**
     * where u start everything
     * @param canvas
     */
    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // on first time drawing?
        if (!mapDrawn) {
            this.createCell();
            setRobotFacing(Constants.NORTH);
            mapDrawn = true;

        }

        drawGridAxes(canvas);
        drawObstacles(canvas, obstacleCoord);
        if (getCanDrawRobot()) {
            drawRobot(canvas, curCoord);
        }
        drawCell(canvas);
        drawHorizontalLines(canvas);
        drawVerticalLines(canvas);
    }

    private void createCell() {
        cells = new Cell[COL + 1][ROW + 1];
        this.calculateDimension();
        cellSize = this.getCellSize();

        for (int x = 0; x <= COL; x++) {
            for (int y = 0; y <= ROW; y++) {
                cells[x][y] = new Cell(x * cellSize + (cellSize / 30), y * cellSize + (cellSize / 30), (x + 1) * cellSize, (y + 1) * cellSize, unexploredCellColor, "unexplored");
            }
        }
    }


    /**
     * Drawing of cells
     * @param canvas
     */
    public void drawCell(Canvas canvas) {
        for (int x = 1; x <= COL; x++) {
            for (int y = 0; y < ROW; y++) {
                for (int i = 0; i < robotSize; i++) {
                    Paint textPaint = new Paint();
                    textPaint.setTextSize(20);
                    textPaint.setColor(Color.WHITE);
                    textPaint.setTextAlign(Paint.Align.CENTER);
                    canvas.drawText(String.valueOf(cells[x][y].getId()),(cells[x][y].startX+cells[x][y].endX)/2, cells[x][y].endY + (cells[x][y].startY-cells[x][y].endY)/4, textPaint);
                    canvas.drawRect(cells[x][y].startX, cells[x][y].startY, cells[x][y].endX, cells[x][y].endY, cells[x][y].paint);
                }
            }
        }
    }



    /**
     * Draws vertical lines for each of the cells
     * @param canvas
     */
    private void drawVerticalLines(Canvas canvas) {
        for (int x = 0; x <= COL; x++)
            canvas.drawLine(cells[x][0].startX - (cellSize / 30) + cellSize, cells[x][0].startY - (cellSize / 30), cells[x][0].startX - (cellSize / 30) + cellSize, cells[x][19].endY + (cellSize / 30), lineColor);
    }

    /**
     * Draws horizontal lines for each of the cells
     * @param canvas
     */
    private void drawHorizontalLines(Canvas canvas) {
        for (int y = 0; y <= ROW; y++)
            canvas.drawLine(cells[1][y].startX, cells[1][y].startY - (cellSize / 30), cells[ROW][y].endX, cells[15][y].startY - (cellSize / 30), lineColor); // black lines
    }



    public void drawRobot(Canvas canvas, int[] curCoord) {
        int androidRowCoord = this.convertRow(curCoord[1]);

        // for the shading of square - USED TO BE -1 to + 1
        for (int x = curCoord[0]; x <= curCoord[0] + 2; x++)
            for (int y = androidRowCoord - 2; y <= androidRowCoord; y++)
                cells[x][y].setType("robot");
    }

    private void drawGridAxes(Canvas canvas) {
        for (int x = 1; x <= COL; x++) {
            if (x > 9)
                canvas.drawText(Integer.toString(x-1), cells[x][20].startX + (cellSize / 5), cells[x][20].startY + (cellSize / 3), black);
            else
                canvas.drawText(Integer.toString(x-1), cells[x][20].startX + (cellSize / 3), cells[x][20].startY + (cellSize / 3), black);
        }
        for (int y = 0; y < ROW; y++) {
            if ((20 - y) > 9)
                canvas.drawText(Integer.toString(19 - y), cells[0][y].startX + (cellSize / 2), cells[0][y].startY + (cellSize / 1.5f), black);
            else
                canvas.drawText(Integer.toString(19 - y), cells[0][y].startX + (cellSize / 1.5f), cells[0][y].startY + (cellSize / 1.5f), black);
        }
    }

    public void drawObstacles(Canvas canvas, ArrayList<int[]> obstacles) {
        for (int i = 0; i < obstacles.size(); i++) {
            cells[obstacles.get(i)[0]][obstacles.get(i)[1]].setType("obstacle");
        }
    }

    /**
     * have smt to move the robot
     * HOW TO MAKE THE OLD ONE NOT COUNT
     */
    public void moveRobot() {
        int[] tempCoord = this.getCurCoord();
        this.setOldRobotCoord(tempCoord[0], tempCoord[1]);
        int[] oldCoord = this.getOldRobotCoord();

        int transX = 0, transY = 0;

        oldFacing = convertFacingToIndex(getRobotFacing());
        switch( this.getRobotMovement()) {
            case Constants.UP:
                // Includes check for end of the grid
                transX = 0;
                transY = 1;
                break;
            case Constants.DOWN:
                transX = 0;
                transY = -1;
                break;
            case Constants.LEFT:
                transX = -1;
                transY = 2;

                //changing to new facing
                if (robotReverse) {
                    newFacing = (oldFacing + 1) % 4;
                } else {
                    newFacing = (oldFacing + 3) % 4;
                }
                setRobotFacing(robotFacingEnum[newFacing]);


                break;
            case Constants.RIGHT:
                transX = 1;
                transY = 2;

                if (robotReverse) {
                    newFacing = (oldFacing + 3) % 4;
                } else {
                    newFacing = (oldFacing + 1) % 4;
                }
                setRobotFacing(robotFacingEnum[newFacing]);

                break;
            default:
                System.out.println("Error in moveRobot() direction input");
                break;
        }

        if (robotReverse) {
            transY = transY * -1;
        }

        // to change the direction according to formula!
        switch (oldFacing) {
            case 0: //North
                tempCoord[0] = tempCoord[0] + transX;
                tempCoord[1] = tempCoord[1] + transY;
                break;
            case 1: //East
                tempCoord[0] = tempCoord[0] + transY;
                tempCoord[1] = tempCoord[1] - transX;
                break;
            case 2: //South
                tempCoord[0] = tempCoord[0] - transX;
                tempCoord[1] = tempCoord[1] - transY;
                break;
            case 3: //West
                tempCoord[0] = tempCoord[0] - transY;
                tempCoord[1] = tempCoord[1] + transX;
                break;
        }



        // CHECKS OUT OF BOUNDS
        if (tempCoord[0] < 1) {
            tempCoord[0] = Math.max(tempCoord[0],1);
        } else {
            tempCoord[0] = Math.min(tempCoord[0],COL-2);
        }
        if (tempCoord[1] < 1) {
            tempCoord[1] = Math.max(tempCoord[1],1);
        } else {
            tempCoord[1] = Math.min(tempCoord[1],ROW-2);
        }

        // set oldcoord wont happen as of now - useless btw
        setCurCoord(tempCoord);

    }

    /**
     *
     * @param column
     * @param row
     */
    public int[] setRobotImagePosition(int column, int row, float left, float top) {

        int[] newRobotLocation= {(int) ((column) * cellSize + left), (int) ((row - 2) * cellSize + top)};

        return newRobotLocation;
    }




    public int[] updateObstacleOnBoard(int x, int y) {
        int column = (int) Math.floor(x / cellSize);
        int row = (int) Math.floor(y / cellSize);

        if (column < 1) {
            column = Math.max(column,0);
        } else {
            column = Math.min(column,COL);
        }
        if (row< 1) {
            row = Math.max(row,0);
        } else {
            row = Math.min(row,ROW-1);
        }

        cells[column][row].setType("obstacle");

        setObstacleCoord(new int[] {column, row});

        int[] newObstacleDrag= {(int) (column * cellSize), (int) (row * cellSize), column-1, convertRow(row)-1};

        return newObstacleDrag;

    }

    /**
     * this one is using COORDINATES
     * @param originalX
     * @param originalY
     */
    public void removeObstacleUsingCoord(float originalX, float originalY) {
        int column = (int) Math.floor(originalX / cellSize);
        int row = (int) Math.floor(originalY / cellSize);
        removeObstacleCoord(new int[] {column, row});
    }

    public int[] getColRowFromXY(float x, float y, float mapLeft, float mapTop) {

        int column = (int) Math.floor((x - mapLeft + cellSize/2) / cellSize);
        int row = (int) Math.floor((y - mapTop + cellSize/2) / cellSize);

        int[] result = new int[] {column-1, convertRow(row)-1};
        return result;
    }





    /** its to make the old tracks
     * Saves the old robot coords and also resets the cell to the old one
     * (a little inefficient as most of the robot cells will still be robot)
     */
    public void setOldRobotCoord(int oldCol, int oldRow) {
        this.oldCoord[0] = oldCol;
        this.oldCoord[1] = oldRow;
        oldRow = this.convertRow(oldRow);
        for (int x = oldCol; x <= oldCol + 2; x++)
            for (int y = oldRow - 2; y <= oldRow; y++)
                cells[x][y].setType("explored");
    }
    

    /**
     * Called when create cell called --> to set the size of the cells --> so that it will fit the size?
     * COL+1 to make sure that the cell is full
     */
    private void calculateDimension() {
        this.setCellSize(getWidth()/(COL+1));
    }

    /**
     * cos row 5 is array[][15]
     * @param row
     * @return
     */
    public int convertRow(int row) {
        return (20 - row);
    }

    public int convertFacingToIndex(String facing) {
        for (int i = 0; i < robotFacingEnum.length; i++) {
            if (robotFacingEnum[i] == facing) {
                return i;
            }
        }
        System.out.println("ERROR in facing index");
        return -1;
    }

    public int convertFacingToRotation(String facing) {
        switch (facing) {
            case Constants.NORTH:
                return 0;
            case Constants.EAST:
                return 90;
            case Constants.SOUTH:
                return 180;
            case Constants.WEST:
                return 270;
            default:
                return 0;    // assume
        }
    }

    public String convertRotationToFacing(int rotation) {
        switch (rotation) {
            case 0:
                return Constants.NORTH;
            case 90:
                return Constants.EAST;
            case 180:
                return Constants.SOUTH;
            case 270:
                return Constants.WEST;
            default:
                return Constants.ERROR;    // assume
        }
    }

    public void reset() {
        for (int x = 0; x <= COL; x++)
            for (int y = 0; y <= ROW; y++)
                cells[x][y].setType("unexplored");
    }


    private void setCellSize(float cellSize) {
        Map.cellSize = cellSize;
    }

    public void setObstacleCoord(int[] coordinates) {
        obstacleCoord.add(coordinates);
    }


    /**
     * does the actual removing
     * @param coordinates
     */
    public void removeObstacleCoord(int[] coordinates) {
        //printObstacleCoord();

        cells[coordinates[0]][coordinates[1]].setType("unexplored");

        for (int i = 0; i < obstacleCoord.size(); i++) {
            if (Arrays.equals(obstacleCoord.get(i), coordinates)) {
                obstacleCoord.remove(i);
                break;
            }
        }
        //printObstacleCoord();
    }

    public void printObstacleCoord() {
        System.out.printf("total number of obstacles: %d \n", obstacleCoord.size());
        for (int x = 0; x < obstacleCoord.size(); x++) {
            System.out.printf("Obstacle %d |  X: %d, Y: %d\n", x+1, obstacleCoord.get(x)[0], obstacleCoord.get(x)[1]);
        }
    }

    public void removeAllObstacles() {
        while (obstacleCoord.size() >= 1) {
            cells[obstacleCoord.get(0)[0]][obstacleCoord.get(0)[1]].setType("unexplored");
            removeObstacleCoord(obstacleCoord.get(0));
        }
    }

    public ArrayList<int[]> getObstacleCoord() {
        return obstacleCoord;
    }

    public float getCellSize() { return cellSize; }
    public String getRobotMovement() {
        return robotMovement;
    }
    public String getRobotFacing() {
        return robotFacing;
    }


    public void setCanDrawRobot(boolean isDrawRobot) {
        canDrawRobot = isDrawRobot;
    }
    public boolean getCanDrawRobot() {
        return canDrawRobot;
    }
    private ArrayList<String[]> getArrowCoord() {
        return arrowCoord;
    }

    public void setRobotMovement(String direction) {
        robotMovement = direction;}

    public void setRobotReverse(Boolean reverse) {
        robotReverse = reverse;
    }

    public void setRobotFacing(String facing) {
        robotFacing = facing;}

    public void saveFacingWithRotation(int rotation) {
        robotFacing = robotFacingEnum[(int) (rotation / 90)];
    }

    /**
     * col then row
     * @param coordinates
     */
    public void setCurCoord(int[] coordinates) {curCoord = coordinates;}
    public void setCurCoord(int col, int row) {
        curCoord[0] = col;
        curCoord[1] = row;
    }

    public int[] getCurCoord() {
        return curCoord;
    }

    public int[] getOldRobotCoord() {
        return oldCoord;
    }

    public int getCol() {
        return COL;
    }


    //WAS USED FOR SERIALIZABLE
    //private void writeObject(ObjectOutputStream out) throws IOException {
    //    out.defaultWriteObject();
    //    out.writeObject(context);
    //    out.writeObject(attrs);
    //}

     //private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
     //    in.defaultReadObject();
     //   context = (Context) in.readObject();
     //   attrs = (AttributeSet) in.readObject();
    //}


}

