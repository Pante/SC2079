package com.example.mdpandroidcontroller;

public class Constants {

    private static MySubject subject = null;

    public Constants(MySubject subject) {
        this.subject = subject;
    }

    public static final String APP_NAME = "GRP3";

    public static final String BLUETOOTH_ON = "BLUETOOTH ON";
    public static final String BLUETOOTH_OFF = "BLUETOOTH OFF";
    public static final String SECTION_NUMBER = "section_number";
    public static final Integer ONE_THOUSAND = 1000;
    public static final Integer SIXTY = 60;
    public static final Integer FIVE_HUNDRED = 500;
    public static final Integer ZERO = 0;
    public static final Integer FIVE = 5;
    public static final Integer FIFTEEN = 15;
    public static final Integer TWENTY = 20;
    public static final Integer TWENTY_ONE = 21;
    public static final String NOT_AVAILABLE = "NOT AVAILABlE";
    public static final String MDF_ALL_F_STRING = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff";
    public static final String NONE = "None";
    public static final String UP = "Up";
    public static final String DOWN = "Down";
    public static final String LEFT = "Left";
    public static final String RIGHT = "Right";
    public static final String NORTH = "N";
    public static final String SOUTH = "S";
    public static final String EAST = "E";
    public static final String WEST = "W";
    public static final String ERROR = "Error!!!";

    public static boolean connected = false;
    public static String instruction = "null";

    public static void setConnected (Boolean connection) {
        connected = connection;
        if (connected) {
            System.out.println("ITS CONNECTED");
        } else {
            System.out.println("not connected");
        }
    }

    public static void setInstruction (String received) {
        instruction = received;
        System.out.println("AT CONSTANT");
        System.out.println(instruction);
        subject.changeInstruction();

    }


}
