package com.example.mdp_group_14;

import java.util.*;
import java.util.AbstractMap.*;
import java.util.function.BiFunction;

import java.util.ArrayList;
import java.util.function.BiFunction;

public class Turn {

    public static Map.Entry<String, ArrayList<Integer[]>> turn(Integer[] start, String direction, String turn) {
        int radius = radius(turn);
        Integer[] initial;
        switch (direction) {
            case "up":
                switch (turn) {
                    case "left":
                        return new SimpleEntry<>(
                          "left",
                          curve(
                            start,
                            new Integer[] {start[0] - radius - 1, start[1] + radius},
                            radius,
                            start[0] - radius,
                            start[1],
                            1
                          )
                        );
                    case "right":
                        return new SimpleEntry<>(
                          "right",
                          curve(
                            start,
                            new Integer[] {start[0] + radius, start[1] + radius - 1},
                            radius,
                            start[0] + radius,
                            start[1],
                            2
                          )
                        );
                    case "backleft":
                        return new SimpleEntry<>(
                          "right",
                          curve(
                            start,
                            new Integer[] {start[0] - radius, start[1] - radius - 1},
                            radius,
                            start[0] - radius,
                            start[1],
                            4
                          )
                        );
                    case "backright":
                        return new SimpleEntry<>(
                          "left",
                          curve(
                            start,
                            new Integer[] {start[0] + radius - 1, start[1] - radius},
                            radius,
                            start[0] + radius,
                            start[1],
                            3
                          )
                        );
                }

            case "right":
                initial = new Integer[] {start[0], start[1] + 1};
                switch (turn) {
                    case "left":
                        return new SimpleEntry<>(
                          "up",
                          curve(
                            initial,
                            new Integer[] {initial[0] + radius, initial[1] + radius},
                            radius,
                            initial[0],
                            initial[1] + radius,
                            4
                          )
                        );

                    case "right":
                        return new SimpleEntry<>(
                          "down",
                          curve(
                            initial,
                            new Integer[] {initial[0] + radius - 1, initial[1] - radius - 1},
                            radius,
                            initial[0],
                            initial[1] - radius,
                            1
                          )
                        );
                    case "backleft":
                        return new SimpleEntry<>(
                          "down",
                          curve(
                            initial,
                            new Integer[] {initial[0] - radius - 1, initial[1] + radius - 1},
                            radius,
                            initial[0],
                            initial[1] + radius,
                            3
                          )
                        );
                    case "backright":
                        return new SimpleEntry<>(
                          "up",
                          curve(
                            initial,
                            new Integer[] {initial[0] - radius, initial[1] - radius},
                            radius,
                            initial[0],
                            initial[1] - radius,
                            2
                          )
                        );
                }

            case "down":
                initial = new Integer[] {start[0] + 1, start[1] + 1};
                switch (turn) {
                    case "left":
                        return new SimpleEntry<>(
                          "right",
                          curve(
                            initial,
                            new Integer[] {initial[0] + radius, initial[1] - radius - 1},
                            radius,
                            initial[0] + radius,
                            initial[1],
                            3
                          )
                        );
                    case "right":
                        return new SimpleEntry<>(
                          "left",
                          curve(
                            initial,
                            new Integer[] {initial[0] - radius - 1, initial[1] - radius},
                            radius,
                            initial[0] - radius,
                            initial[1],
                            4
                          )
                        );
                    case "backleft":
                        return new SimpleEntry<>(
                          "left",
                          curve(
                            initial,
                            new Integer[] {initial[0] + radius - 1, initial[1] + radius},
                            radius,
                            initial[0] + radius,
                            initial[1],
                            2
                          )
                        );
                    case "backright":
                        return new SimpleEntry<>(
                          "right",
                          curve(
                            initial,
                            new Integer[] {initial[0] - radius, initial[1] + radius - 1},
                            radius,
                            initial[0] - radius,
                            initial[1],
                            1
                          )
                        );
                }

            case "left":
                initial = new Integer[] {start[0] + 1, start[1]};
                switch (turn) {
                    case "left":
                        return new SimpleEntry<>(
                          "down",
                          curve(
                            initial,
                            new Integer[] {initial[0] - radius - 1, initial[1] - radius - 1},
                            radius,
                            initial[0] - radius,
                            initial[1],
                            2
                          )
                        );

                    case "right":
                        return new SimpleEntry<>(
                          "up",
                          curve(
                            initial,
                            new Integer[] {initial[0] - radius, initial[1] + radius},
                            radius,
                            initial[0],
                            initial[1] + radius,
                            3
                          )
                        );

                    case "backleft":
                        return new SimpleEntry<>(
                          "up",
                          curve(
                            initial,
                            new Integer[] {initial[0] + radius, initial[1] - radius},
                            radius,
                            initial[0],
                            initial[1] - radius,
                            1
                          )
                        );

                    case "backright":
                        return new SimpleEntry<>(
                          "down",
                          curve(
                            initial,
                            new Integer[] {initial[0] + radius - 1, initial[1] + radius - 1},
                            radius,
                            initial[0],
                            initial[1] + radius,
                            4
                          )
                        );
                }
        }

        throw new IllegalStateException("Invalid robot direction: " + direction + " & turn direction: " + turn);
    }

    static int radius(String direction) {
        return 3;
    }

    static ArrayList<Integer[]> curve(Integer[] initial, Integer[] destination, int radius, int centreX, int centreY, int quadrant) {
        int x = radius;
        int y = 0;
        int err = 0;

        ArrayList<Integer[]> a = new ArrayList<>();
        ArrayList<Integer[]> b = new ArrayList<>();
        BiFunction<Integer, Integer, Integer[]> aMap = null;
        BiFunction<Integer, Integer, Integer[]> bMap = null;

        switch (quadrant) {
            case 1:
                aMap = (_x, _y) -> new Integer[]{centreX + _x, centreY + _y};
                bMap = (_x, _y) -> new Integer[]{centreX + _y, centreY + _x};
                break;
            case 2:
                aMap = (_x, _y) -> new Integer[]{centreX - _y, centreY + _x};
                bMap = (_x, _y) -> new Integer[]{centreX - _x, centreY + _y};
                break;
            case 3:
                aMap = (_x, _y) -> new Integer[]{centreX - _x, centreY - _y};
                bMap = (_x, _y) -> new Integer[]{centreX - _y, centreY - _x};
                break;
            case 4:
                aMap = (_x, _y) -> new Integer[]{centreX + _y, centreY - _x};
                bMap = (_x, _y) -> new Integer[]{centreX + _x, centreY - _y};
                break;
        }

        while (x >= y) {
            a.add(aMap.apply(x, y));
            b.add(bMap.apply(x, y));

            y += 1;
            err += 1 + 2 * y;
            if (2 * (err - x) + 1 > 0) {
                x -= 1;
                err += 1 - 2 * x;
            }
        }

        ArrayList<Integer[]> firstPart;
        ArrayList<Integer[]> secondPart;
        if (manhattanDistance(initial, a.get(0)) < manhattanDistance(initial, b.get(0))) {
            firstPart = a;
            secondPart = b;
        } else {
            firstPart = b;
            secondPart = a;
        }
        
        Collections.reverse(secondPart);
        if (!Arrays.equals(secondPart.get(secondPart.size() - 1), destination)) {
            secondPart.add(destination);
        }

        firstPart.addAll(secondPart);
        return firstPart;
    }

    static int manhattanDistance(Integer[] a, Integer[] b) {
        return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
    }
}