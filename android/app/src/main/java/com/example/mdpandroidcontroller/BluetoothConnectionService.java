package com.example.mdpandroidcontroller;

import android.app.IntentService;
import android.app.ProgressDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Handler;
import android.util.Log;

import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.io.IOException;
import java.util.UUID;

public class BluetoothConnectionService extends IntentService {

    private static final String TAG = "BTConnectionAService";
    private static final String appName = "Mdp";

    //UUID
    private static final UUID myUUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    private BluetoothAdapter myBluetoothAdapter;

    private AcceptThread myAcceptThread;
    private ConnectThread myConnectThread;
    public BluetoothDevice myDevice;
    private UUID deviceUUID;
    private Handler mHandler;

    Context myContext;
    ProgressDialog myProgressDialog;

    private ReconnectThread mReconnectThread;
    private boolean reconnecting = false;
    private static String BLUETOOTH_CONNECTION_TAG = "Bluetooth (Connection)";
    private int mState;

    public interface ConnectionConstants {
        // Constants that indicate the current connection state
        int STATE_DISCONNECTED = 0;       // we're doing nothing
        int STATE_CONNECTING = 1; // now initiating an outgoing connection
        int STATE_CONNECTED = 2;  // now connected to a remote device
    }

    //CONSTRUCTOR
    public BluetoothConnectionService() {

        super("BluetoothConnectionService");
        // mHandler = new Handler(Looper.getMainLooper());
    }


    //HANDLE INTENT FOR SERVICE. START THIS METHOD WHEN THE SERVICE IS CREATED
    @Override
    protected void onHandleIntent(@Nullable Intent intent) {

        myContext = getApplicationContext();
        myBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        if (intent.getStringExtra("serviceType").equals("listen")) {

            myDevice = (BluetoothDevice) intent.getExtras().getParcelable("device");

            Log.d(TAG, "Service Handle: startAcceptThread");

            startAcceptThread();
        } else {
            myDevice = (BluetoothDevice) intent.getExtras().getParcelable("device");
            deviceUUID = (UUID) intent.getSerializableExtra("id");

            Log.d(TAG, "Service Handle: startClientThread");

            startClientThread(myDevice, deviceUUID);
        }

    }

    /*
         A THREAD THAT RUNS WHILE LISTENING FOR INCOMING CONNECTIONS. IT BEHAVES LIKE
         A SERVER-SIDE CLIENT. IT RUNS UNTIL A CONNECTION IS ACCEPTED / CANCELLED
    */
    private class AcceptThread extends Thread {

        //Local server socket
        private final BluetoothServerSocket myServerSocket;

        public AcceptThread() {
            BluetoothServerSocket temp = null;

            //Create a new listening server socket
            try {
                if (ActivityCompat.checkSelfPermission(BluetoothConnectionService.this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                    // TODO: Consider calling
                    //    ActivityCompat#requestPermissions
                    // here to request the missing permissions, and then overriding
                    //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                    //                                          int[] grantResults)
                    // to handle the case where the user grants the permission. See the documentation
                    // for ActivityCompat#requestPermissions for more details.
                }
                temp = myBluetoothAdapter.listenUsingInsecureRfcommWithServiceRecord(appName, myUUID);
                Log.d(TAG, "AcceptThread: Setting up server using: " + myUUID);

            } catch (IOException e) {

            }

            myServerSocket = temp;
        }

        public void run() {
            Log.d(TAG, "AcceptThread: Running");

            BluetoothSocket socket = null;
            Intent connectionStatusIntent;

            try {
                Log.d(TAG, "Run: RFCOM server socket start....");

                //Blocking call which will only return on a successful connection / exception
                socket = myServerSocket.accept();

                //BROADCAST CONNECTION MSG
                connectionStatusIntent = new Intent("btConnectionStatus");
                connectionStatusIntent.putExtra("ConnectionStatus", "connect");
                connectionStatusIntent.putExtra("Device", Connect.getBluetoothDevice());
                LocalBroadcastManager.getInstance(myContext).sendBroadcast(connectionStatusIntent);

                //Successfully connected
                Log.d(TAG, "Run: RFCOM server socket accepted connection");

                //START BLUETOOTH CHAT
                BluetoothChat.connected(socket, myDevice, myContext);


            } catch (IOException e) {

                connectionStatusIntent = new Intent("btConnectionStatus");
                connectionStatusIntent.putExtra("ConnectionStatus", "connectionFail");
                connectionStatusIntent.putExtra("Device", Connect.getBluetoothDevice());

                Log.d(TAG, "AcceptThread: Connection Failed ,IOException: " + e.getMessage());
            }


            Log.d(TAG, "Ended AcceptThread");

        }

        public void cancel() {

            Log.d(TAG, "Cancel: Canceling AcceptThread");

            try {
                myServerSocket.close();
            } catch (IOException e) {
                Log.d(TAG, "Cancel: Closing AcceptThread Failed. " + e.getMessage());
            }
        }
    }

    private void connectionFailed() {
        // Send a failure message back to the Activity
//        mHandler.obtainMessage(HandlerConstants.MESSAGE_TOAST, "Unable to connect device").sendToTarget();
        Log.d(BLUETOOTH_CONNECTION_TAG, "Connection failed");
        mState = ConnectionConstants.STATE_DISCONNECTED;
        reconnecting = true;
        if (mReconnectThread == null && myBluetoothAdapter.isEnabled()) {
            mReconnectThread = new ReconnectThread(myDevice);
            mReconnectThread.start();
        } else if (!myBluetoothAdapter.isEnabled()){
            if (mReconnectThread != null) {
                mReconnectThread.cancel();
            }
            mReconnectThread = null;
        }
    }

    public void connectionLost() {
        // Send a failure message back to the Activity
        Log.d(BLUETOOTH_CONNECTION_TAG, "Connection lost");
        //mHandler.obtainMessage(HandlerConstants.MESSAGE_TOAST, "Device connection was lost").sendToTarget();
        mState = ConnectionConstants.STATE_DISCONNECTED;
        reconnecting = true;
        if (mReconnectThread == null && myBluetoothAdapter.isEnabled()) {
            mReconnectThread = new ReconnectThread(myDevice);
            mReconnectThread.start();
        } else if (!myBluetoothAdapter.isEnabled()){
            if (mReconnectThread != null) {
                mReconnectThread.cancel();
            }
            mReconnectThread = null;
        }
    }

    public class ReconnectThread extends Thread {
        private final BluetoothDevice myDevice;
        private boolean flag = true;
        BluetoothSocket socket = null;

        private final BluetoothServerSocket myServerSocket;

        ReconnectThread(BluetoothDevice device) {
            BluetoothServerSocket temp = null;
            myDevice = device;
            myServerSocket = temp;
        }

        public void run() {
            Log.i(BLUETOOTH_CONNECTION_TAG, "Attempting to reconnect");
            while (mState != ConnectionConstants.STATE_CONNECTED && myBluetoothAdapter.isEnabled() && flag) {

                //Blocking call which will only return on a successful connection / exception
                try {
                    socket = myServerSocket.accept();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }

                if (reconnecting) {
                    BluetoothChat.connected(socket, myDevice, myContext);
                }
                reconnecting = false;
                try {
                    sleep(3000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
        void cancel() {
            this.flag = false;
        }
    }

    /*
        THREAD RUNS WHILE ATTEMPTING TO MAKE AN OUTGOING CONNECTION WITH A DEVICE.
        IT RUNS STRAIGHT THROUGH, MAKING EITHER A SUCCESSFULLY OR FAILED CONNECTION
    */
    private class ConnectThread extends Thread {

        private BluetoothSocket mySocket;

        public ConnectThread(BluetoothDevice device, UUID uuid) {

            Log.d(TAG, "ConnectThread: started");
            myDevice = device;
            deviceUUID = uuid;
        }

        public void run() {
            BluetoothSocket temp = null;
            Intent connectionStatusIntent;

            Log.d(TAG, "Run: myConnectThread");

            /* Get a BluetoothSocket for a connection with given BluetoothDevice */
            try {
                Log.d(TAG, "ConnectThread: Trying to create InsecureRFcommSocket using UUID: " + myUUID);
                if (ActivityCompat.checkSelfPermission(BluetoothConnectionService.this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                    // TODO: Consider calling
                    //    ActivityCompat#requestPermissions
                    // here to request the missing permissions, and then overriding
                    //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                    //                                          int[] grantResults)
                    // to handle the case where the user grants the permission. See the documentation
                    // for ActivityCompat#requestPermissions for more details.
                }
                temp = myDevice.createRfcommSocketToServiceRecord(deviceUUID);
            } catch (IOException e) {
                Log.d(TAG, "ConnectThread: Could not create InsecureRFcommSocket " + e.getMessage());
            }

            mySocket = temp;

            //Cancel discovery to prevent slow connection
            myBluetoothAdapter.cancelDiscovery();

            try {
                Log.d(TAG, "Connecting to Device: " + myDevice);
                //Blocking call and will only return on a successful connection / exception
                mySocket.connect();

                //BROADCAST CONNECTION MSG
                connectionStatusIntent = new Intent("btConnectionStatus");
                connectionStatusIntent.putExtra("ConnectionStatus", "connect");
                connectionStatusIntent.putExtra("Device", myDevice);
                LocalBroadcastManager.getInstance(myContext).sendBroadcast(connectionStatusIntent);

                Log.d(TAG, "run: ConnectThread connected");

                //START BLUETOOTH CHAT
                BluetoothChat.connected(mySocket, myDevice, myContext);

                //CANCEL ACCEPT THREAD FOR LISTENING
                if (myAcceptThread != null) {
                    myAcceptThread.cancel();
                    myAcceptThread = null;
                }

            } catch (IOException e) {
                //Close socket on error
                try {
                    mySocket.close();

                    connectionStatusIntent = new Intent("btConnectionStatus");
                    connectionStatusIntent.putExtra("ConnectionStatus", "connectionFail");
                    connectionStatusIntent.putExtra("Device", myDevice);

                    LocalBroadcastManager.getInstance(myContext).sendBroadcast(connectionStatusIntent);
                    Log.d(TAG, "run: Socket Closed: Connection Failed!! " + e.getMessage());

                } catch (IOException e1) {
                    Log.d(TAG, "myConnectThread, run: Unable to close socket connection: " + e1.getMessage());
                }

            }

            try {
                //Dismiss Progress Dialog when connection established
                //myProgressDialog.dismiss();
                //mHandler.post(new DisplayToast(getApplicationContext(),"Connection Established With: "+myDevice.getName()));
            } catch (NullPointerException e) {
                e.printStackTrace();
            }
        }

        public void cancel() {

            try {
                Log.d(TAG, "Cancel: Closing Client Socket");
                mySocket.close();
            } catch (IOException e) {
                Log.d(TAG, "Cancel: Closing mySocket in ConnectThread Failed " + e.getMessage());
            }
        }
    }

    //START ACCEPTTHREAD AND LISTEN FOR INCOMING CONNECTION
    public synchronized void startAcceptThread() {

        Log.d(TAG, "start");

        //Cancel any thread attempting to make a connection
        if (myConnectThread != null) {
            myConnectThread.cancel();
            myConnectThread = null;
        }
        if (myAcceptThread == null) {
            myAcceptThread = new AcceptThread();
            myAcceptThread.start();
        }
    }

    /* CONNECTTHREAD STARTS AND ATTEMPT TO MAKE A CONNECTION WITH THE OTHER DEVICES */
    public void startClientThread(BluetoothDevice device, UUID uuid) {

        Log.d(TAG, "startClient: Started");

        myConnectThread = new ConnectThread(device, uuid);
        myConnectThread.start();

    }


}
