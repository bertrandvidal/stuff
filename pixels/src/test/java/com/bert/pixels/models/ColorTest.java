package com.bert.pixels.models;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ColorTest {
  @Test
  void testRedApply() {
    final Pixel pixel = new Pixel(null, 0);
    assertEquals(Color.R.apply(pixel, 1), 1);
  }

  @Test
  void testYellowApply() {
    final Pixel pixel = new Pixel(null, 0);
    assertEquals(Color.Y.apply(pixel, 1), -1);
  }
}
