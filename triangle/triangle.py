import os

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "small_triangle.txt"))

with open(file_path, "r") as triangle:
  lines = triangle.readlines()

base = [int(v.strip()) for v in lines[-1].split(" ") if v.strip()]
lines = lines[:-1]

print base

for line in lines:
  values = [int(v.strip()) for v in line.split(" ") if v.strip()]
  if len(values) == 1:
    base[0] += values[0]
    continue
  for idx, value in enumerate(values):
    print "base[%s]:"%(idx-1), base[idx+1] + values[idx], base[idx+1] + values[idx-1]
    base[idx+1] += max(values[idx], values[idx-1])
  print base
print max(base)
