package sg.edu.ntu.scse.mdp.g7.mdpkotlin.entity

interface Protocol {
    companion object {
        const val MESSAGE_RECEIVE = 0
        const val MESSAGE_ERROR = 1
        const val CONNECTION_ERROR = 2
    }
}