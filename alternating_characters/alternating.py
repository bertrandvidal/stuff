number_test_cases = int(input("Enter the number of test cases: "))

for idx in range(number_test_cases):
    test_case = input("Test case #{} ".format(idx+1))
    suppression = 0
    for i, c in enumerate(test_case):
        if i < 1:
            continue
        if c == test_case[i-1]:
            suppression += 1
    print("{} suppression(s) for '{}'".format(suppression, test_case))
