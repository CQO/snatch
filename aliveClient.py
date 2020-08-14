import requests
import json
import time

url = "http://154.8.196.163:8009/updata"

class AliveClient(object):
  def __init__ (self, name = None, interval = None):
    self.name = name
    self.interval = interval
  def updata(self):
    payload = json.dumps({"name": self.name,"endTime": int(round(time.time() * 1000)) + self.interval})
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data = payload)

    # print(response.text.encode('utf8'))
