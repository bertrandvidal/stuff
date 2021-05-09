package com.bert.pixels.view;

import com.bert.pixels.models.Chamber;
import com.bert.pixels.models.Color;
import com.bert.pixels.models.Pixel;
import org.junit.jupiter.api.Test;

import java.util.Random;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class TextVisualizationTest {
  @Test
  void testMaxSizeValidation() {
    assertThrows(IllegalArgumentException.class, () -> new TextVisualization(0).from("."));
  }

  @Test
  void testSize() {
    final int i = new Random().nextInt(100);
    final TextVisualization visualization = new TextVisualization(i);
    visualization.from(IntStream.range(0, i).mapToObj(x -> ".").collect(Collectors.joining("")));
    assertEquals(visualization.size(), i);
  }

  @Test
  void testFromWithUnsupportedCharacters() {
    assertThrows(IllegalArgumentException.class, () -> new TextVisualization(1).from("A"));
  }

  @Test
  void testFromEmptyChamber() {
    final Chamber chamber = new TextVisualization(1).from(".");
    assertTrue(chamber.isEmpty());
  }

  @Test
  void testFromCaseInsensitive() {
    final Chamber chamber = new TextVisualization(2).from("RY");
    assertFalse(chamber.isEmpty());
    assertEquals(chamber.pixels().size(), 2);
    for (Pixel pixel : chamber.pixels()) {
      if (pixel.getColor() == Color.R) {
        assertEquals(pixel.getPosition(), 0);
      } else {
        assertEquals(pixel.getPosition(), 1);
      }
    }
  }
}
