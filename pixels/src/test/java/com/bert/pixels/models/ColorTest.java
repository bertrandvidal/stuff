package com.bert.pixels.models;

import org.junit.jupiter.api.Test;

import java.util.Collections;

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

  @Test
  void testPixelAt() {
    assertEquals(Color.RED.pixelAt(0), Collections.singleton(new Pixel(Color.RED, 0)));
    assertEquals(Color.YELLOW.pixelAt(0), Collections.singleton(new Pixel(Color.YELLOW, 0)));
  }
}
