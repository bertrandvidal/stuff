from challenge import open_next_level

import requests
import pickle

print '\n'.join([''.join([p[0] * p[1] for p in row]) for row in pickle.loads(requests.get("http://www.pythonchallenge.com/pc/def/banner.p").content)])
open_next_level("channel")
