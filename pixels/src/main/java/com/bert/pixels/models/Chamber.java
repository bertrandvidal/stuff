package com.bert.pixels.models;

import java.util.Iterator;
import java.util.List;

/**
 * Hold the currently visible pixels
 */
public final class Chamber {

  private final List<Pixel> pixels;

  private final Integer size;

  public Chamber(List<Pixel> pixels, Integer size) {
    this.pixels = pixels;
    this.size = size;
  }

  /**
   * Note that we should probably return an immutable list of pixels.
   *
   * @return the list of currently visible pixels.
   */
  public List<Pixel> pixels(){
    return this.pixels;
  }

  /**
   * @return true is no pixel is visible in the chamber, false otherwise
   */
  public boolean isEmpty() {
    return this.pixels.isEmpty();
  }

  /**
   * Move pixels in the chamber. Pixels that exit the chamber are removed.
   * @param speed the speed at which the pixels move in the chamber
   * @return the current chamber updated.
   */
  public Chamber movePixels(int speed) {
    final Iterator<Pixel> iterator = this.pixels.iterator();
    while (iterator.hasNext()) {
      final Pixel pixel = iterator.next();
      pixel.move(speed);
      final Integer position = pixel.getPosition();
      if (position < 0 || position >= this.size) {
        iterator.remove();
      }
    }
    return this;
  }

  public Integer getSize() {
    return this.size;
  }
}
