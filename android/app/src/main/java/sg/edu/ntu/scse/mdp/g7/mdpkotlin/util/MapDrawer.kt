package sg.edu.ntu.scse.mdp.g7.mdpkotlin.util

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Rect
import android.util.AttributeSet
import android.util.Log
import android.view.View

import sg.edu.ntu.scse.mdp.g7.mdpkotlin.entity.Map
import sg.edu.ntu.scse.mdp.g7.mdpkotlin.entity.Robot

@Suppress("unused")
class MapDrawer(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {

    /**
     * helper variables
     */
    private lateinit var gridPaint: Paint
    private lateinit var gridPaintBorder: Paint
    private lateinit var gridPaintCoords: Paint
    private lateinit var robotPaint: Paint
    private lateinit var directionPaint: Paint
    private lateinit var exploredPaint: Paint
    private lateinit var exploredPaintBorder: Paint

    private lateinit var wayPointPaint: Paint
    private lateinit var wayPointPaintBorder: Paint
    private lateinit var startPointPaint: Paint
    private lateinit var startPointPaintBorder: Paint
    private lateinit var endPointPaint: Paint
    private lateinit var endPointPaintBorder: Paint

    private lateinit var selectionPaint: Paint
    private lateinit var selectionPaintBorder: Paint
    private lateinit var selectionTextPaint: Paint

    private lateinit var obstaclePaint: Paint
    private lateinit var obstaclePaintBorder: Paint
    private lateinit var obstacleTextPaint: Paint
    
    init {
        Robot_X = Robot.START_POS_X
        Robot_Y = Robot.START_POS_Y
        direction = Robot.START_DIRECTION
        exploredPath = Array(Map.COLUMN) { Array(Map.ROW) { "0" } }
        init()
        initMap()
    }
    
    private fun init() {
        gridPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        gridPaintBorder = Paint(Paint.ANTI_ALIAS_FLAG)
        gridPaintCoords = Paint(Paint.ANTI_ALIAS_FLAG)
        robotPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        directionPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        exploredPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        exploredPaintBorder = Paint(Paint.ANTI_ALIAS_FLAG)
        wayPointPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        wayPointPaintBorder = Paint(Paint.ANTI_ALIAS_FLAG)
        startPointPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        startPointPaintBorder = Paint(Paint.ANTI_ALIAS_FLAG)
        endPointPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        endPointPaintBorder = Paint(Paint.ANTI_ALIAS_FLAG)
        selectionPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        selectionPaintBorder = Paint(Paint.ANTI_ALIAS_FLAG)
        selectionTextPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        obstaclePaint = Paint(Paint.ANTI_ALIAS_FLAG)
        obstaclePaintBorder = Paint(Paint.ANTI_ALIAS_FLAG)
        obstacleTextPaint = Paint(Paint.ANTI_ALIAS_FLAG)

        gridPaint.style = Paint.Style.FILL
        gridPaint.color = Color.parseColor("#87cefa")
        //gridPaint.setColor(Color.parseColor("#3A96C2"));
        gridPaintBorder.style = Paint.Style.STROKE
        gridPaintBorder.color = Color.parseColor("#eeeeee")

        gridPaintCoords.style = Paint.Style.STROKE
        gridPaintCoords.color = Color.parseColor("#000000")
        gridPaintCoords.textSize = 15f

        robotPaint.style = Paint.Style.FILL
        robotPaint.color = Color.parseColor("#FF7F50")

        directionPaint.style = Paint.Style.STROKE
        directionPaint.color = Color.parseColor("#424242")

        exploredPaint.style = Paint.Style.FILL
        exploredPaint.color = Color.parseColor("#f5f5f5")
        exploredPaintBorder.style = Paint.Style.STROKE
        exploredPaintBorder.color = Color.parseColor("#3A96C2")

        wayPointPaint.style = Paint.Style.FILL
        wayPointPaint.color = Color.parseColor("#e53935")
        wayPointPaintBorder.style = Paint.Style.STROKE
        wayPointPaintBorder.color = Color.parseColor("#f5f5f5")

        startPointPaint.style = Paint.Style.FILL
        startPointPaint.color = Color.parseColor("#607d8b")
        startPointPaintBorder.style = Paint.Style.STROKE
        startPointPaintBorder.color = Color.parseColor("#f5f5f5")

        endPointPaint.style = Paint.Style.FILL
        endPointPaint.color = Color.parseColor("#009688")
        endPointPaintBorder.style = Paint.Style.STROKE
        endPointPaintBorder.color = Color.parseColor("#f5f5f5")

        selectionPaint.style = Paint.Style.FILL
        selectionPaint.color = Color.parseColor("#9ccc65")
        selectionPaintBorder.style = Paint.Style.STROKE
        selectionPaintBorder.color = Color.parseColor("#f5f5f5")

        selectionTextPaint.style = Paint.Style.STROKE
        selectionTextPaint.color = Color.parseColor("#f5f5f5")
        selectionTextPaint.textSize = 100f

        obstaclePaint.style = Paint.Style.FILL
        obstaclePaint.color = Color.parseColor("#212121")
        obstaclePaintBorder.style = Paint.Style.STROKE
        obstaclePaintBorder.color = Color.parseColor("#f5f5f5")

        obstacleTextPaint.style = Paint.Style.STROKE
        obstacleTextPaint.color = Color.parseColor("#f5f5f5")
        obstacleTextPaint.textSize = 22f

        if (this.tag != null) {
            Log.d("Tag", if (this.tag != null) this.tag as String else "Default")
            gridDimensions = if ((this.tag as String).equals("phone", ignoreCase = true)) GRID_DIMEN_PHABLET else GRID_DIMEN_TABLET
        }
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
        setMeasuredDimension(widthMeasureSpec, heightMeasureSpec)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        Log.d(TAG, "DRAWING GRID MAP")

        drawMap(canvas)
        if (!selectWayPoint && !selectStartPoint) {
            drawExploredMap(canvas)
            drawStartPoint(canvas)
            drawEndPoint(canvas)
            drawWayPoint(canvas)
            drawRobot(canvas)
        } else {
            drawStartPoint(canvas)
            drawEndPoint(canvas)
            drawSelectionMap(canvas)

            if (selectWayPoint) drawWayPoint(canvas)
            else if (selectStartPoint) drawRobot(canvas)
        }
    }

    private fun drawMap(canvas: Canvas) {
        for (i in 0 until Map.COLUMN) {
            for (j in 0 until Map.ROW) {
                val left = i * gridDimensions
                val top = j * gridDimensions

                val rectangle = Rect(left, top, left + gridDimensions, top + gridDimensions)
                canvas.drawRect(rectangle, gridPaint)
                canvas.drawRect(rectangle, gridPaintBorder)
            }
        }
    }

    private fun drawExploredMap(canvas: Canvas) {
        for (i in 0 until Map.COLUMN) {
            for (j in 0 until Map.ROW) {
                val left = i * gridDimensions
                val top = j * gridDimensions

                if (exploredPath[i][j] == "1") {
                    val rectangle = Rect(left, top, left + gridDimensions, top + gridDimensions)
                    canvas.drawRect(rectangle, exploredPaint)
                    canvas.drawRect(rectangle, exploredPaintBorder)
                } else if (exploredPath[i][j] != "0") {
                    Log.d(TAG, exploredPath[i][j])
                    drawObstacles(canvas, left, top, exploredPath[i][j])
                }
            }
        }
    }

    private fun drawRobot(canvas: Canvas) {
        val gridX: Float = ((Robot_X * gridDimensions) + ((Robot_X + 1) * gridDimensions)) / 2f
        val gridY: Float = ((Robot_Y * gridDimensions) + ((Robot_Y + 1) * gridDimensions)) / 2f
        canvas.drawCircle(gridX, gridY, (gridDimensions * 3 / 2f), robotPaint)
        when (direction) {
            "Right" -> canvas.drawLine(gridX, gridY, ((Robot_X + 2f) * gridDimensions), gridY, directionPaint)
            "Left" -> canvas.drawLine(gridX, gridY, ((Robot_X - 1f) * gridDimensions), gridY, directionPaint)
            "Up" -> canvas.drawLine(gridX, gridY, gridX, ((Robot_Y - 1f) * gridDimensions), directionPaint)
            "Down" -> canvas.drawLine(gridX, gridY, gridX, ((Robot_Y + 2f) * gridDimensions), directionPaint)
        }
    }

    private fun drawStartPoint(canvas: Canvas) {
        var left = Start_Point_X * gridDimensions
        var top = Start_Point_Y * gridDimensions
        var rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, startPointPaint)
        canvas.drawRect(rect, startPointPaintBorder)

        left = (Start_Point_X + 1) * gridDimensions
        top = Start_Point_Y * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, startPointPaint)
        canvas.drawRect(rect, startPointPaintBorder)

        left = (Start_Point_X - 1) * gridDimensions
        top = Start_Point_Y * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, startPointPaint)
        canvas.drawRect(rect, startPointPaintBorder)

        left = Start_Point_X * gridDimensions
        top = (Start_Point_Y + 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, startPointPaint)
        canvas.drawRect(rect, startPointPaintBorder)

        left = Start_Point_X * gridDimensions
        top = (Start_Point_Y - 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, startPointPaint)
        canvas.drawRect(rect, startPointPaintBorder)

        left = (Start_Point_X - 1) * gridDimensions
        top = (Start_Point_Y + 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, startPointPaint)
        canvas.drawRect(rect, startPointPaintBorder)

        left = (Start_Point_X - 1) * gridDimensions
        top = (Start_Point_Y - 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, startPointPaint)
        canvas.drawRect(rect, startPointPaintBorder)

        left = (Start_Point_X + 1) * gridDimensions
        top = (Start_Point_Y + 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, startPointPaint)
        canvas.drawRect(rect, startPointPaintBorder)

        left = (Start_Point_X + 1) * gridDimensions
        top = (Start_Point_Y - 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, startPointPaint)
        canvas.drawRect(rect, startPointPaintBorder)
    }

    private fun drawEndPoint(canvas: Canvas) {
        var left = End_Point_X * gridDimensions
        var top = End_Point_Y * gridDimensions
        var rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, endPointPaint)
        canvas.drawRect(rect, endPointPaintBorder)

        left = (End_Point_X + 1) * gridDimensions
        top = End_Point_Y * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, endPointPaint)
        canvas.drawRect(rect, endPointPaintBorder)

        left = (End_Point_X - 1) * gridDimensions
        top = End_Point_Y * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, endPointPaint)
        canvas.drawRect(rect, endPointPaintBorder)

        left = End_Point_X * gridDimensions
        top = (End_Point_Y + 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, endPointPaint)
        canvas.drawRect(rect, endPointPaintBorder)

        left = End_Point_X * gridDimensions
        top = (End_Point_Y - 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, endPointPaint)
        canvas.drawRect(rect, endPointPaintBorder)

        left = (End_Point_X - 1) * gridDimensions
        top = (End_Point_Y + 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, endPointPaint)
        canvas.drawRect(rect, endPointPaintBorder)

        left = (End_Point_X - 1) * gridDimensions
        top = (End_Point_Y - 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, endPointPaint)
        canvas.drawRect(rect, endPointPaintBorder)

        left = (End_Point_X + 1) * gridDimensions
        top = (End_Point_Y + 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, endPointPaint)
        canvas.drawRect(rect, endPointPaintBorder)

        left = (End_Point_X + 1) * gridDimensions
        top = (End_Point_Y - 1) * gridDimensions
        rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, endPointPaint)
        canvas.drawRect(rect, endPointPaintBorder)
    }

    private fun drawWayPoint(canvas: Canvas) {
        val left = Way_Point_X * gridDimensions
        val top = Way_Point_Y * gridDimensions
        val rect = Rect(left, top, left + gridDimensions, top + gridDimensions)
        canvas.drawRect(rect, wayPointPaint)
        canvas.drawRect(rect, wayPointPaintBorder)
    }

    private fun drawSelectionMap(canvas: Canvas) {
        for (i in 0 until Map.VIRTUAL_COLUMN) {
            for (j in 0 until Map.VIRTUAL_ROW) {
                val left = i * gridDimensions
                val top = j * gridDimensions

                if (isSurroundingObstacle(i, j)) {
                    val rectangle = Rect(left, top, left + gridDimensions, top + gridDimensions)
                    canvas.drawRect(rectangle, selectionPaint)
                    canvas.drawRect(rectangle, selectionPaintBorder)
                    canvas.drawText("{$i,${Map.VIRTUAL_ROW-j})", left.toFloat(), top + gridDimensions - 10f, gridPaintCoords)
                }
            }
        }

        val left = 3f * gridDimensions
        var top = 9f * gridDimensions
        if (selectWayPoint) canvas.drawText("WAY", left, top, selectionTextPaint)
        else if (selectStartPoint) canvas.drawText("START", left, top, selectionTextPaint)

        top = 12f * gridDimensions
        canvas.drawText("POINT", left, top, selectionTextPaint)
    }

    private fun drawObstacles(canvas: Canvas, left: Int, top: Int, obstacle: String) {
        val rectangle = Rect(left, top, left + gridDimensions, top + gridDimensions)
        val ttop = top + 25
        val tleft = left + 6

        canvas.drawRect(rectangle, obstaclePaint)
        canvas.drawRect(rectangle, obstaclePaintBorder)
        when (obstacle) {
            "1" -> canvas.drawText("01", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "2" -> canvas.drawText("02", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "3" -> canvas.drawText("03", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "4" -> canvas.drawText("04", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "5" -> canvas.drawText("05", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "6" -> canvas.drawText("06", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "7" -> canvas.drawText("07", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "8" -> canvas.drawText("08", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "9" -> canvas.drawText("09", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "10" -> canvas.drawText("10", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "11" -> canvas.drawText("11", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "12" -> canvas.drawText("12", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "13" -> canvas.drawText("13", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "14" -> canvas.drawText("14", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
            "15" -> canvas.drawText("15", tleft.toFloat(), ttop.toFloat(), obstacleTextPaint)
        }
    }

    companion object {
        // Some constants for compatibility reasons
        const val GRID_DIMEN_TABLET = 36 // large (N7/Acer Tablet)
        const val GRID_DIMEN_PHABLET = 50 // regular (Phones with high dpi, P4XL)
        
        private const val TAG = "Grid"
        var gridDimensions: Int = GRID_DIMEN_TABLET

        /**
         * state variables
         */
        var Robot_X: Int = Robot.START_POS_X
        var Robot_Y: Int = Robot.START_POS_Y
        var Start_Point_X: Int = Map.START_POINT_X
        var Start_Point_Y: Int = Map.START_POINT_Y
        var Way_Point_X: Int = Map.WAY_POINT_X
        var Way_Point_Y: Int = Map.WAY_POINT_Y
        const val End_Point_X: Int = Map.END_POINT_X
        const val End_Point_Y: Int = Map.END_POINT_Y
        var direction: String = Robot.START_DIRECTION
        var selectStartPoint = false
        var selectWayPoint = false

        private var exploredPath = Array(Map.COLUMN) { Array(Map.ROW) { "0" } }

        @JvmStatic
        private fun initMap() {
            for (i in 0 until Map.COLUMN) {
                for (j in 0 until Map.ROW) {
                    exploredPath[i][j] = "0"
                }
            }
            updateExplored()
        }

        @JvmStatic
        fun moveRight() {
            direction = when (direction) {
                "Right" -> "Down"
                "Left" -> "Up"
                "Up" -> "Right"
                "Down" -> "Left"
                else -> "Up"
            }
        }

        @JvmStatic
        fun moveLeft() {
            direction = when (direction) {
                "Right" -> "Up"
                "Left" -> "Down"
                "Up" -> "Left"
                "Down" -> "Right"
                else -> "Up"
            }
        }

        @JvmStatic
        fun moveUp() {
            if (direction == "Right") { if (Robot_X + 1 != Map.VIRTUAL_COLUMN && isSurroundingObstacle(Robot_X + 1, Robot_Y)) Robot_X++ }
            else if (direction == "Left" && isSurroundingObstacle(Robot_X - 1, Robot_Y)) { Log.d(TAG, "L: ${Robot_X - 1}"); if (Robot_X - 1 != 0) Robot_X-- }
            else if (direction == "Up" && isSurroundingObstacle(Robot_X, Robot_Y - 1)) { Log.d(TAG, "U: ${Robot_X - 1}"); if (Robot_Y - 1 != 0) Robot_Y-- }
            else if (direction == "Down" && isSurroundingObstacle(Robot_X, Robot_Y + 1)) { Log.d(TAG, "D: ${Robot_X - 1}"); if (Robot_Y + 1 != Map.VIRTUAL_ROW) Robot_Y++ }
            updateExplored()
        }

        @JvmStatic
        fun updateCoordinates(x_axis: Int, y_axis: Int, dir: String) {
            if (!validMidpoint(x_axis, y_axis)) return
            Log.d(TAG, "X Axis : $x_axis Y Axis: $y_axis")
            val newYAxis = invertYAxis(y_axis)

            Robot_X = x_axis
            Robot_Y = newYAxis
            Log.d(TAG, "$Robot_X, $Robot_Y")

            direction = when (dir) {
                "UP" -> "Up"
                "DOWN" -> "Down"
                "LEFT" -> "Left"
                "RIGHT" -> "Right"
                else -> "Right"
            }
            updateExplored()
        }

        @JvmStatic
        fun updateSelection(x_axis: Int, y_axis: Int) {
            if (isSurroundingObstacle(x_axis, y_axis)) {
                if (selectStartPoint) {
                    Robot_X = x_axis
                    Robot_Y = y_axis
                } else if (selectWayPoint) {
                    Way_Point_X = x_axis
                    Way_Point_Y = y_axis
                }
            }
        }

        @JvmStatic
        private fun updateExplored() {
            exploredPath[Robot_X][Robot_Y] = "1"
            exploredPath[Robot_X-1][Robot_Y] = "1"
            exploredPath[Robot_X+1][Robot_Y] = "1"

            exploredPath[Robot_X][Robot_Y+1] = "1"
            exploredPath[Robot_X][Robot_Y-1] = "1"

            exploredPath[Robot_X-1][Robot_Y-1] = "1"
            exploredPath[Robot_X-1][Robot_Y+1] = "1"

            exploredPath[Robot_X+1][Robot_Y-1] = "1"
            exploredPath[Robot_X+1][Robot_Y+1] = "1"
        }

        @JvmStatic fun validMidpoint(x_axis: Int, y_axis: Int): Boolean { return (x_axis >= 1 && x_axis < Map.VIRTUAL_COLUMN) && (y_axis >= 1 && y_axis < Map.VIRTUAL_ROW) }

        @JvmStatic
        fun setGrid(exploredMap: Array<Array<String>>) {
            for (i in 0 until Map.ROW) {
                for (j in 0 until Map.COLUMN) {
                    exploredPath[j][i] = exploredMap[j][invertYAxis(i)]
                }
            }
        }

        @JvmStatic fun invertYAxis(y_axis: Int): Int { return Map.VIRTUAL_ROW - y_axis }
        @JvmStatic fun setSelectWayPoint() { selectWayPoint = !selectWayPoint }
        @JvmStatic fun setSelectStartPoint() { selectStartPoint = !selectStartPoint }
        @JvmStatic fun updateStartPoint() { updateExplored() }
        @JvmStatic fun getRobotPosition(): String { return "$Robot_X,${invertYAxis(Robot_Y)}" }
        @JvmStatic fun getWayPoint(): String { return "$Way_Point_X,${invertYAxis(Way_Point_Y)}" }
        @JvmStatic fun getWayPointYInvert(): Int { return invertYAxis(Way_Point_Y) }
        @JvmStatic fun getStartPoint(): String { return "$Start_Point_X,${invertYAxis(Start_Point_Y)}" }
        @JvmStatic fun getStartPointYInvert(): Int { return invertYAxis(Start_Point_Y) }
        @JvmStatic fun getRobotInvertY(): Int { return invertYAxis(Robot_Y) }
        @JvmStatic fun resetMap() { initMap() }

        @JvmStatic
        fun getRotationDir(): Int {
            return when (direction) {
                "Up" -> 0
                "Down" -> 180
                "Left" -> 270
                "Right" -> 90
                else -> 90
            }
        }

        @JvmStatic
        fun isSurroundingObstacle(x_axis: Int, y_axis: Int): Boolean {
            // just make sure there is no surround obstacles, inclusive of itself
            if (!validMidpoint(x_axis, y_axis)) return false

            return if (exploredPath[x_axis][y_axis] != "1" && exploredPath[x_axis][y_axis] != "0") false
            else if (exploredPath[x_axis][y_axis + 1] != "1" && exploredPath[x_axis][y_axis + 1] != "0") false
            else if (exploredPath[x_axis][y_axis - 1] != "1" && exploredPath[x_axis][y_axis - 1] != "0") false
            else if (exploredPath[x_axis + 1][y_axis] != "1" && exploredPath[x_axis + 1][y_axis] != "0") false
            else if (exploredPath[x_axis + 1][y_axis + 1] != "1" && exploredPath[x_axis + 1][y_axis + 1] != "0") false
            else if (exploredPath[x_axis + 1][y_axis - 1] != "1" && exploredPath[x_axis + 1][y_axis - 1] != "0") false
            else if (exploredPath[x_axis - 1][y_axis] != "1" && exploredPath[x_axis - 1][y_axis] != "0") false
            else if (exploredPath[x_axis - 1][y_axis + 1] != "1" && exploredPath[x_axis - 1][y_axis + 1] != "0") false
            else !(exploredPath[x_axis - 1][y_axis - 1] != "1" && exploredPath[x_axis - 1][y_axis - 1] != "0")
        }

    }
}