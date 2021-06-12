package com.bert.pixels.models;

import java.util.Objects;

/**
 * A pixel is capable of moving within a "chamber", it is defined by its color and current position.
 */
public final class Pixel {

  private final Color color;
  private Integer position;

  /**
   * @param color color of the pixel
   * @param position original position of the pixel
   */
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

  /**
   * @param speed how many unit of space the pixel should be moved
   */
  public void move(int speed) {
    this.position = this.color.getMovement().apply(this.position, speed);
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
        return true;
    }
    if (o == null || this.getClass() != o.getClass()) {
        return false;
    }

    final Pixel pixel = (Pixel) o;

    if (!Objects.equals(this.position, pixel.position)) {
        return false;
    }
    return Objects.equals(this.color, pixel.color);
  }

  @Override
  public int hashCode() {
    int result = this.position != null ? this.position.hashCode() : 0;
    result = 31 * result + (this.color != null ? this.color.hashCode() : 0);
    return result;
  }
}
