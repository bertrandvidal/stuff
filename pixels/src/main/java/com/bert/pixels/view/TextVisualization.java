package com.bert.pixels.view;

import com.bert.pixels.models.Chamber;
import com.bert.pixels.models.Color;
import com.bert.pixels.models.Pixel;

import java.util.ArrayList;
import java.util.List;

/**
 * Textual representation of pixels going through a chamber
 */
public class TextVisualization {

  private final int maxSize;
  private int size;

  public TextVisualization(int maxSize) {
    this.maxSize = maxSize;
  }

  /**
   * Initialized a chamber from an input.
   *
   * @param input the input string representing the initial state of the chamber.
   * @return a fully initialized chamber.
   */
  public Chamber from(String input) {
    this.size = input.length();
    if (this.size > this.maxSize) {
      throw new IllegalArgumentException(String.format("Input exceeds max size of '%d'", this.maxSize));
    }

    List<Pixel> pixels = new ArrayList<>(this.size);
    for (int i = 0; i < input.length(); i++) {
      final char character = input.charAt(i);
      try {
        pixels.add(new Pixel(Color.valueOf(String.valueOf(character).toUpperCase()), i));
      } catch (IllegalArgumentException e) {
        if (character != '.') {
          throw new IllegalArgumentException(String.format("'%c' not supported", character));
        }
      }
    }

    return new Chamber(pixels, this.size);
  }

  public String to(Chamber chamber) {
    return null;
  }

  /**
   * @return size of the input/output handled by this instance
   */
  public int size() {
    return this.size;
  }
}
