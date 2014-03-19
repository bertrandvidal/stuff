import os
import webbrowser

NEXT_LEVEL_URL = "http://www.pythonchallenge.com/pc/def/%s.html"


def open_next_level(page):
  """Open the default webbrowser using the given parameter.

  Args:
    page: the name of the next page to open - no extension required.
  """
  page = os.path.splitext(page)[0]
  webbrowser.open(NEXT_LEVEL_URL % page)
