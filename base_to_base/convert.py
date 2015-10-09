import string


known_digits = string.digits + string.ascii_uppercase


def to_decimal(number, base):
    return sum(known_digits.index(digit) * base ** idx
               for idx, digit in enumerate(number[::-1]))


assert to_decimal("10", 10) == 10
assert to_decimal("10", 2) == 2
assert to_decimal("FF", 16) == 255
assert to_decimal("A1", 16) == 161


def from_decimal(number, base):
    result = []
    while number:
        result.append(known_digits[number % base])
        number = number / base
    return "".join(result[::-1])


assert from_decimal(10, 16) == "A"
assert from_decimal(15, 16) == "F"
assert from_decimal(19, 16) == "13"
assert from_decimal(10, 2) == "1010"


def convert(number, base, new_base):
    return from_decimal(to_decimal(number, base), new_base)


assert convert("1010", 2, 16) == "A"
assert convert("1010", 10, 16) == "3F2"
assert convert("1010", 2, 10) == "10"
assert convert("1010", 16, 16) == "1010"
assert convert("1010", 16, 2) == "1000000010000"
assert convert("1010", 16, 10) == "4112"
