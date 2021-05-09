package com.bert.pixels.models;

import java.util.List;

/**
 * Hold the currently visible pixels
 */
public class Chamber {
  private List<Pixel> pixels;

  /**
   * Note that we should probably return an immutable list of pixels.
   *
   * @return the list of currently visible pixels.
   */
  public List<Pixel> pixels(){
    return this.pixels;
  }
}
