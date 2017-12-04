from string import ascii_lowercase

# https://www.codeeval.com/public_sc/37/

def pangram(input_sentence):
    input_sentence = set(input_sentence.lower())
    missing_letters = []
    if input_sentence == set(ascii_lowercase):
        return None
    for c in ascii_lowercase:
        if c not in input_sentence:
            missing_letters.append(c)
    return missing_letters or None


assert pangram(ascii_lowercase) is None
assert pangram(ascii_lowercase.replace("z", "a")) == ["z"]
assert pangram(ascii_lowercase.replace("z", "a").replace("b", "a")) == ["b", "z"]

to_be_replaced = []
for c in ascii_lowercase:
    to_be_replaced.append(c)
    alphabet = ascii_lowercase
    for to_replace in to_be_replaced:
        alphabet.replace(to_replace, "a")
        missing_letters_for_pangram = pangram(alphabet)
        assert missing_letters_for_pangram == to_be_replaced or \
               alphabet == ascii_lowercase and missing_letters_for_pangram is None

print("done!")
