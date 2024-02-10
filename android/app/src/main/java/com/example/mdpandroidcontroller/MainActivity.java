package com.example.mdpandroidcontroller;

import android.Manifest;
import android.app.AlertDialog;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.ClipData;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.os.Bundle;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import android.os.Handler;
import android.os.IBinder;
import android.util.Log;

import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.core.app.ActivityCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;

import android.util.TypedValue;
import android.view.DragEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import com.example.mdpandroidcontroller.databinding.ActivityMainBinding;
import com.google.android.material.snackbar.Snackbar;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Observable;
import java.util.Observer;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {

    private AppBarConfiguration appBarConfiguration;
    private ActivityMainBinding binding;

    private static Context context;

    private static final String[] BL_PERMISSIONS = new String[]{
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.BLUETOOTH_ADVERTISE,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.BLUETOOTH_SCAN
    };
    private static final int BT1_PERMISSION_CODE = 101;
    private static final int BT2_PERMISSION_CODE = 102;
    private static final int BT3_PERMISSION_CODE = 103;
    private static final int BT4_PERMISSION_CODE = 104;
    private static final int BT5_PERMISSION_CODE = 105;
    private static final int BT6_PERMISSION_CODE = 106;
    private static final int BT7_PERMISSION_CODE = 107;
    private static final int request_code = 200;

    private static final int REQUEST_ENABLE_BT = 0;
    private static final int REQUEST_DISCOVER_BT = 1;

    TextView mStatusBlueTv;
    TextView mPairedTv;

    Button mOnBtn;
    Button mOffBtn;
    Button mDiscoverBtn;
    Button mPairedBtn;

    ListView listview;

    ListView listview_paireddevices;
    ListView listview_availabledevices;
    ArrayList<String> availabledevicelist = new ArrayList<>();
    ArrayList<String> paireddevicelist = new ArrayList<>();
    ArrayList<BluetoothDevice> mBTDevices = new ArrayList<>();
    ArrayList<BluetoothDevice> mPairDevices = new ArrayList<>();

    private static final String TAG = "btlog";

    private static final UUID my_uuid_insecure = UUID.fromString("8ce255c0-200a-11e0-ac64-0800200c9a66");

    BluetoothDevice mBTDevice;
    BluetoothDevice mPairDevice;
    BluetoothAdapter myBluetoothAdapter;

    //BluetoothConnectionService mBluetoothConnection;

    // grid stuff
    private static Map map;
    private static int mapLeft; // only at robot generate button
    private static int mapTop;
    private static int rotation = 0;

    private static ConstraintLayout obstacle1Grp;
    private static ImageView obstacle1Box;
    private static ImageView obstacle1Face;
    private static TextView obstacle1Id;

    private static ConstraintLayout obstacle2Grp;
    private static ImageView obstacle2Box;
    private static ImageView obstacle2Face;
    private static TextView obstacle2Id;

    private static ConstraintLayout obstacle3Grp;
    private static ImageView obstacle3Box;
    private static ImageView obstacle3Face;
    private static TextView obstacle3Id;

    private static ConstraintLayout obstacle4Grp;
    private static ImageView obstacle4Box;
    private static ImageView obstacle4Face;
    private static TextView obstacle4Id;

    private static ConstraintLayout obstacle5Grp;
    private static ImageView obstacle5Box;
    private static ImageView obstacle5Face;
    private static TextView obstacle5Id;

    private static ConstraintLayout obstacle6Grp;
    private static ImageView obstacle6Box;
    private static ImageView obstacle6Face;
    private static TextView obstacle6Id;

    private static ConstraintLayout obstacle7Grp;
    private static ImageView obstacle7Box;
    private static ImageView obstacle7Face;
    private static TextView obstacle7Id;

    private static ConstraintLayout obstacle8Grp;
    private static ImageView obstacle8Box;
    private static ImageView obstacle8Face;
    private static TextView obstacle8Id;


    private static ImageView obstacleFaceCur;

    private static String obstacleFaceText;
    private static int obstacleFaceNumber;

    private static TextView outputNotifView; // for all the notifications!!
    private static TextView locationNotifView;
    private static TextView facingNotifView;

    private static String outputNotif;
    private static String locationNotif;
    private static String facingNotif;

    //private static Boolean connected;

    private static String instruction = "Robot, 4, 10, S";

    private static ConstraintLayout popup;
    private static ConstraintLayout robot_popup;
    private static Switch reverseSwitch;

    private static int robotColPopup = 1;
    private static int robotRowPopup = 1;
    private static String robotFacingPopup = "N";

    private static ImageView robot;
    float pastX, pastY;
    private static String longPress;

    private Runnable runnable;
    private Handler handler;

    TextView incomingMessages;
    StringBuilder messages;
    Intent connectIntent;


    private static int[][] originalObstacleCoords = new int[8][2];

    private static int[][] currentObstacleCoords = new int[8][2]; // remember to expand this


    // this one is for constraint
    private List<ConstraintLayout> obstacleViews = new ArrayList<>(); // cant be static!! - COS ITS REGENRATED ALL THE TIME - change eventually.

    // for the face views
    private List<ImageView> obstacleFaceViews = new ArrayList<>();
    private List<TextView> obstacleTextViews = new ArrayList<>();
    private List<ImageView> obstacleBoxViews = new ArrayList<>();

    boolean connectedState = false;
    static String connectedDevice;
    BluetoothDevice myBTConnectionDevice;
    boolean currentActivity;

    private boolean mBound = false;

    //UUID
    private static final UUID myUUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    BluetoothAdapter mBlueAdapter = BluetoothAdapter.getDefaultAdapter();
    ActivityResultLauncher<Intent> activityResultLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            result -> {
                if (result.getResultCode() == Activity.RESULT_OK) {
                    Log.e("Activity result", "OK");
                    // There are no request codes
                    Intent data = result.getData();
                }
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        setSupportActionBar(binding.toolbar);

        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        appBarConfiguration = new AppBarConfiguration.Builder(navController.getGraph()).build();
        NavigationUI.setupActionBarWithNavController(this, navController, appBarConfiguration);


        //mStatusBlueTv = findViewById(R.id.statusBluetoothTv);

        //REGISTER BROADCAST RECEIVER FOR INCOMING MSG
        LocalBroadcastManager.getInstance(this).registerReceiver(btConnectionReceiver, new IntentFilter("btConnectionStatus"));
        connectedDevice = null;
        currentActivity = true;

        //REGISTER BROADCAST RECEIVER FOR IMCOMING MSG
        //LocalBroadcastManager.getInstance(this).registerReceiver(incomingMsgReceiver, new IntentFilter("IncomingMsg"));




        //GUI

        map = findViewById(R.id.mapView);
        for (int i = 0; i < originalObstacleCoords.length; i++) {
            for (int j = 0; j < originalObstacleCoords[i].length; j++) {
                originalObstacleCoords[i][j] = -1;
            }
        }

        //TEST INSTRUCTION
        if (!Constants.instruction.equals("null")) {
            System.out.println("AT VIEW CREATE");
            System.out.println(Constants.instruction);
            executeInstruction();
        }


        //OLD ON VIEW CREATED


        System.out.println("OnViewCreated");

        //LISTEN FOR COMMANDS
        MySubject subject = new MySubject();
        MyObserver observer = new MyObserver(subject);
        Constants constants = new Constants(subject);


        //CHECK THIS - MIGHT NOT EVEN NEED THIS!!
        obstacle1Grp = (ConstraintLayout) findViewById(R.id.obstacle1Group);
        obstacle1Box = (ImageView) findViewById(R.id.obstacle1Box);
        obstacle1Face = (ImageView) findViewById(R.id.obstacle1Face);
        obstacle1Id = (TextView) findViewById(R.id.obstacle1ID);

        obstacle2Grp = (ConstraintLayout) findViewById(R.id.obstacle2Group);
        obstacle2Box = (ImageView) findViewById(R.id.obstacle2Box);
        obstacle2Face = (ImageView) findViewById(R.id.obstacle2Face);
        obstacle2Id = (TextView) findViewById(R.id.obstacle2ID);

        obstacle3Grp = (ConstraintLayout) findViewById(R.id.obstacle3Group);
        obstacle3Box = (ImageView) findViewById(R.id.obstacle3Box);
        obstacle3Face = (ImageView) findViewById(R.id.obstacle3Face);
        obstacle3Id = (TextView) findViewById(R.id.obstacle3ID);

        obstacle4Grp = (ConstraintLayout) findViewById(R.id.obstacle4Group);
        obstacle4Box = (ImageView) findViewById(R.id.obstacle4Box);
        obstacle4Face = (ImageView) findViewById(R.id.obstacle4Face);
        obstacle4Id = (TextView) findViewById(R.id.obstacle4ID);

        obstacle5Grp = (ConstraintLayout) findViewById(R.id.obstacle5Group);
        obstacle5Box = (ImageView) findViewById(R.id.obstacle5Box);
        obstacle5Face = (ImageView) findViewById(R.id.obstacle5Face);
        obstacle5Id = (TextView) findViewById(R.id.obstacle5ID);

        obstacle6Grp = (ConstraintLayout) findViewById(R.id.obstacle6Group);
        obstacle6Box = (ImageView) findViewById(R.id.obstacle6Box);
        obstacle6Face = (ImageView) findViewById(R.id.obstacle6Face);
        obstacle6Id = (TextView) findViewById(R.id.obstacle6ID);

        obstacle7Grp = (ConstraintLayout) findViewById(R.id.obstacle7Group);
        obstacle7Box = (ImageView) findViewById(R.id.obstacle7Box);
        obstacle7Face = (ImageView) findViewById(R.id.obstacle7Face);
        obstacle7Id = (TextView) findViewById(R.id.obstacle7ID);

        obstacle8Grp = (ConstraintLayout) findViewById(R.id.obstacle8Group);
        obstacle8Box = (ImageView) findViewById(R.id.obstacle8Box);
        obstacle8Face = (ImageView) findViewById(R.id.obstacle8Face);
        obstacle8Id = (TextView) findViewById(R.id.obstacle8ID);


        //TEXTVIEWS
        outputNotifView = (TextView) findViewById(R.id.notifications);
        locationNotifView = (TextView) findViewById(R.id.robot_location);
        facingNotifView = (TextView) findViewById(R.id.robot_facing);


        // add to lists
        obstacleViews.add(obstacle1Grp);
        obstacleViews.add(obstacle2Grp);
        obstacleViews.add(obstacle3Grp);
        obstacleViews.add(obstacle4Grp);
        obstacleViews.add(obstacle5Grp);
        obstacleViews.add(obstacle6Grp);
        obstacleViews.add(obstacle7Grp);
        obstacleViews.add(obstacle8Grp);

        obstacleFaceViews.add(obstacle1Face);
        obstacleFaceViews.add(obstacle2Face);
        obstacleFaceViews.add(obstacle3Face);
        obstacleFaceViews.add(obstacle4Face);
        obstacleFaceViews.add(obstacle5Face);
        obstacleFaceViews.add(obstacle6Face);
        obstacleFaceViews.add(obstacle7Face);
        obstacleFaceViews.add(obstacle8Face);

        obstacleTextViews.add(obstacle1Id);
        obstacleTextViews.add(obstacle2Id);
        obstacleTextViews.add(obstacle3Id);
        obstacleTextViews.add(obstacle4Id);
        obstacleTextViews.add(obstacle5Id);
        obstacleTextViews.add(obstacle6Id);
        obstacleTextViews.add(obstacle7Id);
        obstacleTextViews.add(obstacle8Id);

        obstacleBoxViews.add(obstacle1Box);
        obstacleBoxViews.add(obstacle2Box);
        obstacleBoxViews.add(obstacle3Box);
        obstacleBoxViews.add(obstacle4Box);
        obstacleBoxViews.add(obstacle5Box);
        obstacleBoxViews.add(obstacle6Box);
        obstacleBoxViews.add(obstacle7Box);
        obstacleBoxViews.add(obstacle8Box);

        popup = (ConstraintLayout) findViewById(R.id.popup_window);
        popup.setVisibility(View.INVISIBLE);

        robot_popup = (ConstraintLayout) findViewById(R.id.popup_window_robot);
        robot_popup.setVisibility(View.INVISIBLE);

        // reverse
        reverseSwitch = (Switch) findViewById(R.id.reverse_switch);

        //set face views invisible
        for (int i = 0; i < obstacleFaceViews.size(); i++) {
            obstacleFaceViews.get(i).setVisibility(View.INVISIBLE);
        }


        printAllObstacleCoords();
        printAllObstacleLeftTop();


        obstacle1Grp.post(new Runnable() {
            @Override
            public void run() {
                System.out.println("current coordinates");
                printAllObstacleCoords();
                printAllObstacleLeftTop();

                //SET THE SIZES CORRECTLY JIC - RMB ITS THE BOX NOT THE WHOLE CONSTRAINT

                for (int i = 0; i < obstacleBoxViews.size(); i++) {
                    obstacleBoxViews.get(i).getLayoutParams().height = (int) map.getCellSize();
                    obstacleBoxViews.get(i).getLayoutParams().width = (int) map.getCellSize();
                    obstacleBoxViews.get(i).requestLayout();
                }

                for (int i = 0; i < obstacleFaceViews.size(); i++) {
                    obstacleFaceViews.get(i).getLayoutParams().height = (int) map.getCellSize();
                    obstacleFaceViews.get(i).getLayoutParams().width = (int) map.getCellSize();
                    obstacleFaceViews.get(i).requestLayout();
                }

                robot.getLayoutParams().height = (int) map.getCellSize() * 3;
                robot.getLayoutParams().width = (int) map.getCellSize() * 3;
                robot.requestLayout();

                //reverse
                reverseSwitch.setChecked(false);  // default = false: not reverse

                //MAP coordinates - for saving
                mapLeft = map.getLeft();
                mapTop = map.getTop();

                // save original coords of obstacles
                for (int i = 0; i < obstacleViews.size(); i++) {
                    originalObstacleCoords[i][0] = (int) obstacleViews.get(i).getLeft();
                    originalObstacleCoords[i][1] = (int) obstacleViews.get(i).getTop();
                }
                printOriginalObstacleCoords();
                reset(false);
            }
        });


        //ROBOT settings - KEEP IT INVISIBLE AT FIRST
        robot = (ImageView) findViewById(R.id.robotcar);

        if (map.getCanDrawRobot()) {
            robot.setVisibility(View.VISIBLE);
            rotation = map.convertFacingToRotation(map.getRobotFacing());
            trackRobot();
        } else {
            robot.setVisibility(View.INVISIBLE);
        }


        findViewById(R.id.connect_button).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                /*Intent intent = new Intent(getContext(), SecondFragment.class);
                BluetoothServices bluetoothServices = new BluetoothServices();
                intent.putExtra("bluetooth_services", bluetoothServices);
                startActivity(intent);*/

                Intent intent = new Intent(MainActivity.this, Connect.class);
                startActivity(intent);
            }
        });

        findViewById(R.id.discoverableBtn).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                bluetooth_discoverable();
            }
        });


        // NEW Short press and Long Press for ALL BUTTONS
        ImageButton forwardButton = (ImageButton) findViewById(R.id.arrowForward);
        ImageButton rightButton = (ImageButton) findViewById(R.id.arrowRight);
        ImageButton leftButton = (ImageButton) findViewById(R.id.arrowLeft);
        ImageButton backButton = (ImageButton) findViewById(R.id.arrowBack);

        View.OnClickListener movementOnClickListener = new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (robot.getVisibility() == View.INVISIBLE) {
                    return;
                }
                //byte[] bytes = "f".getBytes(Charset.defaultCharset());
                String instruction1 = "_";
                switch (view.getId()) {
                    case R.id.arrowForward:
                        masterRobotMovement(Constants.UP);
                        instruction1 = "f";
                        break;
                    case R.id.arrowRight:
                        masterRobotMovement(Constants.RIGHT);
                        instruction1 = "sr";
                        break;
                    case R.id.arrowLeft:
                        masterRobotMovement(Constants.LEFT);
                        instruction1 = "sl";
                        break;
                    case R.id.arrowBack:
                        masterRobotMovement(Constants.DOWN);
                        instruction1 = "r";
                        break;
                }

                if (Constants.connected) {
                    System.out.println("first fragment - HI ITS CONNECTED");
                    byte[] bytes = instruction1.getBytes(Charset.defaultCharset());
                    BluetoothChat.writeMsg(bytes);
                } else {
                    System.out.println("first fragment - NOT CONNECTED");
                }
            }
        };

        View.OnLongClickListener movementOnLongClickListener = new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View view) {
                if (robot.getVisibility() == View.INVISIBLE) {
                    return false;
                }
                handler.removeCallbacks(runnable);
                handler.post(runnable);
                String instruction2 = "_";

                switch (view.getId()) {
                    case R.id.arrowForward:
                        longPress = Constants.UP;
                        instruction2 = "f";
                        break;
                    case R.id.arrowRight:
                        longPress = Constants.RIGHT;
                        instruction2 = "sr";
                        break;
                    case R.id.arrowLeft:
                        longPress = Constants.LEFT;
                        instruction2 = "sl";
                        break;
                    case R.id.arrowBack:
                        longPress = Constants.DOWN;
                        instruction2 = "r";
                        break;
                }
                if (Constants.connected) {
                    System.out.println("HI ITS CONNECTED");
                    byte[] bytes = instruction2.getBytes(Charset.defaultCharset());
                    BluetoothChat.writeMsg(bytes);
                } else {
                    System.out.println("NOT CONNECTED");
                }

                return true;
            }
        };

        View.OnTouchListener movementOnTouchListener = new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (robot.getVisibility() == View.INVISIBLE) {
                    return false;
                }
                if (event.getAction() == MotionEvent.ACTION_UP) {
                    handler.removeCallbacks(runnable);
                }
                return false;
            }
        };

        forwardButton.setOnClickListener(movementOnClickListener);
        forwardButton.setOnLongClickListener(movementOnLongClickListener);
        forwardButton.setOnTouchListener(movementOnTouchListener);

        rightButton.setOnClickListener(movementOnClickListener);
        rightButton.setOnLongClickListener(movementOnLongClickListener);
        rightButton.setOnTouchListener(movementOnTouchListener);

        leftButton.setOnClickListener(movementOnClickListener);
        leftButton.setOnLongClickListener(movementOnLongClickListener);
        leftButton.setOnTouchListener(movementOnTouchListener);

        backButton.setOnClickListener(movementOnClickListener);
        backButton.setOnLongClickListener(movementOnLongClickListener);
        backButton.setOnTouchListener(movementOnTouchListener);

        handler = new Handler();
        runnable = new Runnable() {
            @Override
            public void run() {
                switch (longPress) {
                    case Constants.UP:
                        masterRobotMovement(Constants.UP);
                        break;
                    case Constants.RIGHT:
                        masterRobotMovement(Constants.RIGHT);
                        break;
                    case Constants.DOWN:
                        masterRobotMovement(Constants.DOWN);
                        break;
                    case Constants.LEFT:
                        masterRobotMovement(Constants.LEFT);
                        break;
                    default:
                        System.out.println("somehow its still null for buttonpress");
                }
                handler.postDelayed(runnable, 100);
            }
        };


        reverseSwitch.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (reverseSwitch.isChecked()) {
                    reverseSwitch.setChecked(true);
                } else {
                    reverseSwitch.setChecked(false);
                }
            }
        });


        //OBSTACLES
        View.OnTouchListener obstacleOnTouchListener = new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {
                if (motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    ClipData data = ClipData.newPlainText("", "");
                    View.DragShadowBuilder shadowBuilder = new View.DragShadowBuilder(view);
                    view.startDrag(data, shadowBuilder, view, 0);

                    switch (view.getId()) {
                        case R.id.obstacle1Group:
                            pastX = obstacle1Grp.getX();
                            pastY = obstacle1Grp.getY();
                            break;
                        case R.id.obstacle2Group:
                            pastX = obstacle2Grp.getX();
                            pastY = obstacle2Grp.getY();
                            break;
                        case R.id.obstacle3Group:
                            pastX = obstacle3Grp.getX();
                            pastY = obstacle3Grp.getY();
                            break;
                        case R.id.obstacle4Group:
                            pastX = obstacle4Grp.getX();
                            pastY = obstacle4Grp.getY();
                            break;
                        case R.id.obstacle5Group:
                            pastX = obstacle5Grp.getX();
                            pastY = obstacle5Grp.getY();
                            break;
                        case R.id.obstacle6Group:
                            pastX = obstacle6Grp.getX();
                            pastY = obstacle6Grp.getY();
                            break;
                        case R.id.obstacle7Group:
                            pastX = obstacle7Grp.getX();
                            pastY = obstacle7Grp.getY();
                            break;
                        case R.id.obstacle8Group:
                            pastX = obstacle8Grp.getX();
                            pastY = obstacle8Grp.getY();
                            break;
                    }
                    return true;
                } else {
                    return false;
                }
            }
        };

        obstacle1Grp.setOnTouchListener(obstacleOnTouchListener);
        obstacle2Grp.setOnTouchListener(obstacleOnTouchListener);
        obstacle3Grp.setOnTouchListener(obstacleOnTouchListener);
        obstacle4Grp.setOnTouchListener(obstacleOnTouchListener);
        obstacle5Grp.setOnTouchListener(obstacleOnTouchListener);
        obstacle6Grp.setOnTouchListener(obstacleOnTouchListener);
        obstacle7Grp.setOnTouchListener(obstacleOnTouchListener);
        obstacle8Grp.setOnTouchListener(obstacleOnTouchListener);

        /**
         * finally works - resets all obstacles to the original coordinates
         */
        ImageButton resetObstacles = (ImageButton) findViewById(R.id.resetObstacles);
        resetObstacles.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                reset(true);
            }
        });


        //POPUP BUTTONS
        ImageButton startRobot = (ImageButton) findViewById(R.id.start_robot);
        startRobot.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //executeInstruction();
                outputNotif = String.format("run");
                outputNotifView.setText(outputNotif);

                if (Constants.connected) {
                    Snackbar snackbar = Snackbar.make(getWindow().getDecorView(), "Start Robot", Snackbar.LENGTH_SHORT);
                    snackbar.show();

                    byte[] bytes = outputNotif.getBytes(Charset.defaultCharset());
                    BluetoothChat.writeMsg(bytes);
                }
            }
        });

        ImageButton calculatePath = (ImageButton) findViewById(R.id.calculate);
        calculatePath.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //executeInstruction();
                outputNotif = String.format("path");
                outputNotifView.setText(outputNotif);

                if (Constants.connected) {
                    Snackbar snackbar = Snackbar.make(getWindow().getDecorView(), "Calculate path", Snackbar.LENGTH_SHORT);
                    snackbar.show();

                    byte[] bytes = outputNotif.getBytes(Charset.defaultCharset());
                    BluetoothChat.writeMsg(bytes);
                }
            }
        });


        /**
         * Create the robot button - make it visible and decide the coordinates.
         */
        ImageButton robotButton = (ImageButton) findViewById(R.id.generateRobot);
        robotButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (robot_popup.getVisibility() == View.VISIBLE) {
                    robot_popup.setVisibility(View.INVISIBLE);
                } else {
                    // Automate the chosen obstacle number first!!

                    robot_popup.setVisibility(View.VISIBLE);
                }
            }
        });

        Spinner spinnerRobotX = findViewById(R.id.spinner_robot_x);
        Spinner spinnerRobotY = findViewById(R.id.spinner_robot_y);
        ArrayAdapter<CharSequence> adapterRobot = ArrayAdapter.createFromResource(
                MainActivity.this,
                R.array.spinner_robot_coord,
                android.R.layout.simple_spinner_item
        );
        adapterRobot.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerRobotX.setAdapter(adapterRobot);
        spinnerRobotY.setAdapter(adapterRobot);

        Spinner spinnerRobotFacing = findViewById(R.id.spinner_robot_facing);
        ArrayAdapter<CharSequence> adapterRobotFacing = ArrayAdapter.createFromResource(
                MainActivity.this,
                R.array.spinner_robot_facing,
                android.R.layout.simple_spinner_item
        );
        adapterRobotFacing.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerRobotFacing.setAdapter(adapterRobotFacing);


        spinnerRobotX.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                robotColPopup = Integer.parseInt(parent.getItemAtPosition(position).toString());
                System.out.printf("COL: %d\n", robotColPopup);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                // Do nothing
            }
        });
        spinnerRobotY.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                robotRowPopup = Integer.parseInt(parent.getItemAtPosition(position).toString());
                System.out.printf("ROW: %d\n", robotRowPopup);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                // Do nothing
            }
        });
        spinnerRobotFacing.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                robotFacingPopup = parent.getItemAtPosition(position).toString();
                System.out.printf("FACING: %s\n", robotFacingPopup);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                // Do nothing
            }
        });

        Button confirmRobot = (Button) findViewById(R.id.finalise_robot);
        confirmRobot.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (robot.getVisibility() == View.VISIBLE) {
                    map.setOldRobotCoord(map.getCurCoord()[0], map.getCurCoord()[1]);
                }
                map.saveFacingWithRotation(rotation);
                map.setCanDrawRobot(true);
                map.setCurCoord(robotColPopup, robotRowPopup);
                robot.setVisibility(View.VISIBLE);
                rotation = map.convertFacingToRotation(robotFacingPopup);
                trackRobot();
                map.invalidate();

                robot_popup.setVisibility(View.INVISIBLE);
            }
        });
        Button removeRobot = (Button) findViewById(R.id.remove_robot);
        removeRobot.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                map.setCanDrawRobot(false);
                robot.setVisibility(View.INVISIBLE);
                map.setOldRobotCoord(map.getCurCoord()[0], map.getCurCoord()[1]);
                robot_popup.setVisibility(View.INVISIBLE);
                map.invalidate();
            }
        });


        /**
         * POPUP disappears when the view clicked is not the popup_window!
         */
        View rootView = findViewById(R.id.first_fragment);
        rootView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (view.getId() != R.id.popup_window) {
                    popup.setVisibility(View.GONE);
                    robot_popup.setVisibility(View.GONE);
                }
            }
        });


        /**
         * //drop down for the face
         */
        Spinner spinner = findViewById(R.id.spinner);
        ArrayAdapter<CharSequence> adapterObst = ArrayAdapter.createFromResource(
                MainActivity.this,
                R.array.spinner_array,
                android.R.layout.simple_spinner_item
        );
        adapterObst.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapterObst);

        spinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                obstacleFaceNumber = Integer.parseInt(parent.getItemAtPosition(position).toString());
                // Do something with the selected item
                System.out.println(obstacleFaceNumber);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                // Do nothing
            }
        });

        Button northFace = (Button) findViewById(R.id.face_north);
        Button eastFace = (Button) findViewById(R.id.face_east);
        Button southFace = (Button) findViewById(R.id.face_south);
        Button westFace = (Button) findViewById(R.id.face_west);

        /**
         * Relevant for all obstacles!
         * If u press the option again, the face will be invisible!
         * If its a different orientation, then the view will be rotated.
         */
        View.OnClickListener onClickFaceListener = new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                obstacleFaceCur = obstacleFaceViews.get(obstacleFaceNumber - 1);
                ConstraintLayout obstacleGroup = obstacleViews.get(obstacleFaceNumber - 1);

                String facing = "error";

                switch (view.getId()) {
                    case R.id.face_north:
                        if (obstacleFaceCur.getRotation() == 0 && obstacleFaceCur.getVisibility() == View.VISIBLE) {
                            obstacleFaceCur.setVisibility(View.INVISIBLE);
                        } else {
                            obstacleFaceCur.setVisibility(View.VISIBLE);
                            obstacleFaceCur.setRotation(0);
                            facing = "N";
                        }
                        break;
                    case R.id.face_east:
                        if (obstacleFaceCur.getRotation() == 90 && obstacleFaceCur.getVisibility() == View.VISIBLE) {
                            obstacleFaceCur.setVisibility(View.INVISIBLE);
                        } else {
                            obstacleFaceCur.setVisibility(View.VISIBLE);
                            obstacleFaceCur.setRotation(90);
                            facing = "E";
                        }
                        break;
                    case R.id.face_south:
                        if (obstacleFaceCur.getRotation() == 180 && obstacleFaceCur.getVisibility() == View.VISIBLE) {
                            obstacleFaceCur.setVisibility(View.INVISIBLE);
                        } else {
                            obstacleFaceCur.setVisibility(View.VISIBLE);
                            obstacleFaceCur.setRotation(180);
                            facing = "S";
                        }
                        break;
                    case R.id.face_west:
                        if (obstacleFaceCur.getRotation() == 270 && obstacleFaceCur.getVisibility() == View.VISIBLE) {
                            obstacleFaceCur.setVisibility(View.INVISIBLE);
                        } else {
                            obstacleFaceCur.setVisibility(View.VISIBLE);
                            obstacleFaceCur.setRotation(270);
                            facing = "W";
                        }
                        break;
                }

                int obstacleNum = getObstacleNumber(obstacleGroup);
                int[] currentColRow = map.getColRowFromXY(obstacleGroup.getX(), obstacleGroup.getY(), map.getLeft(), map.getTop());

                //FOR CHECKLIST
                //outputNotif = String.format("Facing: %s, Col: %d, Row: %d\n", facing, currentColRow[0], currentColRow[1]);
                outputNotif = String.format("Obstacle: %d, Facing: %s", obstacleNum, facing);
                if (!facing.equals("error")) {
                    System.out.printf(outputNotif);
                    System.out.println();
                    outputNotifView.setText(outputNotif);

                    //SEND VALUE
                    if (Constants.connected) {
                        byte[] bytes = outputNotif.getBytes(Charset.defaultCharset());
                        BluetoothChat.writeMsg(bytes);
                    }
                }

            }
        };

        northFace.setOnClickListener(onClickFaceListener);
        eastFace.setOnClickListener(onClickFaceListener);
        southFace.setOnClickListener(onClickFaceListener);
        westFace.setOnClickListener(onClickFaceListener);


        /** WHOLE Dropping segment of the obstacles on the map - Do clean up q hard to understand! lots of considerations.
         *
         */
        map.setOnDragListener(new View.OnDragListener() {
            @Override
            public boolean onDrag(View view, DragEvent dragEvent) {

                int action = dragEvent.getAction();
                switch (action) {
                    case DragEvent.ACTION_DRAG_STARTED:
                        // Do nothing
                        break;
                    case DragEvent.ACTION_DRAG_ENTERED:
                        // Highlight the cell on the chess board where the piece is being dragged over
                        break;
                    case DragEvent.ACTION_DRAG_EXITED:
                        // Remove the highlight from the cell
                        break;
                    case DragEvent.ACTION_DROP:
                        // when dropped into the grid
                        ConstraintLayout curObstacleGrp = (ConstraintLayout) dragEvent.getLocalState();

                        int x = (int) dragEvent.getX();
                        int y = (int) dragEvent.getY();


                        // this is the exact location - but we want to snap to grid //myImage.setX(x + map.getX() - map.getCellSize()/2); //myImage.setY(y+ map.getY() - map.getCellSize()/2);
                        // if the past location of obstacle was in the map, u remove the old one.
                        if (pastX >= map.getX() && pastX <= map.getX() + map.getWidth() && pastY >= map.getY() && pastY <= map.getY() + map.getHeight()) {
                            //System.out.println("IN MAP");
                            map.removeObstacleUsingCoord(pastX - map.getX() + map.getCellSize() / 2, pastY - map.getY() + map.getCellSize() / 2);
                        }


                        // to add the new obstacle black square - returns the coordinates, col and row --> (x, y, col, row)
                        int[] newObstCoordColRow = map.updateObstacleOnBoard(x, y);


                        //getting the notification to print!!
                        System.out.println("Notification values:");
                        int obstacleNum = getObstacleNumber(curObstacleGrp);
                        int col = newObstCoordColRow[2];
                        int row = newObstCoordColRow[3];
                        outputNotif = String.format("Obstacle: %d, Col: %d, Row: %d", obstacleNum, col, row);
                        System.out.printf(outputNotif);
                        System.out.println();
                        outputNotifView.setText(outputNotif);


                        //others
                        int[] newObstacleCoord = {newObstCoordColRow[0], newObstCoordColRow[1]};
                        newObstacleCoord[0] = newObstacleCoord[0] + (int) (map.getX());  // NEW 6 feb
                        newObstacleCoord[1] = newObstacleCoord[1] + (int) (map.getY());

                        //WHEN U JUST CLICK IT ONLY - releases the popupwindow
                        if (currentObstacleCoords[obstacleNum - 1][0] == newObstacleCoord[0] && currentObstacleCoords[obstacleNum - 1][1] == newObstacleCoord[1]) {
                            spinner.setSelection(obstacleNum - 1);
                            popup.setVisibility(View.VISIBLE);
                        } else {
                            //SEND to RPI - if not a ®click!! - MESSAGE
                            if (Constants.connected) {
                                byte[] bytes = outputNotif.getBytes(Charset.defaultCharset());
                                BluetoothChat.writeMsg(bytes);
                            }
                        }

                        //saving the current obstacles
                        currentObstacleCoords[obstacleNum - 1] = newObstacleCoord;

                        // MUST get from the map class to snap to grid - for the new image
                        curObstacleGrp.setX(newObstacleCoord[0]); //+ map.getX()); // SHOULD BE INBUILT!!
                        curObstacleGrp.setY(newObstacleCoord[1]); // + map.getY());
                        printAllObstacleCoords();

                        map.invalidate();

                        break;
                    case DragEvent.ACTION_DRAG_ENDED:
                        // Remove the highlight from the cell
                        break;
                    default:
                        break;
                }
                return true;
            }
        });

        /**
         * when the drop of the obstacle is out of the map, move it to the original starting place
         */
        ViewGroup parentView = (ViewGroup) map.getParent();
        parentView.setOnDragListener(new View.OnDragListener() {
            @Override
            public boolean onDrag(View view, DragEvent event) {
                int x = (int) event.getX();
                int y = (int) event.getY();
                int mapWidth = map.getWidth();
                int mapHeight = map.getHeight();
                int[] mapCoord = new int[2];
                map.getLocationOnScreen(mapCoord);

                if (event.getAction() == DragEvent.ACTION_DROP) {
                    if (x < mapCoord[0] || x > mapCoord[0] + mapWidth || y < mapCoord[1] || y > mapCoord[1] + mapHeight) {

                        //System.out.println("out of map");
                        ConstraintLayout curObstacleGrp = (ConstraintLayout) event.getLocalState();

                        // loop through obstacleviews to find the obstacle name
                        // set according to obstacle coord
                        for (int i = 0; i < obstacleViews.size(); i++) {
                            if (curObstacleGrp == obstacleViews.get(i)) {
                                curObstacleGrp.setX(originalObstacleCoords[i][0]);
                                curObstacleGrp.setY(originalObstacleCoords[i][1]);
                                break; // i just tried adding this
                            }
                        }
                        //reset coordinates of current.
                        int index = getObstacleNumber(curObstacleGrp);
                        currentObstacleCoords[index - 1][0] = 0;
                        currentObstacleCoords[index - 1][1] = 0;

                        printAllObstacleCoords();

                        // in of map to out of map!!
                        if (pastX >= mapCoord[0] && pastX <= mapCoord[0] + mapWidth && pastY >= mapCoord[1] && pastY <= mapCoord[1] + mapHeight) {
                            map.removeObstacleUsingCoord(pastX - map.getX() + map.getCellSize() / 2, pastY - map.getY() + map.getCellSize() / 2);
                            map.invalidate();
                        }

                    } else {
                        // obstacle was dropped inside the map
                    }
                }
                return true;
            }
        });


    }

    // ---------------------------- GUI ---------------------------- IDK ABT ONRESUME, ON PAUSE

    /**
     * Summarize the move buttons actions.
     * @param direction
     */
    public void masterRobotMovement(String direction) {
        // setting variables
        map.saveFacingWithRotation(rotation);
        map.setRobotMovement(direction);
        map.setRobotReverse(reverseSwitch.isChecked());
        //actual movement
        map.moveRobot();
        map.invalidate();
        rotation = map.convertFacingToRotation(map.getRobotFacing());
        trackRobot();
    }

    /** RUNS EVERYTIME robot moves!!
     * Purpose is to track the image of the robot to the current coord of the robot in map class. and follows the right rotation
     * The robot will be paired accordingly
     * Does displays as well
     *
     */
    @SuppressLint("DefaultLocale")
    public void trackRobot() {
        //System.out.println("TRACK ROBOT FUNCTION");

        int[] robotImageCoord = map.getCurCoord();
        int[] robotLocation = map.setRobotImagePosition(robotImageCoord[0], map.convertRow(robotImageCoord[1]), map.getLeft(), map.getTop());
        robot.setX(robotLocation[0]);
        robot.setY(robotLocation[1]);
        robot.setRotation(rotation);

        //Setting displays
        locationNotif = String.format("X: %d, Y: %d\n", robotImageCoord[0], robotImageCoord[1]);
        locationNotifView.setText(locationNotif);

        facingNotif = String.format("%s\n", map.convertRotationToFacing(rotation));
        facingNotifView.setText(facingNotif);
    }


    /**
     * Responding to instructions from external RPI
     */
    public void executeInstruction() {

        if (!Constants.instruction.equals("null")) {
            instruction = Constants.instruction;
        }
        String formattedInstruction = instruction.replaceAll("\\s", "");
        List<String> instructionList = Arrays.asList(formattedInstruction.split(","));

        System.out.println(formattedInstruction);
        System.out.println(instructionList.get(0));
        //CLEANING
        String prefix = instructionList.get(0);
        prefix = prefix.toUpperCase();

        //FOR STATUS
        if (prefix.equals("STATUS")) {
            // assuming max 1 comma
            String display = "STATUS: ";
            display = display + instructionList.get(1);
            outputNotifView.setText(display);
        } else if (prefix.equals("TARGET")) {
            // need to add check?
            int targetObst = Integer.parseInt(instructionList.get(1));
            String targetID = instructionList.get(2);
            TextView target = obstacleTextViews.get(targetObst - 1);
            target.setText(targetID);
            target.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);

        } else if (prefix.equals("ROBOT")) {
            //SET A MAX AND MIN!!! -- 8 feb
            int col = Integer.parseInt(instructionList.get(1));
            int row = Integer.parseInt(instructionList.get(2));

            if (col < 1) {
                col = Math.max(col, 1);
            } else {
                col = Math.min(col, map.getCol() - 2);
            }
            if (row < 1) {
                row = Math.max(row, 1);
            } else {
                row = Math.min(row, map.getCol() - 2);
            }
            String face = instructionList.get(3);
            robot.setVisibility(View.VISIBLE);

            map.setOldRobotCoord(map.getCurCoord()[0], map.getCurCoord()[1]); // create tracks
            int[] newCoord = new int[]{col, row};
            map.setCurCoord(newCoord);

            rotation = map.convertFacingToRotation(face);
            map.saveFacingWithRotation(rotation);
            trackRobot();
            map.invalidate();
        } else {
            System.out.println(instruction);
            String errorMsg = "Error: " + instruction;
            outputNotifView.setText(errorMsg);
            System.out.println("DOESNT WORK");
        }
    }


    /**
     * convert the constraint layout obstacle to an index
     * @param obstacle
     * @return
     */
    public int getObstacleNumber(ConstraintLayout obstacle) {
        for (int i = 0; i < obstacleViews.size(); i++) {
            if (obstacle == obstacleViews.get(i)) {
                return i + 1;
            }
        }
        return -1;
    }


    /**
     * HELPER FUNCTIONS TO CHECK
     */

    public void printAllObstacleCoords() {
        System.out.println("Obstacle Coords");
        for (int i = 0; i < currentObstacleCoords.length; i++) {
            System.out.printf("Obstacle %d |  X: %d, Y: %d\n", i + 1, currentObstacleCoords[i][0], currentObstacleCoords[i][1]);
        }
    }

    public void printOriginalObstacleCoords() {
        System.out.println("OG obstacle Coords");
        for (int i = 0; i < originalObstacleCoords.length; i++) {
            System.out.printf("Obstacle %d |  X: %d, Y: %d\n", i + 1, originalObstacleCoords[i][0], originalObstacleCoords[i][1]);
        }

    }

    public void printAllObstacleLeftTop() {
        System.out.println("Obstacle Left Top");
        for (int i = 0; i < obstacleViews.size(); i++) {
            //System.out.println(i+1);
            System.out.printf("Obstacle %d |  Left: %d, Top: %d\n", i + 1, obstacleViews.get(i).getLeft(), obstacleViews.get(i).getTop());
        }
    }

    public void reset(boolean print) {
        for (int i = 0; i < obstacleViews.size(); i++) {
            obstacleViews.get(i).setX(originalObstacleCoords[i][0]);
            obstacleViews.get(i).setY(originalObstacleCoords[i][1]);
        }
        // make the face side disappear.
        for (int i = 0; i < obstacleFaceViews.size(); i++) {
            //obstacleFaceViews.get(i).setRotation(0);
            obstacleFaceViews.get(i).setVisibility(View.INVISIBLE);
        }
        // reset list of current obstacles
        for (int i = 0; i < currentObstacleCoords.length; i++) {
            currentObstacleCoords[i][0] = 0;
            currentObstacleCoords[i][1] = 0;
        }
        for (int i = 0; i < obstacleTextViews.size(); i++) {
            obstacleTextViews.get(i).setTextSize(TypedValue.COMPLEX_UNIT_SP, 8);
        }
        if (print) {
            outputNotifView.setText("Obstacles Reset");
        }
        map.removeAllObstacles();


        //TO REMOVE THE ROBOT ALSO
        //map.setCanDrawRobot(false);
        //robot.setVisibility(View.INVISIBLE);
        //map.setOldRobotCoord(map.getCurCoord()[0],map.getCurCoord()[1]);
        //robot_popup.setVisibility(View.INVISIBLE);

        map.reset();   //remove all cells.
        map.invalidate();

    }


    public void setInstruction(String receivedInstruction) {
        this.instruction = receivedInstruction;
    }

    public class MyObserver implements Observer {
        private final MySubject subject;

        public MyObserver(MySubject subject) {
            this.subject = subject;
            subject.addObserver(this);
        }


        @Override
        public void update(Observable observable, Object arg) {
            if (observable == subject) {
                onInstructionChanged();
            }
        }

        private void onInstructionChanged() {
            // Do something when the constant variable changes
            executeInstruction();
        }
    }


    // ---------------------------- BLUETOOTH ----------------------------

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    public boolean onSupportNavigateUp() {
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        return NavigationUI.navigateUp(navController, appBarConfiguration)
                || super.onSupportNavigateUp();
    }

    //@Override
    //public void onClick(View view) {
    //}

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == 1 && grantResults.length > 0) {
            if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                showToast("Permission Granted");
            } else {
                showToast("Permission Denied");
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        switch (requestCode) {
            case REQUEST_ENABLE_BT:

                if (resultCode == RESULT_OK) {
                    // Bluetooth is on
                    //mBlueIv.setImageResource(R.drawable.ic_action_on);
                    showToast("Bluetooth is on");
                } else {
                    showToast("Failed to connect to bluetooth");
                }

                break;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    //Toast message function
    private void showToast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
    }

    //first fragment - turn on bluetooth
    public void turnonbluetooth() {
        if (!mBlueAdapter.isEnabled()) {
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                // TODO: Consider calling
                ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.BLUETOOTH_ADMIN}, 1);
                // here to request the missing permissions, and then overriding
                //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                //                                          int[] grantResults)
                // to handle the case where the user grants the permission. See the documentation
                // for ActivityCompat#requestPermissions for more details.
                Intent intent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                activityResultLauncher.launch(intent);
                //return;
            }
            mStatusBlueTv.setText("Bluetooth is on");

            // Intent to On Bluetooth
            //Intent intent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            //  startActivityForResult(intent, REQUEST_ENABLE_BT);

            //activityResultLauncher.launch(intent);
        } else {
            showToast("Bluetooth is already on");
        }
    }

    //first fragment - turn off bluetooth
    public void turnoffbluetooth() {
        if (mBlueAdapter.isEnabled()) {
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                // TODO: Consider calling
                //    ActivityCompat#requestPermissions
                // here to request the missing permissions, and then overriding
                //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                //                                          int[] grantResults)
                // to handle the case where the user grants the permission. See the documentation
                // for ActivityCompat#requestPermissions for more details.

                mBlueAdapter.disable();
                showToast("Turning Bluetooth Off");
                mStatusBlueTv.setText("Bluetooth is off");
                //mBlueIv.setImageResource(R.drawable.ic_action_off);
            }
        } else {
            showToast("Bluetooth is already off");
        }
    }

    //first fragment - set Bluetooth discoverable
    public void bluetooth_discoverable() {
        if (!mBlueAdapter.isEnabled()) {
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                // TODO: Consider calling
                ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.BLUETOOTH_ADMIN}, 1);
                // here to request the missing permissions, and then overriding
                //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                //                                          int[] grantResults)
                // to handle the case where the user grants the permission. See the documentation
                // for ActivityCompat#requestPermissions for more details.
                mStatusBlueTv.setText("Making Your Device Discoverable");
                Intent intent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
                //startActivityForResult(intent ,REQUEST_DISCOVER_BT);
                activityResultLauncher.launch(intent);
            }
        } else {
            mStatusBlueTv.setText("Bluetooth discovery is already on");
        }
    }

    ServiceConnection serviceConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            mBound = true;
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            mBound = false;
        }
    };

    BroadcastReceiver btConnectionReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {

            Log.d(TAG, "Receiving btConnectionStatus Msg!!!");

            String connectionStatus = intent.getStringExtra("ConnectionStatus");
            myBTConnectionDevice = intent.getParcelableExtra("Device");
            //myBTConnectionDevice = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
            //DISCONNECTED FROM BLUETOOTH CHAT
            if (connectionStatus.equals("disconnect")) {

                Log.d("MainActivity:", "Device Disconnected");
                connectedDevice = null;
                connectedState = false;

                if (currentActivity) {

                    //RECONNECT DIALOG MSG
                    AlertDialog alertDialog = new AlertDialog.Builder(MainActivity.this).create();
                    alertDialog.setTitle("BLUETOOTH DISCONNECTED");
                    alertDialog.setMessage("Connection with device: '" + myBTConnectionDevice.getName() + "' has ended. Do you want to reconnect?");


                    Handler handler = new Handler();
                    handler.postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            //START BT CONNECTION SERVICE
                            Intent connectIntent = new Intent(MainActivity.this, BluetoothConnectionService.class);
                            connectIntent.putExtra("serviceType", "connect");
                            connectIntent.putExtra("device", myBTConnectionDevice);
                            connectIntent.putExtra("id", myUUID);
                            startService(connectIntent);
                        }
                    }, 8000);

                    alertDialog.show();

                    handler.postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            //CLOSE DIALOG
                            alertDialog.cancel();
                        }
                    }, 1000);



                }

                //SUCCESSFULLY CONNECTED TO BLUETOOTH DEVICE
                else if (connectionStatus.equals("connect")) {

                    if (ActivityCompat.checkSelfPermission(MainActivity.this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                        // TODO: Consider calling
                        //    ActivityCompat#requestPermissions
                        // here to request the missing permissions, and then overriding
                        //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                        //                                          int[] grantResults)
                        // to handle the case where the user grants the permission. See the documentation
                        // for ActivityCompat#requestPermissions for more details.
                    }
                    connectedDevice = myBTConnectionDevice.getName();
                    connectedState = true;
                    Log.d("MainActivity:", "Device Connected " + connectedState);
                    Snackbar snackbar = Snackbar.make(getWindow().getDecorView(), "Connection Established: " + myBTConnectionDevice.getName(), Snackbar.LENGTH_SHORT);
                    snackbar.show();
                    //Toast.makeText(MainActivity.this, "Connection Established: " + myBTConnectionDevice.getName(), Toast.LENGTH_LONG).show();
                }

                //BLUETOOTH CONNECTION FAILED
                else if (connectionStatus.equals("connectionFail")) {
                    Toast.makeText(MainActivity.this, "Connection Failed: " + myBTConnectionDevice.getName(),
                            Toast.LENGTH_LONG).show();
                }
            }
        }
    };

    @Override
    protected void onPause() {
        super.onPause();
        //unregisterReceiver(btConnectionReceiver);
    }

    @Override
    protected void onStart() {
        super.onStart();
    }

    //RESUME ACTIVITY
    @Override
    protected void onResume() {
        super.onResume();

        //REGISTER BROADCAST RECEIVER FOR INCOMING MSG
        LocalBroadcastManager.getInstance(this).registerReceiver(btConnectionReceiver, new IntentFilter("btConnectionStatus"));

        //CHECK FOR EXISTING CONNECTION
        if (connectedState) {
            Log.d(" MainAcitvity:", "OnResume1");

            //SET TEXTFIELD TO DEVICE NAME
        } else {
            Log.d(" MainAcitvity:", "OnResume2");

            //SET TEXTFIELD TO NOT CONNECTED
        }

    }

    @Override
    protected void onStop() {
        super.onStop();
        if (mBound) {
            unbindService(serviceConnection);
            mBound = false;
        }
    }


}