package com.bert.pixels.view;

import com.bert.pixels.models.Chamber;
import com.bert.pixels.models.Color;
import com.bert.pixels.models.Pixel;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Textual representation of pixels going through a chamber
 */
public class TextVisualization {

  private final int maxSize;
  private int size;
  private static final Map<Character, Color> TEXT_TO_COLOR = setupTextToColor();


  /**
   * @param maxSize the maximum size this textual visualization can support
   */
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
      Color color = TEXT_TO_COLOR.get(Character.toUpperCase(character));
      // TODO(bvidal): The "blank" character could be made a constant and/or passed in the constructor
      if (character == 'O' || character == 'o') {
        pixels.add(new Pixel(Color.RED, i));
        pixels.add(new Pixel(Color.YELLOW, i));
      } else if (color == null && character != '.') {
        throw new IllegalArgumentException(String.format("'%c' not supported", character));
      } else if (color != null) {
        pixels.add(new Pixel(color, i));
      }
    }

    return new Chamber(pixels, this.size);
  }

  /**
   * Return the textual representation of the given chamber
   * @param chamber the chamber to visualize
   * @return a textual representation of the given chamber
   */
  public String to(Chamber chamber) {
    final char[] output = String.join("", Collections.nCopies(chamber.getSize(), ".")).toCharArray();
    for (Pixel pixel : chamber.pixels()) {
      final Integer position = pixel.getPosition();
      if (output[position] != '.') {
        // TODO(bvidal): The "overlap" color could be obtain by "mixing" Color rather than being harcoded
        output[position] = 'O';
      } else {
        output[position] = pixel.getColor().toChar();
      }
    }
    return new String(output);
  }

  /**
   * @return size of the input/output handled by this instance
   */
  public int size() {
    return this.size;
  }

  private static Map<Character, Color> setupTextToColor() {
    return Collections.unmodifiableMap(Arrays.stream(Color.values())
                                             .collect(Collectors.toMap(Color::toChar, Function.identity())));
  }
}
