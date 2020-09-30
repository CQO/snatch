import requests
import json
import time
from subprocess import Popen, PIPE

url = "http://t.lamp.run/alive"

def getIPAddrs():
  p = Popen("hostname -I", shell=True, stdout=PIPE)
  data = p.stdout.read() # 获取命令输出内容
  data = str(data,encoding = 'UTF-8') # 将输出内容编码成字符串
  ip_list = data.split(' ') # 用空格分隔输出内容得到包含所有IP的列表
  if "\n" in ip_list: # 发现有的系统版本输出结果最后会带一个换行符
      ip_list.remove("\n")
  print(ip_list)
  return ip_list

ip_list = getIPAddrs()

class AliveClient(object):
  def __init__ (self, name = None, interval = None):
    self.name = name
    self.interval = interval
  def updata(self):
    payload = json.dumps({
      "name": self.name,
      "endTime": int(round(time.time() * 1000)) + self.interval,
      "message": '机器IP:' + str(ip_list)
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data = payload)

    print(response.text.encode('utf8'))
