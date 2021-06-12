package com.bert.pixels.models;

import org.junit.jupiter.api.Test;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

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
    Set<Pixel> pixels = new HashSet<>();
    pixels.add(new Pixel(Color.RED, 0));
    pixels.add(new Pixel(Color.YELLOW, 0));
    assertTrue(Color.ORANGE.pixelAt(0).containsAll(pixels));
  }
}
