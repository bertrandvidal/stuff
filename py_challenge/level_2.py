from collections import deque
from string import ascii_lowercase, maketrans

from challenge import open_next_level

to_translate = "g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj."

rotation = deque(ascii_lowercase)
rotation.rotate(-2)
trans_table = maketrans(ascii_lowercase, "".join(rotation))

translate = lambda x: x.translate(trans_table)

print translate(to_translate)

open_next_level(translate("map"))
