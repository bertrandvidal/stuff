package com.bert.pixels.models;

import java.util.Collection;
import java.util.Collections;
import java.util.function.BinaryOperator;
import java.util.stream.Collectors;
import java.util.stream.Stream;

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
  YELLOW((a, b) -> a - b),
  /**
   * Orange is the combination of a RED and YELLOW pixels. It does not have a move function has an ORANGE pixel does
   * not "naturally" occurs and can only be born of the combination of RED and YELLOW and is represented as such.
   */
  ORANGE(null) {
    @Override
    public Collection<Pixel> pixelAt(int position) {
      return Stream.of(new Pixel(RED, position), new Pixel(YELLOW, position)).collect(Collectors.toList());
    }
  };

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

  /**
   * Pixel(s) that should be created when reading chamber from input.
   * @param position the position in the chamber at which the input that resolve to this color was fond
   * @return Pixel(s) at the given position with the appropriate color
   */
  public Collection<Pixel> pixelAt(int position) {
    return Collections.singleton(new Pixel(this, position));
  }
}
