@file:Suppress("unused")

package sg.edu.ntu.scse.mdp.g7.mdpkotlin.util

import java.text.DecimalFormat

object Cmd {
    /**
     * Utility Variables
     */
    private val coordinatesFormatter = DecimalFormat("00")

    /**
     * Exploration/Fastest Path
     */
    const val EXPLORATION_START = "ex"
    const val FASTEST_PATH_START = "fp"
    const val STOP = "T"

    /**
     * Robot movements
     */
    const val DIRECTION_LEFT = "A"
    const val DIRECTION_RIGHT = "D"
    const val DIRECTION_UP = "W"

    /**
     * Map Status
     */
    const val CLEAR = "clr"

    @JvmStatic
    fun getWayPoint(x: Int, y: Int): String { return "XWP${coordinatesFormatter.format(x)}${coordinatesFormatter.format(y)}" }

    @JvmStatic
    fun getStartPoint(x: Int, y: Int): String { return "XWP${coordinatesFormatter.format(x)}${coordinatesFormatter.format(y)}" }
}