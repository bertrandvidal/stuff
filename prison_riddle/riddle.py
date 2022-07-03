# see https://youtu.be/iSNsgj1OCLA?t=632; I just can't understand the
# explanation no matter how many times I watch it so I'm "proving" it to myself
# by coding it

import random

nb_boxes = 100

user_nb = random.randint(0, nb_boxes - 1)
boxes = [i for i in range(nb_boxes)]

for _ in range(10):
    random.shuffle(boxes)

current_box = user_nb
boxes_opened = []

while user_nb not in boxes_opened:
    current_box = boxes[current_box]
    boxes_opened.append(current_box)

assert user_nb == boxes_opened[-1]
print(f"{user_nb} == {boxes_opened[-1]} | size: {len(boxes_opened)} | {boxes_opened}")

loops = []

for i in range(nb_boxes):
    current_loop = set()
    current_box = i
    while i not in current_loop:
        current_box = boxes[current_box]
        current_loop.add(current_box)
    current_loop.add(i)
    if current_loop not in loops:
        loops.append(current_loop)

print(f"{len(loops)} loops")

for l in loops:
    print(f"{len(l)}: {l}")

assert sum(len(l) for l in loops) == nb_boxes
