API_URL = "http://q.daskeyboard.com"

headers = {'Content-Type': 'application/json'}
data = {
    "clientId": "",
    "clientSecret": "",
    "grantType": "client_credentials"
}

# result = requests.post(API_URL + "/oauth/1.3/token", json=data, headers=headers)
# access_token = result.json()["access_token"]

from pprint import pprint
from random import choice
from universalclient import Client

q_api = Client(API_URL, headers=headers)

response = q_api.oauth._("1.3").token.post(json=data)
json_data = response.json()
pprint(json_data)
access_token = json_data["access_token"]

zones = q_api.api._("1.0").DK5QPID.zones.get(headers={"Authorization": "Bearer " + access_token})

signals = q_api.api._("1.0").signals._setArgs(headers={"Authorization": "Bearer " + access_token})


def gen_hex_colour_code():
    return ''.join([choice('0123456789ABCDEF') for _ in xrange(6)])


for k in zones.json():
    signal_data = {
        "name": "all of them at once",
        "pid": "DK5QPID",
        "effect": "SET_COLOR",
        "zoneId": k["id"],
        "color": "#FFF"
    }
    print "setting '%s'" % k["name"]
    response = signals.post(json=signal_data)
    if not response.ok:
        pprint(response.json())
