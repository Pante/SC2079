package com.example.mdp_group_14;

public class Straight {

  public static Integer[] straight(Integer[] start, String direction, String movement) {
    switch (direction) {
      case "up":
        switch (movement) {
          case "forward":
            return new Integer[] {start[0], start[1] + 1};
          case "back":
            return new Integer[] {start[0], start[1] - 1};
        }
      case "right":
        switch (movement) {
          case "forward":
            return new Integer[] {start[0] + 1, start[1]};
          case "back":
            return new Integer[] {start[0] - 1, start[1]};
        }
      case "down":
        switch (movement) {
          case "forward":
            return new Integer[] {start[0], start[1] - 1};
          case "back":
            return new Integer[] {start[0], start[1] + 1};
        }
      case "left":
        switch (movement) {
          case "forward":
            return new Integer[] {start[0] - 1, start[1]};
          case "back":
            return new Integer[] {start[0] + 1, start[1]};
        }
    }

    throw new IllegalStateException("This should never happen");
  }

}
