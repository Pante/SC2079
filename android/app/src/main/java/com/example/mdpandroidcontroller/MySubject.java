package com.example.mdpandroidcontroller;

import java.util.Observable;

public class MySubject extends Observable {
    public void changeInstruction() {
        setChanged();
        notifyObservers();
    }
}