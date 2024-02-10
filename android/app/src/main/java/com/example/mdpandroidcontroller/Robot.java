package com.example.mdpandroidcontroller;

import android.content.Context;
import android.util.AttributeSet;
import android.view.View;

import androidx.annotation.Nullable;

public class Robot extends View {

    private Context context;
    private AttributeSet attrs;

    public Robot(Context c) {
        super(c);
        // init map???
    }

    public Robot(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        this.context = context;
        this.attrs = attrs;
    }







}
