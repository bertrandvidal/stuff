"""
Problem: Compress a string such that 'AAABCCDDDD' becomes 'A3B1C2D4'. Only compress the string if it saves space.
"""


def str_compress(s):
    if not s:
        return s
    if len(s) <= 2 * len(set(s)):
        # No need to compress as there are not enough letters
        return s
    char, cpt = s[0], 1
    result = ""
    for current_char in s[1:]:
        if current_char == char:
            cpt += 1
        else:
            result += char + str(cpt)
            cpt = 1
            char = current_char
    return result + char + str(cpt)


assert str_compress(None) == None
assert str_compress("") == ""
assert str_compress("AABBCC") == "AABBCC"
assert str_compress("AABCCDDDD") == "A2B1C2D4"
assert str_compress("AAA") == "A3"

# BONUS
def str_decompress(s):
    result = ""
    for _ in range(len(s)//2):
        a, b, *s = s
        result += a * int(b)
    return result

assert str_decompress("A4") == "AAAA"
assert str_decompress("A2B1C2D4") == "AABCCDDDD"
