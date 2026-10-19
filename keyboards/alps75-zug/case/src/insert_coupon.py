"""Practice piece for the heat-set inserts: five copies of the top frame's insert boss (print it with the case)."""
from cadgen import srgb, step

from lib.case_geom import make_insert_coupon


@step(out="../STEP/insert_coupon.step")
def insert_coupon():
    part = make_insert_coupon()
    part.color = srgb("#3A3F47")
    return part


if __name__ == "__main__":
    insert_coupon()
