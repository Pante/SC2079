package sg.edu.ntu.scse.mdp.g7.mdpkotlin

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.TextView
import sg.edu.ntu.scse.mdp.g7.mdpkotlin.entity.Device

class DeviceAdapter(context: Context, private val deviceList: ArrayList<Device>) : BaseAdapter() {
    private val inflater: LayoutInflater = LayoutInflater.from(context)

    override fun getCount(): Int { return deviceList.size }
    override fun getItem(i: Int): Any? { return null }
    override fun getItemId(i: Int): Long { return 0 }
    override fun getView(i: Int, view: View?, viewGroup: ViewGroup?): View {
        var viewObj: View? = view
        val holder = if (viewObj == null) DeviceViewHolder() else viewObj.tag as DeviceViewHolder
        if (viewObj == null) {
            viewObj = inflater.inflate(R.layout.listview_device, null)
            holder.device = viewObj.findViewById(R.id.textView)
            holder.macAddr = viewObj.findViewById(R.id.textView2)
            viewObj.tag = holder
        }

        holder.device?.text = deviceList[i].deviceName
        holder.macAddr?.text = deviceList[i].macAddr

        return viewObj!!
    }

    class DeviceViewHolder {
        var device: TextView? = null
        var macAddr: TextView? = null
    }
}