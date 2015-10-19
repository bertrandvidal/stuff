

def is_permutation(str1, str2):
    return sorted(str1) == sorted(str2)


assert is_permutation("", "foo") == False
assert is_permutation("Nib", "bin") == False
assert is_permutation("a ct", "c at") == True


def array_permutation(str1, str2):
    if len(str1) != len(str2):
        return False
    total = [0] * 128
    for char in str1:
        total[ord(char)] += 1
    for char in str2:
        total[ord(char)] -= 1
    return min(total) == max(total) == 0

assert array_permutation("", "foo") == False
assert array_permutation("Nib", "bin") == False
assert array_permutation("a ct", "c at") == True
