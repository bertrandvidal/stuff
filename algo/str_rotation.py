"""
Problem: Determine if a string s1 is a rotation of another string s2, by calling (only once) a function is_substring
"""


def is_substring(str1, str2):
    return str1 in str2


def is_rotation(str1, str2):
    if str1 is None or str2 is None:
        return False
    if len(str1) != len(str2):
        return False
    return is_substring(str2, str1 + str1)


assert is_rotation('o', 'oo') == False
assert is_rotation(None, 'foo') == False
assert is_rotation('', 'foo') == False
assert is_rotation('', '') == True
assert is_rotation('foobarbaz', 'barbazfoo') == True
assert is_rotation('oobarbazf', 'barbazfoo') == True
