package sg.edu.ntu.scse.mdp.g7.mdpkotlin.util

import android.util.Log
import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject
import sg.edu.ntu.scse.mdp.g7.mdpkotlin.BuildConfig
import sg.edu.ntu.scse.mdp.g7.mdpkotlin.entity.Map
import java.math.BigInteger

class Parser(payload: String) {

    private var payload: JSONObject? = null
    var robotX = 0
    var robotY = 0
    var robotDir = ""
    var robotStatus = ""
    var lastImageID = ""
    private var currentPayload = ""

    val exploredMap = Array(Map.COLUMN) { Array(Map.ROW) { "" } }

    var validPayload = true

    init {
        val tmpPayload: JSONObject?
        this.currentPayload = payload

        try {
            tmpPayload = JSONObject(payload)
            this.payload = tmpPayload

            setRobot()
            setMDF()
        } catch (jsonEx: JSONException) {
            Log.d(TAG, "JSON EXCEPTION1")
            this.validPayload = false
        }
    }

    private fun setRobot() {
        if (!this.validPayload) return

        this.payload?.let {
            try {
                val robot = it.getJSONArray("pos")

                this.robotX = robot.getInt(0)
                this.robotY = robot.getInt(1)
                val angle = robot.getInt(2)

                this.robotDir = when (angle) {
                    0 -> "UP"
                    90 -> "RIGHT"
                    180 -> "DOWN"
                    270 -> "LEFT"
                    else -> "RIGHT" // DEFAULT RIGHT
                }
            } catch (jsonEx: JSONException) {
                Log.d(TAG, "JSON EXCEPTION")
                this.validPayload = false
            } catch (indexEx: IndexOutOfBoundsException) {
                Log.d(TAG, "INDEX OUT OF BOUNDS EXCEPTION")
                this.validPayload = false
            } catch (castEx: ClassCastException) {
                Log.d(TAG, "CLASS CAST EXCEPTION")
                this.validPayload = false
            }
        }
    }

    fun setStatus(): Boolean { return try { this.robotStatus = this.payload?.getString("status") ?: "Unknown"; true } catch (e: Exception) { Log.d(TAG, "EXCEPTION"); false } }

    fun processImage() {
        if (!this.validPayload) return

        this.payload?.let {
            try {
                val images = it.getJSONArray("imgs")
                var imgID = "0"
                var image: JSONArray?
                var imgX: Int
                var imgY: Int

                for (i in 0 until images.length()) {
                    image = images.getJSONArray(i)
                    imgX = image.getString(0).toInt()
                    imgY = image.getString(1).toInt()
                    imgID = image.getString(2)
                    hexImage += " ($imgID,$imgX,$imgY),"
                    this.exploredMap[imgX][imgY] = imgID
                }

                if (hexImage.isNotEmpty()) hexImage = hexImage.trimEnd(',') // Previously substring remove length-1
                this.lastImageID = imgID
            } catch (jsonEx: JSONException) {
                Log.d(TAG, "JSON EXCEPTION")
                this.validPayload = false
            } catch (indexEx: IndexOutOfBoundsException) {
                Log.d(TAG, "INDEX OUT OF BOUNDS EXCEPTION")
                this.validPayload = false
            } catch (castEx: ClassCastException) {
                Log.d(TAG, "CLASS CAST EXCEPTION")
                this.validPayload = false
            }
        }
    }

    private fun setMDF() {
        if (!this.validPayload) { Log.d("MDF", "Invalid Payload"); return }

        mdfPayload = this.currentPayload

        this.payload?.let {
            try {
                var exploredMDF = it.getString("expMDF")
                var obstacleMDF = it.getString("objMDF")

                /**
                 * Explored Portion
                 */
                hexMDF = exploredMDF
                exploredMDF = BigInteger(exploredMDF, 16).toString(2)
                exploredMDF = exploredMDF.substring(2, 302)
                if (DEBUG) Log.d("MDF", "Explored MDF: $exploredMDF")

                val exploredLength = exploredMDF.replace("0", "").length
                val obstaclePad = exploredLength % 4
                if (DEBUG) Log.d("MDF", "Obstacle Padding: $obstaclePad")

                hexExplored = obstacleMDF
                obstacleMDF = BigInteger(obstacleMDF, 16).toString(2)
                val obstacleMdfHexToBinLen = hexExplored.length * 4
                obstacleMDF = String.format("%${obstacleMdfHexToBinLen}s", obstacleMDF).replace(" ", "0")
                if (DEBUG) Log.d("MDF", "Obstacle MDF: $obstacleMDF")

                Log.d("MDF", "Parsing Explored String on map")
                for (i in 0 until Map.ROW) {
                    for (j in 0 until Map.COLUMN) {
                        val characterIndex = (i * Map.COLUMN) + j
                        exploredMap[j][i] = exploredMDF[characterIndex].toString()
                    }
                }
                if (DEBUG) printMapDbg()

                Log.d("MDF", "Parsing Obstacle String on map")
                var counter = 0
                for (i in 0 until Map.ROW) {
                    for (j in 0 until Map.COLUMN) {
                        if (exploredMap[j][i] == "1") {
                            if (obstacleMDF[counter] == '1') {
                                exploredMap[j][i] = "O"
                            }
                            counter++
                        }
                    }
                }
                if (DEBUG) printMapDbg()

            } catch (jsonEx: JSONException) {
                Log.d(TAG, "JSON EXCEPTION")
                this.validPayload = false
            } catch (indexEx: IndexOutOfBoundsException) {
                Log.d(TAG, "INDEX OUT OF BOUNDS EXCEPTION")
                this.validPayload = false
            } catch (castEx: ClassCastException) {
                Log.d(TAG, "CLASS CAST EXCEPTION")
                this.validPayload = false
            }
        }
    }

    private fun printMapDbg() {
        Log.d("MDF-Map", "=========================================")
        for (i in 0 until Map.ROW) {
            var s = ""
            for (j in 0 until Map.COLUMN) { s += exploredMap[j][i] }
            Log.d("MDF-Map", s)
        }
        Log.d("MDF-Map", "=========================================")
    }

    companion object {
        const val TAG = "Parser"
        val DEBUG = BuildConfig.DEBUG

        var hexMDF = "0x0000000000000000"
        var hexExplored = "0x0000000000000000"
        var hexImage = ""
        var mdfPayload = ""
    }
}