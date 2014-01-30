import sys
import unicodedata

with open(sys.argv[1], "r") as text_file:
  text = u"".join([unicodedata.normalize("NFKD", line) for line in text_file]).lower()
print text
