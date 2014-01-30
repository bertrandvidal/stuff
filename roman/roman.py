d = {"I":1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

def compute(left, right):
  if left < right:
    return right - left
  else:
    return left + right

def convert(number):
  return map(lambda x: d[x], number)

def to_decimal(number):
  components = convert(number)
  total = 0
  while components:
    if len(components) == 1:
      total += components.pop()
    else:
      first, second = components[0:2:1]
      if first < second:
        total += second - first
        components = components[2:]
      else:
        total += first
        components = components[1:]
  return total


def rec_to_decimal(components, total=0):
  if not components:
    return total
  if len(components) == 1:
    return total + components.pop()
  else:
    first, second = components[0:2:1]
    if first < second:
      return rec_to_decimal(components[2:], total + (second - first))
    else:
      return rec_to_decimal(components[1:], total + first)

assert to_decimal("XLVIII") == 48
assert to_decimal("CCVII") == 207
assert to_decimal("MLXVI") == 1066
assert to_decimal("MCMLIV") == 1954
assert to_decimal("MCMXC") == 1990
assert to_decimal("MMXIV") == 2014

assert rec_to_decimal(convert("XLVIII")) == 48
assert rec_to_decimal(convert("CCVII")) == 207
assert rec_to_decimal(convert("MLXVI")) == 1066
assert rec_to_decimal(convert("MCMLIV")) == 1954
assert rec_to_decimal(convert("MCMXC")) == 1990
assert rec_to_decimal(convert("MMXIV")) == 2014

