package com.bert.pixels.models;

import java.util.function.BinaryOperator;

/**
 * Possible colors for a pixel
 */
public enum Color {
  /**
   * Red pixels can only move right.
   */
  RED(Integer::sum),
  /**
   * Yellow pixels can only move left.
   */
  YELLOW((a, b) -> a - b);

  /**
   * The movement function to apply to a pixel's position
   */
  private final BinaryOperator<Integer> moveFunction;

  Color(BinaryOperator<Integer> moveFunction) {
    this.moveFunction = moveFunction;
  }

  /**
   * @return the "movement" to apply to a pixel's position to get its new position
   */
  public BinaryOperator<Integer> getMovement() {
    return this.moveFunction;
  }

  /**
   * @return the single character representation of the Color
   */
  public Character toChar() {
    return this.name().charAt(0);
  }
}
