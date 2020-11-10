#!/bin/bash env
# Taken from https://leetcode.com/problems/add-two-numbers/


class Node:
    def __init__(self, value, nextNode = None):
        self.value = value
        self.next = nextNode

    def toInt(self, depth = 0):
        subTotal = 0
        if self.next:
            subTotal += self.next.toInt(depth + 1)
        return self.value * (10 ** depth) + subTotal


n = Node(0)
assert n.toInt() == 0

n = Node(1)
assert n.toInt() == 1

n = Node(1, Node(0, Node(2)))
assert n.toInt() == 201


class AddNodeNumbers:

    def add(self, n1: Node, n2: Node) -> Node:
        return self._add(n1, n2, 0)

    def _add(self, n1: Node, n2: Node, carry: int) -> Node:
        carry, value = divmod(n1.value + n2.value + carry, 10)
        n = Node(value)
        if n1.next or n2.next or carry:
            n.next = self._add(
                n1.next or Node(0),
                n2.next or Node(0),
                carry)
        return n


n1 = Node(2, Node(4, Node(3)))
n2 = Node(5, Node(6, Node(4)))
addition = AddNodeNumbers()
n3 = addition.add(n1, n2)
assert n3.toInt() == 807, f"{n3.toInt()} != 807"

n1 = Node(9, Node(9, Node(9, Node(9, Node(9)))))
n2 = Node(9, Node(9, Node(9)))
addition = AddNodeNumbers()
n3 = addition.add(n1, n2)
assert n3.toInt() == 99999 + 999, f"{n3.toInt()} != {99999 + 999}"


print("DONE")

