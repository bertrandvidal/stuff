package com.bert.pixels.models;

import org.junit.jupiter.api.Test;

import java.util.Collections;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
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
    assertEquals(new Pixel(Color.RED, -1).getPosition(), -1);
    assertEquals(new Pixel(Color.RED, 0).getPosition(), 0);
    assertEquals(new Pixel(Color.RED, 1).getPosition(), 1);
    assertNull(new Pixel(Color.RED, null).getPosition());
  }

  @Test
  void testMove() {
    Pixel pixel = new Pixel(Color.RED, 0);
    pixel.move(0);
    assertEquals(pixel.getPosition(), 0);
    pixel.move(1);
    assertEquals(pixel.getPosition(), 1);
    pixel.move(-2);
    assertEquals(pixel.getPosition(), -1);
  }

  @Test
  void testEqualsAndHashCode() {
    Pixel redPixel = new Pixel(Color.RED, 0);
    assertEquals(redPixel, redPixel);
    assertEquals(redPixel, new Pixel(Color.RED, 0));
    assertNotEquals(redPixel, new Pixel(Color.RED, 1));
    assertNotEquals(redPixel, new Pixel(Color.YELLOW, 0));
    assertEquals(Collections.singleton(redPixel), Collections.singleton(redPixel));
    assertEquals(Collections.singleton(redPixel), Collections.singleton(new Pixel(Color.RED, 0)));
    assertNotEquals(Collections.singleton(redPixel), Collections.singleton(new Pixel(Color.RED, 1)));
    assertNotEquals(Collections.singleton(redPixel), Collections.singleton(new Pixel(Color.YELLOW, 0)));
  }
}
