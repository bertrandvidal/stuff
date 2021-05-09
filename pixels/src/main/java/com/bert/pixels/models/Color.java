package com.bert.pixels.models;

import java.util.function.BinaryOperator;

/**
 * Possible colors for a pixel
 */
public enum Color {
  /**
   * Red pixels can only more right.
   */
  R(Integer::sum),
  /**
   * Yellow pixels can only more left.
   */
  Y((a, b) -> a - b);

  private final BinaryOperator<Integer> moveFunction;

  Color(BinaryOperator<Integer> moveFunction) {
    this.moveFunction = moveFunction;
  }

  public Integer apply(Pixel pixel, int speed) {
    return this.moveFunction.apply(pixel.getPosition(), speed);
  }
}
