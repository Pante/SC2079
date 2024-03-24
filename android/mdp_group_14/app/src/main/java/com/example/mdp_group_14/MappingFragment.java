package com.example.mdp_group_14;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.Switch;
import android.widget.Toast;
import android.widget.ToggleButton;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import java.util.Arrays;

public class MappingFragment extends Fragment {
    private static final String TAG = "MapFragment";

    SharedPreferences mapPref;
    private static SharedPreferences.Editor editor;

    Button updateButton;
    ImageButton resetMapBtn, saveMapObstacle, loadMapObstacle;
    ImageButton directionChangeImageBtn, obstacleImageBtn;
    ToggleButton setStartPointToggleBtn;
    ImageView emergencyBtn; // testing
    int clicks = 0;
    final int THRESHOLD = 5;    // no. of clicks before triggering
    GridMap gridMap;

    Switch dragSwitch;
    Switch changeObstacleSwitch;

    static String imageID="";
    static String imageBearing="North";
    static String path="LL";
    static boolean dragStatus;
    static boolean changeObstacleStatus;

    String direction = "";
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(
            @NonNull LayoutInflater inflater, ViewGroup container,
            Bundle savedInstanceState) {
        View root = inflater.inflate(R.layout.activity_map_config, container,  false);
        SharedPreferences sharedPreferences = getActivity().getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
        editor = sharedPreferences.edit();
        direction = sharedPreferences.getString("direction","");

        if (savedInstanceState != null)
            direction = savedInstanceState.getString("direction");
        gridMap = Home.getGridMap();
        final DirectionsFragment directionFragment = new DirectionsFragment();
        final EmergencyFragment emergencyFragment = new EmergencyFragment();

        resetMapBtn = root.findViewById(R.id.resetBtn);
        setStartPointToggleBtn = root.findViewById(R.id.startpointToggleBtn);
        directionChangeImageBtn = root.findViewById(R.id.changeDirectionBtn);
        obstacleImageBtn = root.findViewById(R.id.addObstacleBtn);
//        updateButton = root.findViewById(R.id.updateMapBtn);
        saveMapObstacle = root.findViewById(R.id.saveBtn);
        loadMapObstacle = root.findViewById(R.id.loadBtn);
        dragSwitch = root.findViewById(R.id.dragSwitch);
        changeObstacleSwitch = root.findViewById(R.id.changeObstacleSwitch);
        // testing
        emergencyBtn = root.findViewById(R.id.eBtn);

        // for hidden functionalities
        emergencyBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                clicks = (clicks + 1) % THRESHOLD;
                showLog("Click count: " + clicks);
                switch(clicks) {
                    case 0:
                        emergencyBtn.setImageDrawable(getResources().getDrawable(R.drawable.snor_0));
                        path = "LL";
                        showLog("Set eBtn to snor_0!");
                        break;
                    case 1:
                        emergencyBtn.setImageDrawable(getResources().getDrawable(R.drawable.snor_1));
                        path = "LR";
                        showLog("Set eBtn to snor_1!");
                        break;
                    case 2:
                        emergencyBtn.setImageDrawable(getResources().getDrawable(R.drawable.snor_2));
                        path = "RL";
                        showLog("Set eBtn to snor_2!");
                        break;
                    case 3:
                        emergencyBtn.setImageDrawable(getResources().getDrawable(R.drawable.snor_3));
                        path = "RR";
                        showLog("Set eBtn to snor_3!");
                        break;
                    case 4:
                        emergencyBtn.setImageDrawable(getResources().getDrawable(R.drawable.snor_4));
                        path = "G";
                        showLog("Set eBtn to snor_4!");
                        break;
                    default:    // should NOT occur
                        showLog("Click count error!!");
                }
                // Display "hidden" message in chat box - in case you forget what each image represents
//                Home.refreshMessageReceivedNS(path);
//                if(clicks >= THRESHOLD) {
                    // emergency protocol

                    // manual input of obstacles - quite shit tbh
//                    showLog("Entered emergencyProtocol");
//                    emergencyFragment.show(getChildFragmentManager(),
//                            "Emergency");
//                    showLog("Exiting emergencyProtocol");

                    // last minute new protocol: to track robot or not
//                    MainActivity.toggleTrackRobot();
//                    showToast("trackRobot: " + MainActivity.getTrackRobot());
//                    MainActivity.refreshMessageReceivedNS("trackRobot: " + MainActivity.getTrackRobot());
                    // reset clicks
//                    clicks = 0;
//                }
            }
        });


        resetMapBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked resetMapBtn");
                showToast("Reseting map...");
                Home.printMessage("CLEAR");
                gridMap.resetMap();

            }
        });

        // switch for dragging
        dragSwitch.setOnCheckedChangeListener( new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton toggleButton, boolean isChecked) {
                showToast("Dragging is " + (isChecked ? "on" : "off"));
                dragStatus = isChecked;
                if (dragStatus) {
                    gridMap.setSetObstacleStatus(false);
                    changeObstacleSwitch.setChecked(false);
                }
            }
        });

        // switch for changing obstacle
        changeObstacleSwitch.setOnCheckedChangeListener( new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton toggleButton, boolean isChecked) {
                showToast("Changing Obstacle is " + (isChecked ? "on" : "off"));
                changeObstacleStatus = isChecked;
                if (changeObstacleStatus) {
                    gridMap.setSetObstacleStatus(false);
                    dragSwitch.setChecked(false);
                }
            }
        });

        setStartPointToggleBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked setStartPointToggleBtn");
                // 2nd consecutive tap on the toggle btn (logic to handle other buttons being tapped is in gridmap.toggleCheckedBtn())
                if (setStartPointToggleBtn.getText().equals("SET START POINT")) {
                    showToast("Cancelled select starting point");
                    setStartPointToggleBtn.setBackgroundResource(R.drawable.border_black);
                }
                else {  // 1st tap on the toggle btn
                    showToast("Please select starting point");
                    gridMap.setStartCoordStatus(true);
                    gridMap.toggleCheckedBtn("setStartPointToggleBtn");
                    setStartPointToggleBtn.setBackgroundResource(R.drawable.border_black_pressed);
                }
            }
        });

        saveMapObstacle.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked saveMapObstacle");
                String getObsPos = "";
                mapPref = getContext().getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
                editor = mapPref.edit();
                if(!mapPref.getString("maps", "").equals("")){
                    editor.putString("maps", "");
                    editor.commit();
                }
                getObsPos = GridMap.saveObstacleList();
                editor.putString("maps",getObsPos);
                editor.commit();
                showToast("Saved map");
            }
        });

        loadMapObstacle.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked loadMapObstacle");
                mapPref = getContext().getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
                String obsPos = mapPref.getString("maps","");
                if(!obsPos.equals("")){

                    String[] obstaclePosition = obsPos.split("\n");
                    for (String s : obstaclePosition) {

                        String[] coords = s.split(",");
//                        BluetoothCommunications.getMessageReceivedTextView().append(Arrays.toString(coords));

//                        String direction2 = "";
//                        switch (coords[2]) {
//                            case "N":
//                                direction2 = "NORTH";
//                                break;
//                            case "E":
//                                direction2 = "EAST";
//                                break;
//                            case "W":
//                                direction2 = "WEST";
//                                break;
//                            case "S":
//                                direction2 = "SOUTH";
//                                break;
//                            default:
//                                direction2 = "null";
//                        }
//
////                        BluetoothCommunications.getMessageReceivedTextView().append(coords[0]);
////                        BluetoothCommunications.getMessageReceivedTextView().append(coords[1]);
////                        BluetoothCommunications.getMessageReceivedTextView().append(direction2);
//
//                        gridMap.imageBearings.get(Integer.parseInt(coords[1]))[Integer.parseInt(coords[0])] = direction2;



//                        gridMap.setObstacleCoord(Integer.parseInt(coords[0]) + 1, Integer.parseInt(coords[1]) + 1, "","");
                        String direction = "";
                        switch (coords[2]) {
                            case "N":
                                direction = "North";
                                break;
                            case "E":
                                direction = "East";
                                break;
                            case "W":
                                direction = "West";
                                break;
                            case "S":
                                direction = "South";
                                break;
                            default:
                                direction = "";
                        }
                        gridMap.imageBearings.get(Integer.parseInt(coords[1]))[Integer.parseInt(coords[0])] = direction;
                        gridMap.setObstacleCoord(Integer.parseInt(coords[0]) + 1, Integer.parseInt(coords[1]) + 1);
                        try {
                            Thread.sleep(50);
                        } catch (InterruptedException e) {
                            throw new RuntimeException(e);
                        }
                    }

                    gridMap.invalidate();
                    showLog("Exiting Load Button");
                    showToast("Loaded saved map");
                }
                showToast("Empty saved map!");
            }
        });


        directionChangeImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked directionChangeImageBtn");
//                directionFragment.show(getActivity().getFragmentManager(),
//                        "Direction Fragment");
//                BluetoothCommunications.getMessageReceivedTextView().append(direction);
                switch(direction)
                {
                    case "None":
                    case "up":
                        direction="right";
                        break;
                    case "right":
                        direction="down";
                        break;
                    case "down":
                        direction="left";
                        break;
                    case "left":
                        direction="up";
                        break;
                }
                editor.putString("direction",direction);
                Home.refreshDirection(direction);
                Toast.makeText(getActivity(), "Saving direction...", Toast.LENGTH_SHORT).show();
                showLog("Exiting saveBtn");
                editor.commit();

                showLog("Exiting directionChangeImageBtn");
            }
        });

        // To place obstacles
        obstacleImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked obstacleImageBtn");

                if (!gridMap.getSetObstacleStatus()) {  // if setObstacleStatus is false
                    showToast("Please plot obstacles");
                    gridMap.setSetObstacleStatus(true);
                    gridMap.toggleCheckedBtn("obstacleImageBtn");
                    obstacleImageBtn.setBackgroundResource(R.drawable.border_black_pressed);
                }
                else if (gridMap.getSetObstacleStatus()) {  // if setObstacleStatus is true
                    gridMap.setSetObstacleStatus(false);
                    obstacleImageBtn.setBackgroundResource(R.drawable.border_black);
                }
                // disable the other on touch functions
                changeObstacleSwitch.setChecked(false);
                dragSwitch.setChecked(false);
                showLog("obstacle status = " + gridMap.getSetObstacleStatus());
                showLog("Exiting obstacleImageBtn");
            }
        });

        //preload defaults button
//        updateButton.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View v) {
//                showLog("Clicked updateButton");
//
//                gridMap.imageBearings.get(9)[5] = "South";
//                gridMap.imageBearings.get(15)[15] = "South";
//                gridMap.imageBearings.get(14)[7] = "West";
//                gridMap.imageBearings.get(4)[15] = "West";
//                gridMap.imageBearings.get(9)[12] = "East";
//                gridMap.setObstacleCoord(5+1, 9+1);
//                gridMap.setObstacleCoord(15+1, 15+1);
//                gridMap.setObstacleCoord(7+1, 14+1);
//                gridMap.setObstacleCoord(15+1, 4+1);
//                gridMap.setObstacleCoord(12+1, 9+1);
//                gridMap.invalidate();
//                updateStatus("i say dont click right why u still click????");
//                showLog("Exiting updateButton");
//            }
//        });
        return root;
    }

    private void showLog(String message) {
        Log.d(TAG, message);
    }

    private void showToast(String message) {
        Toast.makeText(getContext(), message, Toast.LENGTH_SHORT).show();
    }
    private void updateStatus(String message) {
        Toast toast = Toast.makeText(getContext(), message, Toast.LENGTH_SHORT);
        toast.setGravity(Gravity.TOP,0, 0);
        toast.show();
    }
}
