package com.bert.pixels;

import com.bert.pixels.models.Chamber;
import com.bert.pixels.view.TextVisualization;

import java.util.ArrayList;
import java.util.List;

/**
 * Entry point to solve the pixel exercise
 */
public class Animation {

  private final static int MAX_SIZE = 10;

  public static void main(String[] args) {
    final int speed = Integer.parseInt(args[1]);
    TextVisualization visualization = new TextVisualization(MAX_SIZE);
    final Chamber chamber = visualization.from(args[0]);
    // We could set the size of the list by using the size of the chamber and the value of speed
    // but ... #prematureoptimization
    List<String> iterations = new ArrayList<>();
    iterations.add(visualization.to(chamber));
    while (!chamber.isEmpty()) {
      iterations.add(visualization.to(chamber.movePixels(speed)));
    }
    System.out.println(String.join("\n", iterations));
  }
}
