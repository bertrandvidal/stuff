from challenge import open_next_level
import requests

def get_next_nothing(content):
  return content.split()[-1]

def get_page(nothing):
  response = requests.get("http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=%s" % nothing)
  response.raise_for_status()
  return response.content

nothing = 44827
while nothing:
  nothing = get_next_nothing(get_page(nothing))
  print "Next nothing is '%s'" % nothing
  try:
    int(nothing)
  except ValueError as val_error:
    print "This might be the one", val_error
    open_next_level(nothing)
