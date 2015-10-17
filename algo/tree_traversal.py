

class Node(object):

    def __init__(self, value, left, right):
        self.value = value
        self.left = left
        self.right = right


right_1_right_2 = Node(6, None, None)
right_1_left_2 = Node(5, None, None)
left_1_right_2 = Node(4, None, None)
left_1_left_2 = Node(3, None, None)
right_1 = Node(2, right_1_left_2, right_1_right_2)
left_1 = Node(1, left_1_left_2, left_1_right_2)
root = Node(0, left_1, right_1)


def pre_order(node):
    if node is None:
        return
    print(node.value)
    pre_order(node.left)
    pre_order(node.right)


print("PreOrder")
pre_order(root)


def in_order(node):
    if node is None:
        return
    in_order(node.left)
    print(node.value)
    in_order(node.right)


print("InOrder")
in_order(root)


def post_order(node):
    if node is None:
        return
    post_order(node.left)
    post_order(node.right)
    print(node.value)


print("PostOrder")
post_order(root)


def breadth_first(node, queue=None):
    queue = queue or []
    if node is None:
        return queue
    if not queue:
        queue.append(node.value)
    if node.left is not None:
        queue.append(node.left.value)
    if node.right is not None:
        queue.append(node.right.value)
    queue = breadth_first(node.left, queue)
    queue = breadth_first(node.right, queue)
    return queue


print("BreadthFirst")
print(breadth_first(root))


def level_order(root):
    queue = []
    queue.append(root)
    while queue:
        node = queue.pop(0)
        print(node.value)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)


level_order(root)


