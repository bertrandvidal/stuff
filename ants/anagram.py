from itertools import permutations, izip
from hashlib import md5
from math import factorial
from multiprocessing import Pool,current_process

with open("./md5.txt", "r") as f:
    target_md5 = [l.strip("\n") for l in f]

with open("./words.txt", "r") as f:
    wordlist = [line.strip("\n") for line in f]


def match_one_anagram(a, idx):
    if idx % 1000 ==  0:
        print "'%s' checking '%s' - %d" % (current_process().name, a, idx)
    if md5("".join(a)).hexdigest() in target_md5:
        return a


if __name__ == "__main__":
    sentence = "poultry outwits ants".replace(" ", "")
    all_anagrams = permutations(sentence)
    total_permutations = factorial(len(sentence))
    nb_processes = 10
    pool = Pool(nb_processes)
    print "using %d process - %d total perms " % (nb_processes,
                                                  total_permutations)
    results = pool.imap_unordered(match_one_anagram,
                                  izip(all_anagrams, xrange(total_permutations)),
                                  total_permutations / nb_processes * 10)
    print "closing pool"
    pool.close()
    pool.join()
    idx = 0
    print "going through results"
    for r in results:
        if r:
            print r
        if idx % 100 == 0:
            print "run ", idx
        idx += 1
