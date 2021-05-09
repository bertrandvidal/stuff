package com.bert.pixels.models;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

class PixelTest {

  @Test
  void testGetColor() {
    for (Color color : Color.values()) {
      assertEquals(new Pixel(color, 1).getColor(), color);
    }
  }

  @Test
  void testGetPosition() {
    assertEquals(new Pixel(Color.R, -1).getPosition(), -1);
    assertEquals(new Pixel(Color.R, 0).getPosition(), 0);
    assertEquals(new Pixel(Color.R, 1).getPosition(), 1);
    assertNull(new Pixel(Color.R, null).getPosition());
  }

  @Test
  void testMove() {
    Pixel pixel = new Pixel(Color.R, 0);
    pixel.move(0);
    assertEquals(pixel.getPosition(), 0);
    pixel.move(1);
    assertEquals(pixel.getPosition(), 1);
    pixel.move(-2);
    assertEquals(pixel.getPosition(), -1);
  }
}
