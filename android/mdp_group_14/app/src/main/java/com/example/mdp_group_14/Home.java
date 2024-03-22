package com.example.mdp_group_14;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentPagerAdapter;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.viewpager.widget.ViewPager;

import android.app.Activity;
import android.app.ProgressDialog;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;


import com.google.android.material.tabs.TabLayout;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Objects;
import java.util.UUID;

public class Home extends Fragment {

    final Handler handler = new Handler();
    // Declaration Variables
    private static SharedPreferences sharedPreferences;
    private static SharedPreferences.Editor editor;
    private static Context context;
    public static Handler timerHandler = new Handler();

    private static GridMap gridMap;
    static TextView xAxisTextView, yAxisTextView, directionAxisTextView;
    static TextView robotStatusTextView, bluetoothStatus, bluetoothDevice;
    static ImageButton upBtn, downBtn, leftBtn, rightBtn,bleftBtn,brightBtn;

    BluetoothDevice mBTDevice;
    private static UUID myUUID;
    ProgressDialog myDialog;
    Bitmap bm, mapscalable;
    String obstacleID;

    private static final String TAG = "Main Activity";
    public static boolean stopTimerFlag = false;
    public static boolean stopWk9TimerFlag = false;

    public static boolean trackRobot = true;

    private int g_coordX;
    private int g_coordY;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // inflate
        View root = inflater.inflate(R.layout.home, container, false);

        // get shared preferences
        sharedPreferences = getActivity().getSharedPreferences("Shared Preferences",
                Context.MODE_PRIVATE);



        SectionsPagerAdapter sectionsPagerAdapter = new SectionsPagerAdapter(getActivity().getSupportFragmentManager(),
                FragmentPagerAdapter.BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT);

        sectionsPagerAdapter.addFragment(new MappingFragment(),"MAP CONFIG");
        sectionsPagerAdapter.addFragment(new BluetoothCommunications(),"CHAT");
        sectionsPagerAdapter.addFragment(new ControlFragment(),"CHALLENGE");

        ViewPager viewPager = root.findViewById(R.id.view_pager);
        viewPager.setAdapter(sectionsPagerAdapter);
        viewPager.setOffscreenPageLimit(2);


        TabLayout tabs = root.findViewById(R.id.tabs);
        tabs.setupWithViewPager(viewPager);



        LocalBroadcastManager
                .getInstance(getContext())
                .registerReceiver(messageReceiver, new IntentFilter("incomingMessage"));

        // Set up sharedPreferences
        Home.context = getContext();
        sharedPreferences();
        editor.putString("message", "");
        editor.putString("direction","None");
        editor.putString("connStatus", "Disconnected");
        editor.commit();

        // Toolbar
        ImageButton bluetoothButton = root.findViewById(R.id.bluetoothButton);
        bluetoothButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent popup = new Intent(getContext(), BluetoothSetUp.class);
                startActivity(popup);
            }
        });

        // Bluetooth Status
        bluetoothStatus = root.findViewById(R.id.bluetoothStatus);
        bluetoothDevice = root.findViewById(R.id.bluetoothConnectedDevice);

        // Map
        gridMap = new GridMap(getContext());
        gridMap = root.findViewById(R.id.mapView);
        xAxisTextView = root.findViewById(R.id.xAxisTextView);
        yAxisTextView = root.findViewById(R.id.yAxisTextView);
        directionAxisTextView = root.findViewById(R.id.directionAxisTextView);

        // initialize ITEM_LIST and imageBearings strings
        for (int i = 0; i < 20; i++) {
            for (int j = 0; j < 20; j++) {
                gridMap.ITEM_LIST.get(i)[j] = "";
                GridMap.imageBearings.get(i)[j] = "";
            }
        }

        // Controller
        upBtn = root.findViewById(R.id.upBtn);
        downBtn = root.findViewById(R.id.downBtn);
        leftBtn = root.findViewById(R.id.leftBtn);
        rightBtn = root.findViewById(R.id.rightBtn);
        brightBtn = root.findViewById(R.id.brightBtn);
        bleftBtn = root.findViewById(R.id.bleftBtn);

        // Robot Status
        robotStatusTextView = root.findViewById(R.id.robotStatus);

        myDialog = new ProgressDialog(getContext());
        myDialog.setMessage("Waiting for other device to reconnect...");
        myDialog.setCancelable(false);
        myDialog.setButton(
                DialogInterface.BUTTON_NEGATIVE,
                "Cancel",
                new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.dismiss();
                    }
                }
        );
        PathTranslator pathTranslator = new PathTranslator(gridMap);
//        pathTranslator.translatePath("MOVE,FORWARD,30");
        return root;
    }

    public static GridMap getGridMap() {
        return gridMap;
    }
    public static TextView getRobotStatusTextView() {  return robotStatusTextView; }

    public static ImageButton getUpBtn() { return upBtn; }
    public static ImageButton getDownBtn() { return downBtn; }
    public static ImageButton getLeftBtn() { return leftBtn; }
    public static ImageButton getRightBtn() { return rightBtn; }

    public static ImageButton getbLeftBtn() { return bleftBtn; }
    public static ImageButton getbRightBtn() { return brightBtn; }


    public static TextView getBluetoothStatus() { return bluetoothStatus; }
    public static TextView getConnectedDevice() { return bluetoothDevice; }
    // For week 8 only
    public static boolean getTrackRobot() { return trackRobot; }
    public static void toggleTrackRobot() { trackRobot = !trackRobot; }

    public static void sharedPreferences() {
        sharedPreferences = Home.getSharedPreferences(Home.context);
        editor = sharedPreferences.edit();
    }

    private static SharedPreferences getSharedPreferences(Context context) {
        return context.getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
    }

    // Send Coordinates to alg
    public static void printCoords(String message){
        showLog("Displaying Coords untranslated and translated");
        showLog(message);
        String[] strArr = message.split("_",2);

        // Translated ver is sent
        if (BluetoothConnectionService.BluetoothConnectionStatus == true){
            byte[] bytes = strArr[1].getBytes(Charset.defaultCharset());
            BluetoothConnectionService.write(bytes);
        }

        // Display both untranslated and translated coordinates on CHAT (for debugging)
        refreshMessageReceivedNS("Untranslated Coordinates: " + strArr[0] + "\n");
        refreshMessageReceivedNS("Translated Coordinates: "+strArr[1]);
        showLog("Exiting printCoords");
    }

    // Send message to bluetooth (not shown on chat box)
    public static void printMessage(String message) {
        showLog("Entering printMessage");
        editor = sharedPreferences.edit();

        if (BluetoothConnectionService.BluetoothConnectionStatus) {
            byte[] bytes = message.getBytes(Charset.defaultCharset());
            BluetoothConnectionService.write(bytes);
        }
        showLog(message);
        showLog("Exiting printMessage");
    }

    // Send message to bluetooth (not shown on chat box)
    public static void printMessage(JSONArray message) {
        showLog("Entering printMessage");
        editor = sharedPreferences.edit();

    }


//        if (BluetoothConnectionService.BluetoothConnectionStatus) {
////            JSONObject jsonObj = message.getJSONObject("data");
//        JSONObject js=new JSONObject();
//        try {
//            JSONArray ja=new JSONArray();
//            js.put("key", "floor");
//            ja.put(js);
//            BluetoothConnectionService.write(ja);
//
//        }
//        catch (JSONException e) {
//            showLog("lol!");
//
//
//            //BluetoothConnectionService.write({"key":"test","value":"hello"});
//        }
//        //showLog(message);
//        showLog("Exiting printMessage");
//    }

    // Purely to display a message on the chat box - NOT SENT via BT
    public static void refreshMessageReceivedNS(String message){
        BluetoothCommunications.getMessageReceivedTextView().append(message+ "\n");
    }

    public static void refreshMessageReceivedNS(int message){
        BluetoothCommunications.getMessageReceivedTextView().append(message+ "\n");
    }

    public static void refreshDirection(String direction) {
        gridMap.setRobotDirection(direction);
        int x = gridMap.getCurCoord()[0];
        int y = gridMap.getCurCoord()[1];
        String dir;
        String newDir = gridMap.getRobotDirection();
//        newDir = newDir.toUpperCase();
        directionAxisTextView.setText(sharedPreferences.getString("direction","")); //changes the UI direction display as well
        //printMessage("Direction is set to " + direction); //OLD VER

        dir= (newDir.equals("up"))?"NORTH":(newDir.equals("down"))?"SOUTH":(newDir.equals("left"))?"WEST":"EAST";
        if ((x - 2)>=0 && (y - 1)>=0)
        {
//          BluetoothCommunications.getMessageReceivedTextView().append("ROBOT" + "," + (col - 2)*5 + "," + (row - 1)*5 + "," + dir.toUpperCase());
            Home.printMessage("ROBOT" + "," + (x-2)*5 + "," + (y-1)*5 + "," + dir.toUpperCase());
        }
        else{
            showLog("out of grid");
        }
//        printMessage("ROBOT,"+ x + "," + y + "," + dir);
//        BluetoothCommunications.getMessageReceivedTextView().append("ROBOT,"+ (x-1) +"," + (y-1) + "," + dir+"\n"); //for troubleshooting

    }

    public static void refreshLabel() {
        xAxisTextView.setText(String.valueOf(gridMap.getCurCoord()[0]-1));
        yAxisTextView.setText(String.valueOf(gridMap.getCurCoord()[1]-1));
        directionAxisTextView.setText(sharedPreferences.getString("direction",""));
    }

    private static void showLog(String message) {
        Log.d(TAG, message);
    }

    private final BroadcastReceiver mBroadcastReceiver5 = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            BluetoothDevice mDevice = intent.getParcelableExtra("Device");
            String status = intent.getStringExtra("Status");
            sharedPreferences();

            if(status.equals("connected")){
                try {
                    myDialog.dismiss();
                } catch(NullPointerException e){
                    e.printStackTrace();
                }

                Log.d(TAG, "mBroadcastReceiver5: Device now connected to "+mDevice.getName());
                updateStatus("Device now connected to "
                        + mDevice.getName());
                editor.putString("connStatus", "Connected to " + mDevice.getName());
            }
            else if(status.equals("disconnected")){
                Log.d(TAG, "mBroadcastReceiver5: Disconnected from "+mDevice.getName());
                updateStatus("Disconnected from "
                        + mDevice.getName());

                editor.putString("connStatus", "Disconnected");

                myDialog.show();
            }
            editor.commit();
        }
    };

    // Message handler (Receiving)
    // RPi relays the EXACT SAME stm commands sent by algo back to android: Starts with "Algo|"
    // RPi sends the image id as "TARGET~<obID>~<ImValue>"
    // Other specific strings are to clear checklist
    BroadcastReceiver messageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            PathTranslator pathTranslator = new PathTranslator(gridMap);    // For real-time updating on displayed gridmap
            String message = intent.getStringExtra("receivedMessage");
            showLog("receivedMessage: message --- " + message);

            String[] cmdd = message.split(",");

//            if (message.contains(" "))
//            {
//                message= Arrays.toString(message.split(" "));
//            }
//            showLog("cmd1 --- " + cmdd[1]);
//            showLog("cmd2 --- " + cmdd[2]);


            int[] global_store = gridMap.getCurCoord();
            g_coordX = global_store[0];
            g_coordY = global_store[1];
            ArrayList<String> mapCoord = new ArrayList<>();

            //STATUS:<input>
            if (message.contains("STATUS")) {
                robotStatusTextView.setText(message.split(":")[1]);
            }
            //ROBOT|5,4,EAST (Early version of updating robot position via comms)
            if(message.contains("ROBOT")) {
                String[] cmd = message.split("\\|");
                String[] sentCoords = cmd[1].split(",");
                String[] sentDirection = sentCoords[2].split("\\.");
//                BluetoothCommunications.getMessageReceivedTextView().append("\n");
                String direction = "";
                String abc = String.join("", sentDirection);
                if (abc.contains("EAST")) {
                    direction = "right";
                }
                else if (abc.contains("NORTH")) {
                    direction = "up";
                }
                else if (abc.contains("WEST")) {
                    direction = "left";
                }
                else if (abc.contains("SOUTH")) {
                    direction = "down";
                }
                else{
                    direction = "";
                }
                gridMap.setCurCoord(Integer.valueOf(sentCoords[1]) + 2, 19 - Integer.valueOf(sentCoords[0]), direction);
            }
            //image format from RPI is "TARGET~<obID>~<ImValue>" eg TARGET~3~7
            else if(message.contains("TARGET")) {
                try {
                    String[] cmd = message.split(",");
                    String temp2="-1";
                    BluetoothCommunications.getMessageReceivedTextView().append("Obstacle no: " + cmd[1]+ "TARGET ID: " + cmd[2] + "\n");

//                    if (cmd[2].contains("STOP"))
//                    {
//                        String temp=cmd[2];
//                        String[] temp1=temp.split(" ");
//                        temp2=temp1[0];
//
//                    }

                    gridMap.updateIDFromRpi(String.valueOf(Integer.valueOf(cmd[1])-1), cmd[2]);
                    obstacleID = String.valueOf(Integer.valueOf(cmd[1]) - 2);


//                    int ob= Integer.parseInt(obstacleID);

                }
                catch(Exception e)
                {
                    e.printStackTrace();
                }
            }
            else if(message.contains("ARROW")){
                String[] cmd = message.split(",");
//                BluetoothCommunications.getMessageReceivedTextView().append("Obstacle no: " + cmd[1]+ "TARGET ID: " + cmd[2] + "\n");

                Home.refreshMessageReceivedNS("TASK2"+"\n");
                Home.refreshMessageReceivedNS("obstacle id: "+cmd[1]+", ARROW: "+cmd[2]);


//                updateStatus(cmd[0]+" "+ cmd[1]+" "+cmd[2]);
            }
            // OLD VER: Expects a syntax of e.g. Algo|f010. Commented out and implemented new version below
/*            if(message.contains("Algo")) {
                // translate the message after Algo|
                if(trackRobot)
                    pathTranslator.translatePath(message.split("\\|")[1]);
//                pathTranslator.altTranslation(message.split("\\|")[1]);   // last min addition - untested
            }*/

            //NEW VER: Expects a syntax of eg. MOVE,<DISTANCE IN CM>,<DIRECTION>.
            //NEW VER: Expects a syntax of eg. TURN,<DIRECTION>.

            //CASE 1 & 2: MoveInstruction or TurnInstruction sent
            else if(message.contains("MOVE") || message.contains("TURN")){
                updateStatus("translation");
                pathTranslator.translatePath(message); //splitting and translation will be done in PathTranslator
            }
            else if(message.contains("STOP"))
            {
                Home.refreshMessageReceivedNS("STOP received");
//                showLog("received Stop");
                Home.stopTimerFlag = true;
                Home.stopWk9TimerFlag=true;
                timerHandler.removeCallbacks(ControlFragment.timerRunnableExplore);
                timerHandler.removeCallbacks(ControlFragment.timerRunnableFastest);
            }
            else{
                BluetoothCommunications.getMessageReceivedTextView().append("unknown message received");
                showLog("unknown message received");
            }
        }
    };

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data){
        super.onActivityResult(requestCode, resultCode, data);

        switch (requestCode){
            case 1:
                if(resultCode == Activity.RESULT_OK){
                    mBTDevice = data.getExtras().getParcelable("mBTDevice");
                    myUUID = (UUID) data.getSerializableExtra("myUUID");
                }
        }
    }

    @Override
    public void onDestroy(){
        super.onDestroy();
        try{
            LocalBroadcastManager.getInstance(getContext()).unregisterReceiver(messageReceiver);
            LocalBroadcastManager.getInstance(getContext()).unregisterReceiver(mBroadcastReceiver5);
        } catch(IllegalArgumentException e){
            e.printStackTrace();
        }
    }

    @Override
    public void onPause(){
        super.onPause();
        try{
            LocalBroadcastManager.getInstance(getContext()).unregisterReceiver(mBroadcastReceiver5);
        } catch(IllegalArgumentException e){
            e.printStackTrace();
        }
    }

    @Override
    public void onResume(){
        super.onResume();
        try{
            IntentFilter filter2 = new IntentFilter("ConnectionStatus");
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(mBroadcastReceiver5, filter2);
        } catch(IllegalArgumentException e){
            e.printStackTrace();
        }
    }

    @Override
    public void onSaveInstanceState(Bundle outState) {
        showLog("Entering onSaveInstanceState");
        super.onSaveInstanceState(outState);

        outState.putString(TAG, "onSaveInstanceState");
        showLog("Exiting onSaveInstanceState");
    }
    private void updateStatus(String message) {
        Toast toast = Toast.makeText(getContext(), message, Toast.LENGTH_SHORT);
        toast.setGravity(Gravity.TOP,0, 0);
        toast.show();
    }
}