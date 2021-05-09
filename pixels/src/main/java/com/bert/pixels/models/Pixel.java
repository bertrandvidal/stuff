package com.bert.pixels.models;

/**
 * A pixel is capable of moving within a "chamber", it is defined by its color and current position.
 */
public final class Pixel {

  private final Color color;
  private Integer position;

  public Pixel(Color color, Integer position) {
    this.color = color;
    this.position = position;
  }

  /**
   * @return the color of the pixel
   */
  public Color getColor() {
    return this.color;
  }

  /**
   * @return the current position of the pixel
   */
  public Integer getPosition() {
    return this.position;
  }

  public void move(int speed) {
    this.position = this.color.apply(this, speed);
  }
}
