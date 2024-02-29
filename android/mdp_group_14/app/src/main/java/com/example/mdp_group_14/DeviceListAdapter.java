package com.example.mdp_group_14;

import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import java.util.ArrayList;

public class DeviceListAdapter extends ArrayAdapter<BluetoothDevice> {

    private LayoutInflater mLayoutInflater;
    private ArrayList<BluetoothDevice> myDevices;
    private int mViewResourceId;

    public DeviceListAdapter(Context context, int tvResourceId, ArrayList<BluetoothDevice> devices) {
        super(context, tvResourceId, devices);
        this.myDevices = devices;
        mLayoutInflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        mViewResourceId = tvResourceId;
    }

    public View getView(int position, View convertView, ViewGroup parent) {
        Log.d("DeviceListAdapter", "Getting View");
        convertView = mLayoutInflater.inflate(mViewResourceId, null);

        BluetoothDevice device = myDevices.get(position);

        if (device != null) {
            TextView deviceName = convertView.findViewById(R.id.deviceName);
            TextView deviceAdress = convertView.findViewById(R.id.deviceAddress);

            if (deviceName != null) {
                deviceName.setText(device.getName());
            }
            if (deviceAdress != null) {
                deviceAdress.setText(device.getAddress());
            }
        }
        return convertView;
    }
}
