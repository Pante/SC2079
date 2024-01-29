package sg.edu.ntu.scse.mdp.g7.mdpkotlin

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.TextView

class StringAdapter(context: Context, private val stringList: Array<String>) : BaseAdapter() {
    private val inflater: LayoutInflater = LayoutInflater.from(context)
    init { stringList.reverse() }

    override fun getCount(): Int { return stringList.size }
    override fun getItem(i: Int): String { return stringList[i] }
    override fun getItemId(i: Int): Long { return 0 }
    override fun getView(i: Int, view: View?, viewGroup: ViewGroup?): View {
        var viewObj = view
        val holder = if (viewObj == null) StringViewHolder() else viewObj.tag as StringViewHolder
        if (viewObj == null) {
            viewObj = inflater.inflate(android.R.layout.simple_list_item_1, null)
            holder.main = viewObj.findViewById(android.R.id.text1)
            viewObj.tag = holder
        }

        holder.main?.text = stringList[i]
        return viewObj!!
    }

    class StringViewHolder {
        var main: TextView? = null
    }
}