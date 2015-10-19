import random


def selection_sort(arr):
    if len(arr) <= 1:
        return arr
    for i in range(len(arr)):
        minimum = arr[i]
        min_idx = i
        for j in range(i, len(arr)):
            if arr[j] < minimum:
                minimum = arr[j]
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


array = range(10)
random.shuffle(array)
assert selection_sort(array) == sorted(range(10))
assert selection_sort([]) == []
assert selection_sort([12]) == [12]


def insertion_sort(arr):
    if len(arr) <= 1:
        return arr
    for i in range(len(arr)):
        j = i
        while j > 0 and arr[j-1] > arr[j]:
            arr[j], arr[j-1] = arr[j-1], arr[j]
            j -= 1
    return arr



array = range(10)
random.shuffle(array)
assert insertion_sort(array) == sorted(range(10))
assert insertion_sort([]) == []
assert insertion_sort([12]) == [12]


def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr.pop(0)
    left = quick_sort([x for x in arr if x < pivot])
    right = quick_sort([x for x in arr if x >= pivot])
    return left + [pivot] + right


array = range(10)
random.shuffle(array)
assert quick_sort(array) == sorted(range(10))
assert quick_sort([]) == []
assert quick_sort([12]) == [12]



def merge(l, r):
    arr = []
    while l and r:
        if l[0] < r[0]:
            arr.append(l.pop(0))
        else:
            arr.append(r.pop(0))
    arr.extend(l)
    arr.extend(r)
    return arr


def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    middle = len(arr) // 2
    left = merge_sort(arr[:middle])
    right = merge_sort(arr[middle:])
    return merge(left, right)


array = range(10)
random.shuffle(array)
assert merge_sort(array) == sorted(range(10))
assert merge_sort([]) == []
assert merge_sort([12]) == [12]




