import requests
import json
import time
import psutil

url = "http://t.lamp.run/alive"

def getIPAddrs():
  """
  通过给定前缀跨平台查询ip
  :param prefix:  需要查询的ip前缀
  :return: ip地址
  """
  localIP = []
  dic = psutil.net_if_addrs()
  for adapter in dic:
    snicList = dic[adapter]
    for snic in snicList:
      if not snic.family.name.startswith('AF_INET'):
        continue
      localIP.append(snic.address)

  return localIP

ip_list = ','.join(getIPAddrs())

class AliveClient(object):
  def __init__ (self, name = None, interval = None):
    self.name = name
    self.interval = interval
  def updata(self):
    payload = json.dumps({
      "name": self.name,
      "endTime": int(round(time.time() * 1000)) + self.interval,
      "message": '',
      "IP": ip_list
    })
    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data = payload)

    print(response.text.encode('utf8'))
