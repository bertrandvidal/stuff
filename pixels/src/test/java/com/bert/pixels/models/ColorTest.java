package com.bert.pixels.models;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ColorTest {

  @Test
  void testGetMovementRedColor() {
    assertEquals(Color.RED.getMovement().apply(0, 1), 1);
  }

  @Test
  void testGetMovementYellowColor() {
    assertEquals(Color.YELLOW.getMovement().apply(0, 1), -1);
  }

  @Test
  void testToChar() {
    assertEquals(Color.RED.toChar(), 'R');
    assertEquals(Color.YELLOW.toChar(), 'Y');
  }
}
