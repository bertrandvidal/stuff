package com.bert.pixels.models;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ChamberTest {

  @Test
  void testIsEmptyNoPixel() {
    assertTrue(new Chamber(new ArrayList<>(), -1).isEmpty());
  }

  @Test
  void testIsEmptyWithPixel() {
    final ArrayList<Pixel> pixels = new ArrayList<>();
    pixels.add(new Pixel(Color.R, 1));
    assertFalse(new Chamber(pixels, -1).isEmpty());
  }

  @Test
  void testMovePixels() {
    final ArrayList<Pixel> pixels = new ArrayList<>();
    pixels.add(new Pixel(Color.R, 0));
    pixels.add(new Pixel(Color.Y, 1));
    final Chamber chamber = new Chamber(pixels, 2);
    chamber.movePixels(1);
    assertFalse(chamber.isEmpty());
    assertEquals(chamber.pixels().size(), 2);
    for (Pixel pixel : chamber.pixels()) {
      if (Color.R.equals(pixel.getColor())) {
        assertEquals(pixel.getPosition(), 1);
      } else {
        assertEquals(pixel.getPosition(), 0);
      }
    }
  }

  @Test
  void testMovePixelsOutOfBoundAreRemoved() {
    final ArrayList<Pixel> pixels = new ArrayList<>();
    pixels.add(new Pixel(Color.R, 1));
    pixels.add(new Pixel(Color.Y, 0));
    final Chamber chamber = new Chamber(pixels, 2);
    chamber.movePixels(1);
    assertTrue(chamber.isEmpty());
  }
}
