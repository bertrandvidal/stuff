package com.bert.pixels.models;

import java.util.List;

/**
 * Hold the currently visible pixels
 */
public final class Chamber {

  private List<Pixel> pixels;

  public Chamber(List<Pixel> pixels) {
    this.pixels = pixels;
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
}
