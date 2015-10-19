"""
Implement string reverse without using the slice operator or the reverse method.
It should be implemented in place
"""

def reverse_in_place(s):
    if not s:
        return s
    for idx in range(len(s)/2):
        s[idx], s[len(s) - idx - 1] = s[len(s) - idx - 1], s[idx]
    return s


assert reverse_in_place(None) == None
assert reverse_in_place("") == ""
assert reverse_in_place("f o o d b a r".split()) == "r a b d o o f".split()
