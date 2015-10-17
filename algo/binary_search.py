import sys

search = int(sys.argv[1])
numbers = range(0, int(sys.argv[2]))

def bin_search(n, array, op=0):
    middle_index = len(array)/2
    if n < array[middle_index]:
        bin_search(n, array[:middle_index], op+1)
    elif n > array[middle_index]:
        bin_search(n, array[middle_index:], op+1)
    print(n, middle_index, array[middle_index], op)

bin_search(search, numbers)

