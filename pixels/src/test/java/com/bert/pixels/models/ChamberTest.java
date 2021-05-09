package com.bert.pixels.models;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ChamberTest {

  @Test
  void testIsEmptyNoPixel() {
    assertTrue(new Chamber(new ArrayList<>()).isEmpty());
  }

  @Test
  void testIsEmptyWithPixel() {
    final ArrayList<Pixel> pixels = new ArrayList<>();
    pixels.add(new Pixel(Color.R, 1));
    assertFalse(new Chamber(pixels).isEmpty());
  }
}
