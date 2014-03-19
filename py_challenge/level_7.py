from challenge import open_next_level
import requests
import zipfile
import os
import tempfile


tmp = tempfile.mkdtemp()
(_, archive_path) = tempfile.mkstemp(dir=tmp)

with open(archive_path, "w") as channel:
  response = requests.get("http://www.pythonchallenge.com/pc/def/channel.zip")
  response.raise_for_status()
  channel.write(response.content)

archive = zipfile.ZipFile(archive_path)

nothing = 90052
comments = []
while nothing:
  current = "%s.txt" % nothing
  data = archive.read(current)
  comments.append(archive.getinfo(current).comment)
  nothing = data.split()[-1]
  try:
    int(nothing)
  except ValueError as val_error:
    print "This might be the one", val_error
    break

print "".join(comments)

open_next_level("oxygen")
