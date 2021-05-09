package com.bert.pixels.models;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ColorTest {

  @Test
  void testGetMovementRedColor() {
    assertEquals(Color.R.getMovement().apply(0, 1), 1);
  }

  @Test
  void testGetMovementYellowColor() {
    assertEquals(Color.Y.getMovement().apply(0, 1), -1);
  }

  @Test
  void testToChar() {
    assertEquals(Color.R.toChar(), 'R');
    assertEquals(Color.Y.toChar(), 'Y');
  }
}
