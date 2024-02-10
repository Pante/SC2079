package com.example.mdpandroidcontroller;

import android.Manifest;
import android.app.ProgressDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothHeadset;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentManager;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Set;
import java.util.UUID;

public class Connect extends AppCompatActivity {

    private static final String TAG = "Connect";

    public ArrayList<BluetoothDevice> myBTDevicesArrayList = new ArrayList<>();
    public ArrayList<BluetoothDevice> myBTPairedDevicesArrayList = new ArrayList<>();

    public DeviceListAdapter myDeviceListAdapter;
    public DeviceListAdapter myPairedDeviceListAdapter;

    BluetoothConnectionService myBluetoothConnection;

    //Bounded Device
    static BluetoothDevice myBTDevice;
    BluetoothDevice myBTConnectionDevice;

    BluetoothAdapter myBluetoothAdapter;

    //VIEWS ANN BUTTONS
    ListView lvNewDevices;
    static ListView lvPairedDevices;
    ImageButton btnSend;
    EditText sendMessage;
    Button btnSearch;
    StringBuilder incomingMsg;
    TextView incomingMsgTextView;
    Button bluetoothConnect;
    TextView deviceSearchStatus;
    ProgressDialog myProgressDialog, connectionDialog;
    TextView pairedDeviceText;
    Intent connectIntent;

    //UUID
    public static final UUID myUUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    public static BluetoothDevice getBluetoothDevice() {
        return myBTDevice;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connect);


        bluetoothConnect = findViewById(R.id.connectBtn);
        btnSearch = findViewById(R.id.searchBtn);
        lvNewDevices = findViewById(R.id.listNewDevice);
        lvPairedDevices = findViewById(R.id.pairedDeviceList);
        btnSend = findViewById(R.id.btSend);
        sendMessage = findViewById(R.id.messageText);
        incomingMsgTextView = findViewById(R.id.incomingText);
        deviceSearchStatus = findViewById(R.id.deviceSearchStatus);
        pairedDeviceText = findViewById(R.id.pairedDeviceText);
        incomingMsg = new StringBuilder();
        myBTDevice = null;


        //REGISTER BROADCAST RECEIVER FOR IMCOMING MSG
        LocalBroadcastManager.getInstance(this).registerReceiver(btConnectionReceiver, new IntentFilter("btConnectionStatus"));

        //REGISTER BROADCAST RECEIVER FOR IMCOMING MSG
        LocalBroadcastManager.getInstance(this).registerReceiver(myReceiver, new IntentFilter("IncomingMsg"));

        //REGISTER BROADCAST WHEN BOND STATE CHANGES (E.G PAIRING)
        IntentFilter bondFilter = new IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED);
        registerReceiver(bondingBroadcastReceiver, bondFilter);

        //LISTENER FOR BLUETOOTH CONNECTION STATUS UPDATE
      /*  IntentFilter connectionFilter = new IntentFilter();
        connectionFilter.addAction(BluetoothDevice.ACTION_ACL_CONNECTED);
        connectionFilter.addAction(BluetoothDevice.ACTION_ACL_DISCONNECT_REQUESTED);
        connectionFilter.addAction(BluetoothDevice.ACTION_ACL_DISCONNECTED);
        registerReceiver(btConnectionReceiver, connectionFilter);*/

        //REGISTER DISCOVERABILITY BROADCAST RECEIVER
        IntentFilter intentFilter = new IntentFilter(myBluetoothAdapter.ACTION_SCAN_MODE_CHANGED);
        registerReceiver(discoverabilityBroadcastReceiver, intentFilter);

        //REGISTER ENABLE/DISABLE BT BROADCAST RECEIVER
        IntentFilter BTIntent = new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED);
        registerReceiver(enableBTBroadcastReceiver, BTIntent);

        //REGISTER DISCOVERED DEVICE BROADCAST RECEIVER
        IntentFilter discoverDevicesIntent = new IntentFilter(BluetoothDevice.ACTION_FOUND);
        registerReceiver(discoveryBroadcastReceiver, discoverDevicesIntent);

        //REGISTER START DISCOVERING BROADCAST RECEIVER
        IntentFilter discoverStartedIntent = new IntentFilter(BluetoothAdapter.ACTION_DISCOVERY_STARTED);
        registerReceiver(discoveryStartedBroadcastReceiver, discoverStartedIntent);

        //REGISTER END DISCOVERING BROADCAST RECEIVER
        IntentFilter discoverEndedIntent = new IntentFilter(BluetoothAdapter.ACTION_DISCOVERY_FINISHED);
        registerReceiver(discoveryEndedBroadcastReceiver, discoverEndedIntent);

        myBTDevicesArrayList = new ArrayList<>();
        myBTPairedDevicesArrayList = new ArrayList<>();
        myBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();


        //ONCLICK LISTENER FOR PAIRED DEVICE LIST
        lvPairedDevices.setOnItemClickListener(
                new AdapterView.OnItemClickListener() {
                    @Override
                    public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {

                        //CANCEL DEVICE SEARCH DISCOVERY
                        if (ActivityCompat.checkSelfPermission(Connect.this, android.Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) {
                            // TODO: Consider calling
                            //    ActivityCompat#requestPermissions
                            // here to request the missing permissions, and then overriding
                            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                            //                                          int[] grantResults)
                            // to handle the case where the user grants the permission. See the documentation
                            // for ActivityCompat#requestPermissions for more details.
                        }
                        myBluetoothAdapter.cancelDiscovery();

                        myBTDevice = myBTPairedDevicesArrayList.get(i);

                        //UnSelect Search Device List
                        lvNewDevices.setAdapter(myDeviceListAdapter);

                        Log.d(TAG, "onItemClick: Paired Device = " + myBTPairedDevicesArrayList.get(i).getName());
                        Log.d(TAG, "onItemClick: DeviceAddress = " + myBTPairedDevicesArrayList.get(i).getAddress());

                    }
                }
        );

        //ONCLICK LISTENER FOR SEARCH DEVICE LIST
        lvNewDevices.setOnItemClickListener(
                new AdapterView.OnItemClickListener() {
                    @Override
                    public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {

                        //CANCEL DEVICE SEARCH DISCOVERY
                        if (ActivityCompat.checkSelfPermission(Connect.this, android.Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) {
                            // TODO: Consider calling
                            //    ActivityCompat#requestPermissions
                            // here to request the missing permissions, and then overriding
                            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                            //                                          int[] grantResults)
                            // to handle the case where the user grants the permission. See the documentation
                            // for ActivityCompat#requestPermissions for more details.
                        }
                        myBluetoothAdapter.cancelDiscovery();

                        Log.d(TAG, "onItemClick: Item Selected");

                        String deviceName = myBTDevicesArrayList.get(i).getName();
                        String deviceAddress = myBTDevicesArrayList.get(i).getAddress();

                        //UnSelect Paired Device List
                        lvPairedDevices.setAdapter(myPairedDeviceListAdapter);


                        Log.d(TAG, "onItemClick: DeviceName = " + deviceName);
                        Log.d(TAG, "onItemClick: DeviceAddress = " + deviceAddress);

                        //CREATE BOND if > JELLY BEAN
                        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.JELLY_BEAN_MR2) {
                            Log.d(TAG, "Trying to pair with: " + deviceName);

                            //CREATE BOUND WITH SELECTED DEVICE
                            myBTDevicesArrayList.get(i).createBond();

                            //ASSIGN SELECTED DEVICE INFO TO myBTDevice
                            myBTDevice = myBTDevicesArrayList.get(i);


                        }

                    }
                }
        );

        //ONCLICKLISTENER FOR SEARCH BUTTON
        btnSearch.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {
                Log.d(TAG, "onClick: search button");
                enableBT();
                myBTDevicesArrayList.clear();


            }
        });

        //ONCLICKLISTENER FOR CONNECT BUTTON
        bluetoothConnect.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {

                if (myBTDevice == null) {

                    if (ActivityCompat.checkSelfPermission(Connect.this, Manifest.permission.BLUETOOTH_ADMIN) != PackageManager.PERMISSION_GRANTED) {
                        // TODO: Consider calling
                        //    ActivityCompat#requestPermissions
                        // here to request the missing permissions, and then overriding
                        //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                        //                                          int[] grantResults)
                        // to handle the case where the user grants the permission. See the documentation
                        // for ActivityCompat#requestPermissions for more details.
                    }

                    Toast.makeText(Connect.this, "No Paired Device! Please Search/Select a Device.",
                            Toast.LENGTH_LONG).show();
                } else if (myBluetoothAdapter.getProfileConnectionState(BluetoothHeadset.HEADSET) == BluetoothAdapter.STATE_CONNECTED) {
                    Toast.makeText(Connect.this, "Bluetooth Already Connected",
                            Toast.LENGTH_LONG).show();
                } else {
                    Log.d(TAG, "onClick: connect button");

                    //CREATE BOUND WITH SELECTED DEVICE
                /*    if (Build.VERSION.SDK_INT > Build.VERSION_CODES.JELLY_BEAN_MR2) {
                        Log.d(TAG, "Rebond");
                        myBTDevice.createBond();
                    }*/

                    //START CONNECTION WITH THE BOUNDED DEVICE

                    Intent intent1 = new Intent();
                    intent1.setAction("com.example.mdpandroidcontroller.btConnectionStatus");
                    intent1.setFlags(Intent.FLAG_INCLUDE_STOPPED_PACKAGES);
                    sendBroadcast(intent1);

                    startBTConnection(myBTDevice, myUUID);
                }
                lvPairedDevices.setAdapter(myPairedDeviceListAdapter);
            }
        });

        //ONCLICKLISTENER FOR SEND BUTTON
        btnSend.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {
                byte[] bytes = sendMessage.getText().toString().getBytes(Charset.defaultCharset());
                BluetoothChat.writeMsg(bytes);
                sendMessage.setText("");
            }
        });
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        //getMenuInflater().inflate(R.menu.connect, menu);
        return true;
    }

    /*@Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.main:
                Intent intent = new Intent(Connect.this, MainActivity.class);
                intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
                startActivity(intent);
        }

        switch (item.getItemId()) {
            case R.id.reconfigure:
                Intent intent = new Intent(Connect.this, Reconfigure.class);
                //intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
                startActivity(intent);
        }
        return super.onOptionsItemSelected(item);
    }*/

    @Override
    protected void onDestroy() {
        Log.d(TAG, "ConnectActivity: onDestroyed: destroyed");
        super.onDestroy();
        unregisterReceiver(discoverabilityBroadcastReceiver);
        unregisterReceiver(discoveryBroadcastReceiver);
        unregisterReceiver(bondingBroadcastReceiver);
        //unregisterReceiver(btConnectionReceiver);
        unregisterReceiver(discoveryStartedBroadcastReceiver);
        unregisterReceiver(discoveryEndedBroadcastReceiver);
        unregisterReceiver(enableBTBroadcastReceiver);
        //LocalBroadcastManager.getInstance(this).unregisterReceiver(myReceiver);
        LocalBroadcastManager.getInstance(this).unregisterReceiver(btConnectionReceiver);


    }


    //BROADCAST RECEIVER FOR BLUETOOTH CONNECTION STATUS
    BroadcastReceiver btConnectionReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {

            Log.d(TAG, "Receiving btConnectionStatus Msg!!!");

            String connectionStatus = intent.getStringExtra("ConnectionStatus");
            myBTConnectionDevice = intent.getParcelableExtra("Device");

            //DISCONNECTED FROM BLUETOOTH CHAT
            if (connectionStatus.equals("disconnect")) {

                Log.d("ConnectAcitvity:", "Device Disconnected");

                //CHECK FOR NOT NULL
                if (connectIntent != null) {
                    //Stop Bluetooth Connection Service
                    stopService(connectIntent);
                }

                //RECONNECT DIALOG MSG
                AlertDialog alertDialog = new AlertDialog.Builder(Connect.this).create();
                alertDialog.setTitle("BLUETOOTH DISCONNECTED");
                alertDialog.setMessage("Connection with device: '"+myBTConnectionDevice.getName()+"' has ended. Do you want to reconnect?");
                alertDialog.setButton(AlertDialog.BUTTON_POSITIVE, "Yes",
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int which) {
                                startBTConnection(myBTConnectionDevice, myUUID);

                            }
                        });
                alertDialog.setButton(AlertDialog.BUTTON_NEGATIVE, "No",
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int which) {
                                dialog.dismiss();
                            }
                        });
                alertDialog.show();
            }

            //SUCCESSFULLY CONNECTED TO BLUETOOTH DEVICE
            else if (connectionStatus.equals("connect")) {


                Log.d("ConnectAcitvity:", "Device Connected");
                Toast.makeText(Connect.this, "Connection Established: " + myBTConnectionDevice.getName(),
                        Toast.LENGTH_LONG).show();
            }

            //BLUETOOTH CONNECTION FAILED
            else if (connectionStatus.equals("connectionFail")) {
                Toast.makeText(Connect.this, "Connection Failed: " + myBTConnectionDevice.getName(),
                        Toast.LENGTH_LONG).show();
            }

        }
    };

/*
    The BroadcastReceiver that listens for bluetooth broadcasts
*/
    /*private final BroadcastReceiver btConnectionReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            final BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
            //Device found
            if (BluetoothDevice.ACTION_FOUND.equals(action)) {
            }
            //Device is now connected
            else if (BluetoothDevice.ACTION_ACL_CONNECTED.equals(action)) {
                Log.d("ConnectAcitvity:","Device Connected");
                Toast.makeText(Connect.this, "Connection Established: "+ device.getName(),
                        Toast.LENGTH_LONG).show();
            }
            //Done searching
            else if (BluetoothAdapter.ACTION_DISCOVERY_FINISHED.equals(action)) {
            }
            //Device is about to disconnect
            else if (BluetoothDevice.ACTION_ACL_DISCONNECT_REQUESTED.equals(action)) {
            }
            //Device has disconnected
            else if (BluetoothDevice.ACTION_ACL_DISCONNECTED.equals(action)) {
                Log.d("ConnectAcitvity:","Device Disconnected");
                //RECONNECT DIALOG MSG
                AlertDialog alertDialog = new AlertDialog.Builder(Connect.this).create();
                alertDialog.setTitle("BLUETOOTH DISCONNECTED");
                alertDialog.setMessage("Connection with device: '"+device.getName()+"' has ended. Do you want to reconnect?");
                alertDialog.setButton(AlertDialog.BUTTON_POSITIVE, "Yes",
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int which) {
                                startBTConnection(device, myUUID);
                            }
                        });
                alertDialog.setButton(AlertDialog.BUTTON_NEGATIVE, "No",
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int which) {
                                dialog.dismiss();
                            }
                        });
                alertDialog.show();
            }
        }
    };
*/

    /*
        Create a BroadcastReceiver for ACTION_FOUND (EnableBT).
    */
    private final BroadcastReceiver enableBTBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (action.equals(myBluetoothAdapter.ACTION_STATE_CHANGED)) {
                final int state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, myBluetoothAdapter.ERROR);

                switch (state) {
                    //BLUETOOTH TURNED OFF STATE
                    case BluetoothAdapter.STATE_OFF:
                        Log.d(TAG, "OnReceiver: STATE OFF");
                        break;
                    //BLUETOOTH TURNING OFF STATE
                    case BluetoothAdapter.STATE_TURNING_OFF:
                        Log.d(TAG, "OnReceiver: STATE TURNING OFF");
                        break;
                    //BLUETOOTH TURNED ON STATE
                    case BluetoothAdapter.STATE_ON:
                        Log.d(TAG, "OnReceiver: STATE ON");

                        //TURN DISCOVERABILITY ON
                        discoverabilityON();

                        break;
                    //BLUETOOTH TURNING ON STATE
                    case BluetoothAdapter.STATE_TURNING_ON:
                        Log.d(TAG, "OnReceiver: STATE TURNING ON");
                        break;
                }
            }
        }
    };


    /*
        Create a BroadcastReceiver for ACTION_FOUND (Enable Discoverability).
    */
    private final BroadcastReceiver discoverabilityBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();
            if (action.equals(BluetoothAdapter.ACTION_SCAN_MODE_CHANGED)) {
                int mode = intent.getIntExtra(BluetoothAdapter.EXTRA_SCAN_MODE, BluetoothAdapter.ERROR);

                switch (mode) {
                    //DEVICE IS IN DISCOVERABLE MODE
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE_DISCOVERABLE:
                        Log.d(TAG, "OnReceiver: DISCOVERABILITY ENABLED");

                        //DISCOVER OTHER DEVICES
                        startSearch();

                        //START BLUETOOTH CONNECTION SERVICE WHICH WILL START THE ACCEPTTHREAD TO LISTEN FOR CONNECTION
                        connectIntent = new Intent(Connect.this, BluetoothConnectionService.class);
                        connectIntent.putExtra("serviceType", "listen");
                        //connectIntent.putExtra("device", device);
                        //connectIntent.putExtra("id", uuid);
                        startService(connectIntent);
                        Constants.setConnected(true);

                        //CHECK PAIRED DEVICE LIST
                        checkPairedDevice();


                        myBluetoothConnection = new BluetoothConnectionService();


                        break;
                    //DEVICE IS NOT IN DISCOVERABLE MODE
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE:
                        Log.d(TAG, "OnReceiver: DISCOVERABILITY DISABLED, ABLE TO RECEIVE CONNECTION");
                        break;
                    //BLUETOOTH TURNING ON STATE
                    case BluetoothAdapter.SCAN_MODE_NONE:
                        Log.d(TAG, "OnReceiver: DISCOVERABILITY DISABLED, NOT ABLE TO RECEIVE CONNECTION");
                        break;
                    //BLUETOOTH TURNED ON STATE
                    case BluetoothAdapter.STATE_CONNECTING:
                        Log.d(TAG, "OnReceiver: CONNECTING");
                        break;
                    //BLUETOOTH TURNED ON STATE
                    case BluetoothAdapter.STATE_CONNECTED:
                        Log.d(TAG, "OnReceiver: CONNECTED");
                        break;
                }
            }
        }
    };


    /*
      Create a BroadcastReceiver for ACTION_FOUND (Get Discovered Devices Info).
  */
    private final BroadcastReceiver discoveryBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();
            Log.d(TAG, "SEARCH ME!");

            if (action.equals(BluetoothDevice.ACTION_FOUND)) {

                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                myBTDevicesArrayList.add(device);
                if (ActivityCompat.checkSelfPermission(Connect.this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                    // TODO: Consider calling
                    //    ActivityCompat#requestPermissions
                    // here to request the missing permissions, and then overriding
                    //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                    //                                          int[] grantResults)
                    // to handle the case where the user grants the permission. See the documentation
                    // for ActivityCompat#requestPermissions for more details.
                }
                Log.d(TAG, "OnReceive: " + device.getName() + ": " + device.getAddress());
                myDeviceListAdapter = new DeviceListAdapter(context, R.layout.device_adapter_view, myBTDevicesArrayList);
                lvNewDevices.setAdapter(myDeviceListAdapter);

            }
        }
    };


    /*
      Create a BroadcastReceiver for ACTION_DISCOVERY_STARTED  (Start Discovering Devices).
  */
    private final BroadcastReceiver discoveryStartedBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();

            if (action.equals(BluetoothAdapter.ACTION_DISCOVERY_STARTED)) {

                Log.d(TAG, "STARTED DISCOVERY!!!");

                //deviceSearchStatus.setText(R.string.searchDevice);

            }
        }
    };


    /*
      Create a BroadcastReceiver for ACTION_DISCOVERY_FINISHED  (End Discovering Devices).
  */
    private final BroadcastReceiver discoveryEndedBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();

            if (action.equals(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)) {

                Log.d(TAG, "ENDED DISCOVERY!!!");

                //deviceSearchStatus.setText(R.string.searchDone);

            }
        }
    };


    /*
        Create a BroadcastReceiver for ACTION_FOUND (Pairing Devices).
    */
    private final BroadcastReceiver bondingBroadcastReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();

            if (action.equals(BluetoothDevice.ACTION_BOND_STATE_CHANGED)) {

                //BONDING DEVICE
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                //BluetoothConnectionService.setMyDevice(device);

                //BOUNDED ALREADY
                if (ActivityCompat.checkSelfPermission(Connect.this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                    // TODO: Consider calling
                    //    ActivityCompat#requestPermissions
                    // here to request the missing permissions, and then overriding
                    //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                    //                                          int[] grantResults)
                    // to handle the case where the user grants the permission. See the documentation
                    // for ActivityCompat#requestPermissions for more details.
                }
                if (device.getBondState() == BluetoothDevice.BOND_BONDED) {

                    Log.d(TAG, "BoundReceiver: Bond Bonded with: " + device.getName());
                    //BluetoothConnectionService.setMyDevice(device);

                    myProgressDialog.dismiss();

                    Toast.makeText(Connect.this, "Bound Successfully With: " + device.getName(),
                            Toast.LENGTH_LONG).show();
                    myBTDevice = device;
                    checkPairedDevice();
                    lvNewDevices.setAdapter(myDeviceListAdapter);

                    Constants.setConnected(true);

                }
                //BONDING WITH ANOTHER DEVICES
                if (device.getBondState() == BluetoothDevice.BOND_BONDING) {
                    Log.d(TAG, "BoundReceiver: Bonding With Another Device");

                    myProgressDialog = ProgressDialog.show(Connect.this, "Bonding With Device", "Please Wait...", true);

                    Constants.setConnected(true);

                }
                //BREAKING A BOND
                if (device.getBondState() == BluetoothDevice.BOND_NONE) {
                    Log.d(TAG, "BoundReceiver: Breaking Bond");

                    myProgressDialog.dismiss();

                    //DIALOG MSG POPUP
                    AlertDialog alertDialog = new AlertDialog.Builder(Connect.this).create();
                    alertDialog.setTitle("Bonding Status");
                    alertDialog.setMessage("Bond Disconnected!");
                    alertDialog.setButton(AlertDialog.BUTTON_NEUTRAL, "OK",
                            new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface dialog, int which) {
                                    dialog.dismiss();
                                }
                            });
                    alertDialog.show();

                    Constants.setConnected(false);

                    //RESET VARIABLE
                    myBTDevice = null;
                }

            }
        }
    };


    //BROADCAST RECEIVER FOR INCOMING MESSAGE
    BroadcastReceiver myReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {

            Log.d(TAG, "Receiving Msg!!!");

            String msg = intent.getStringExtra("receivingMsg");
            incomingMsg.append(msg + "\n");
            incomingMsgTextView.setText(incomingMsg);
            Constants.setInstruction(msg);

            //FragmentManager manager = getSupportFragmentManager();
            //FirstFragment fragment = (FirstFragment) manager.findFragmentById(R.id.first_fragment);
            //fragment.setInstruction(incomingMsgTextView.getText().toString());

        }
    };

    /*
        TURN DISCOVERABILITY ON
    */
    private void discoverabilityON() {

        Intent discoverableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
        discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 900);
        if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.BLUETOOTH_ADVERTISE) != PackageManager.PERMISSION_GRANTED) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.
        }
        startActivity(discoverableIntent);


    }


    //ENABLE DISABLE BLUETOOTH
    public void enableBT() {
        //DEVICE DOES NOT HAVE BLUETOOTH
        if (myBluetoothAdapter == null) {
            Toast.makeText(Connect.this, "Device Does Not Support Bluetooth.",
                    Toast.LENGTH_LONG).show();
            Log.d(TAG, "enableDisableBT: Does not have BT capabilities.");
        }
        //DEVICE'S BLUETOOTH NOT ENABLED
        if (!myBluetoothAdapter.isEnabled()) {
            Intent enableBTIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                // TODO: Consider calling
                //    ActivityCompat#requestPermissions
                // here to request the missing permissions, and then overriding
                //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                //                                          int[] grantResults)
                // to handle the case where the user grants the permission. See the documentation
                // for ActivityCompat#requestPermissions for more details.
            }
            startActivity(enableBTIntent);
        }
        //DEVICE'S BLUETOOTH ENABLED
        if (myBluetoothAdapter.isEnabled()) {
            //TURN DISCOVERABILITY ON
            discoverabilityON();
        }

    }

    /*
     Check BT permission in manifest (For Start Discovery)
 */
    /*private void checkBTPermission() {
        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.LOLLIPOP) {
            int permissionCheck = ContextCompat.checkSelfPermission(getApplicationContext(),
                    Manifest.permission.ACCESS_FINE_LOCATION);

            permissionCheck += ContextCompat.checkSelfPermission(getApplicationContext(), Manifest.permission.ACCESS_COARSE_LOCATION);
            if (permissionCheck != 0) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, 1001);
            }
        } else {
            Log.d(TAG, "checkBTPermissions: No need to check permissions. SDK version < LOLLIPOP.");

        }
    }*/


    /* START DISCOVERING OTHER DEVICES */
    private void startSearch() {
        Log.d(TAG, "btnDiscover: Looking for unpaired devices.");

        //DISCOVER OTHER DEVICES
        if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.
        }
        if (myBluetoothAdapter.isDiscovering()) {
            myBluetoothAdapter.cancelDiscovery();
            Log.d(TAG, "BTDiscovery: canceling discovery");

            //check BT permission in manifest
            //checkBTPermission();
            myBluetoothAdapter.startDiscovery();
            Log.d(TAG, "BTDiscovery: enable discovery");

        }
        if (!myBluetoothAdapter.isDiscovering()) {

            //check BT permission in manifest
            //checkBTPermission();
            myBluetoothAdapter.startDiscovery();
            Log.d(TAG, "BTDiscovery: enable discovery");
        }
    }


    /*
        START BLUETOOTH CHAT SERVICE METHOD
    */
    public void startBTConnection(BluetoothDevice device, UUID uuid) {

        Log.d(TAG, "StartBTConnection: Initializing RFCOM Bluetooth Connection");

        //myBluetoothConnection.startClient(device, uuid);

        connectIntent = new Intent(Connect.this, BluetoothConnectionService.class);
        connectIntent.putExtra("serviceType", "connect");
        connectIntent.putExtra("device", device);
        connectIntent.putExtra("id", uuid);

        Log.d(TAG, "StartBTConnection: Starting Bluetooth Connection Service!");

        startService(connectIntent);
        Constants.setConnected(true);
    }


    public void checkPairedDevice() {

        //CHECK IF THERE IS PAIRED DEVICES
        if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.
        }
        Set<BluetoothDevice> pairedDevices = myBluetoothAdapter.getBondedDevices();
        myBTPairedDevicesArrayList.clear();

        if (pairedDevices.size() > 0) {

            for (BluetoothDevice device : pairedDevices) {
                Log.d(TAG, "PAIRED DEVICES: " + device.getName() + "," + device.getAddress());
                myBTPairedDevicesArrayList.add(device);

            }
            pairedDeviceText.setText("Paired Devices: ");
            myPairedDeviceListAdapter = new DeviceListAdapter(this, R.layout.device_adapter_view, myBTPairedDevicesArrayList);
            lvPairedDevices.setAdapter(myPairedDeviceListAdapter);

        } else {

            /*String[] noDevice = {"No Device"};
            ListAdapter emptyListAdapter = new ArrayAdapter<String>(this, R.layout.device_adapter_view,R.id.deviceName, noDevice);
            lvPairedDevices.setAdapter(emptyListAdapter);*/
            pairedDeviceText.setText("No Paired Devices: ");

            Log.d(TAG, "NO PAIRED DEVICE!!");
        }
    }


}
