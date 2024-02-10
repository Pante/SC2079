package com.example.mdpandroidcontroller;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.Charset;

public class BluetoothChat {

    private static final String TAG = "BluetoothChat";
    // private ConnectedThread myConnectedThread;
    private static Context myContext;

    private static BluetoothSocket mySocket;
    private static InputStream myInputStream;
    private static OutputStream myOutPutStream;
    private static BluetoothDevice myBluetoothConnectionDevice;

    private BluetoothConnectionService.ReconnectThread mReconnectThread;
    private boolean reconnecting = false;
    private static String BLUETOOTH_CONNECTION_TAG = "Bluetooth (Connection)";
    private int mState;
    private boolean flag = true;
    BluetoothSocket socket = null;
    private BluetoothAdapter myBluetoothAdapter;
    public BluetoothDevice myDevice;

    /*
           RESPONSIBLE FOR MAINTAINING THE BLUETOOTH CONNECTION, SENDING THE
           DATA, AND RECEIVING INCOMING DATA THROUGH INPUT/OUTPUT STREAMS RESPECTIVELY
   */

    public static BluetoothDevice getBluetoothDevice(){
        return myBluetoothConnectionDevice;
    }
    public static void startChat(BluetoothSocket socket) {

        Log.d(TAG, "ConnectedThread: Starting");

        mySocket = socket;
        InputStream tempIn = null;
        OutputStream tempOut = null;


        try {
            tempIn = mySocket.getInputStream();
            tempOut = mySocket.getOutputStream();
        } catch (IOException e) {
            e.printStackTrace();
        }
        myInputStream = tempIn;
        myOutPutStream = tempOut;

        //Buffer store for the stream
        byte[] buffer = new byte[1024];

        //Bytes returned from the read()
        int bytes;

        while (true) {
            //Read from the InputStream
            try {
                bytes = myInputStream.read(buffer);

                String incomingMessage = new String(buffer, 0, bytes);
                Log.d(TAG, "InputStream: " + incomingMessage);

                //BROADCAST INCOMING MSG
                Intent incomingMsgIntent = new Intent("IncomingMsg");
                incomingMsgIntent.putExtra("receivingMsg", incomingMessage);
                LocalBroadcastManager.getInstance(myContext).sendBroadcast(incomingMsgIntent);

            } catch (IOException e) {

                //BROADCAST CONNECTION MSG
                Intent connectionStatusIntent = new Intent("btConnectionStatus");
                connectionStatusIntent.putExtra("ConnectionStatus", "disconnect");
                connectionStatusIntent.putExtra("Device",myBluetoothConnectionDevice);
                LocalBroadcastManager.getInstance(myContext).sendBroadcast(connectionStatusIntent);

                Log.d(TAG, "CHAT SERVICE: Closed!!!");
                e.printStackTrace();
                break;

            } catch (Exception e){
                Log.d(TAG, "CHAT SERVICE: Closed 2!!!: "+ e);
                e.printStackTrace();

            }

        }
    }

    /*
    //CALL THIS FROM MAIN ACTIVITY TO SEND DATA TO REMOTE DEVICE (ROBOT)//
    */
    public static void write(byte[] bytes) {

        String text = new String(bytes, Charset.defaultCharset());
        Log.d(TAG, "Write: Writing to outputstream: " + text);

        try {
            myOutPutStream.write(bytes);
        } catch (IOException e) {
            Log.d(TAG, "Write: Error writing to output stream: " + e.getMessage());
        }
    }


    //CALL THIS TO SHUTDOWN CONNECTION
    public void cancel() {
        try {
            mySocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }



    //METHOD TO START CHAT SERVICE
    static void connected(BluetoothSocket mySocket, BluetoothDevice myDevice, Context context) {
        Log.d(TAG, "Connected: Starting");

        //showToast("Connection Established With: "+myDevice.getName());
        myBluetoothConnectionDevice = myDevice;
        myContext = context;
        //Start thread to manage the connection and perform transmissions
        startChat(mySocket);


    }

    /*
    //WRITE TO CONNECTEDTHREAD IN AN UNSYNCHRONIZED MANNER
    */
    public static void writeMsg(byte[] out) {

        // Create temporary object
        // ConnectedThread temp;

        // Synchronize a copy of the ConnectedThread
        Log.d(TAG, "write: Write Called.");
        //perform the write
        write(out);

    }

}
