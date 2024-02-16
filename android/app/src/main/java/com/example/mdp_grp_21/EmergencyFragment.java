package com.example.mdp_grp_21;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.DialogFragment;
import androidx.fragment.app.Fragment;

import java.util.UUID;
import java.util.zip.Inflater;

// NOTE: THIS HAS BEEN REMOVED - NOT IN USE IN FINAL APP
// This was made for redundancy - in case an obstacle can't be placed properly, this is a slightly faster way to get the right syntax to manually send to RPi
public class EmergencyFragment extends DialogFragment {
    private static final String TAG = "EmergencyFragment";
    View rootView;
    private SharedPreferences.Editor editor;
    Button addManualBtn, cancelBtn;
    Switch isObstSwitch;
    boolean isObstacle = true;

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, Bundle savedInstanceState) {
        showLog("Entering onCreateView");
        rootView = inflater.inflate(R.layout.activity_manual_input, container, false);
        super.onCreate(savedInstanceState);

        SharedPreferences sharedPreferences = getActivity().getSharedPreferences("Shared Preferences", Context.MODE_PRIVATE);
        editor = sharedPreferences.edit();

        // buttons
        addManualBtn = rootView.findViewById(R.id.addManualBtn);
        cancelBtn = rootView.findViewById(R.id.cancelManualBtn);

        // switch
        isObstSwitch = rootView.findViewById(R.id.isObstSwitch);

        // selecting 0 - 19 for x, y
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(
                rootView.getContext(), R.array.obstID_array,
                android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        final Spinner xValSpinner = rootView.findViewById(R.id.xDropdownSpinner);
        final Spinner yValSpinner = rootView.findViewById(R.id.yDropdownSpinner);
        xValSpinner.setAdapter(adapter);
        yValSpinner.setAdapter(adapter);

        // Selecting "North", "South", "East", "West" for dir of obstacle
        ArrayAdapter<CharSequence> dirAdapter = ArrayAdapter.createFromResource(
                rootView.getContext(), R.array.obstDir_array,
                android.R.layout.simple_spinner_item);
        dirAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        final Spinner dirValSpinner = rootView.findViewById(R.id.directionDropdownSpinner);
        dirValSpinner.setAdapter(dirAdapter);

        // Initialise selection for all spinners to the 1st element in the given array
        xValSpinner.setSelection(0); yValSpinner.setSelection(0); dirValSpinner.setSelection(0);

        isObstSwitch.setOnCheckedChangeListener( new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton toggleButton, boolean isChecked) {
                showToast("isObstacle: " + (isChecked ? "ON" : "OFF"));
                isObstacle = isChecked;
            }
        });

        addManualBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked addManualBtn");
                EditText chatInput = BluetoothCommunications.getTypeBoxEditText();
                String old = chatInput.getText().toString();
                if(old.equals("")) old = "ALG";

                int col = Integer.parseInt(xValSpinner.getSelectedItem().toString());
                int row = Integer.parseInt(yValSpinner.getSelectedItem().toString());
                showLog("Col = " + col  + ", Row = " + row);
                // obstDir
                String dir = dirValSpinner.getSelectedItem().toString();
                int obstDir;
                switch(dir) {
                    case "North":
                        obstDir = 90;
                        break;
                    case "South":
                        obstDir = -90;
                        break;
                    case "East":
                        obstDir = 0;
                        break;
                    case "West":
                        obstDir = 180;
                        break;
                    default:
                        showLog("Setting default direction: North");
                        obstDir = 90;
                }
                showLog("Dir = " + dir + "; algDir = " + obstDir);

                // obstID is acquired based on the obstID set for the PREVIOUS obstacle (prev obst MUST be added in this way)
                int obstID = 0;
                if(!old.equals("ALG")) {
                    obstID = Integer.parseInt(old.substring(old.lastIndexOf(",") + 1)) + 1;
                }
                if(!isObstacle) obstID = -1;

                String obstString = "|" + (col * 10 + 5) + "," + (row * 10 + 5) + "," + obstDir + "," + obstID;
                String newString = old + obstString;
                chatInput.setText(newString);
//                getDialog().dismiss();
                showToast("Obstacle string added!");
                showLog("Exiting addManualBtn");
            }
        });

        cancelBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked cancelDirectionBtn");
                showLog("Exiting cancelDirectionBtn");
                getDialog().dismiss();
            }
        });

        return rootView;
    }

    @Override
    public void onSaveInstanceState(@NonNull Bundle outState) {
        showLog("Entering onSaveInstanceState");
        super.onSaveInstanceState(outState);
        showLog("Exiting onSaveInstanceState");
    }

    @Override
    public void onDismiss(@NonNull DialogInterface dialog) {
        showLog("Entering onDismiss");
        super.onDismiss(dialog);
        showLog("Exiting onDismiss");
    }

    private void showLog(String message) {
        Log.d(TAG, message);
    }

    private void showToast(String message) { Toast.makeText(getActivity(), message, Toast.LENGTH_SHORT).show(); }
}
