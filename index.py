# -*- coding: utf-8 -*-
import time
import sys
import json
import requests
import datetime
from tool import Tool
from weixin import Weixin
from aliveClient import AliveClient
from requests.cookies import RequestsCookieJar
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# 手动设置编码
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def login():
  print('登陆网络')
  response = requests.post("http://172.31.9.1:8080/PortalServer/Webauth/webAuthAction!login.action", {'userName': 'puge', 'password': 'MMit7750'})
  print(response.text)

# 先自动登录网络
# login()

weixin = Weixin(corpid="ww7192afc91d2f618a", corpsecret="lmLChwwkbfleWMUxJKkk2QLp121Lse-BU92Z08fC_fc")
alive = AliveClient(name="全媒体抢单监控", interval = 5 * 60 * 1000)
cookiesData = ''



def getcookie():
  global cookiesData
  response = requests.post("https://project.peopleurl.cn/interface/public/index.php/user/login", json.dumps({"username": "蒲鸽", "password": "MMit7750"}))
  print(response.text)
  #获取response中的cookies

  cookies=response.cookies.get_dict()
  print(cookies)

  cookiesData = cookies



# 加载文件
data = open('data.json', 'r')
# 已经提醒的订单
orderList = json.loads(data.read())
data.close()


# 获取cookie
getcookie()

def ddxx(item):
  return "申请部门: %s\n联系方式: %s\n完成时间: %s\n详细需求: %s\n需求描述: %s\n" % (item['dep_name'], item['contact'], item['finish_time_f'], item['form_type_name'], item['description'])

def weiqiang(dataList):
  returnData = ''
  for item in dataList:
    itemID = item['id']
    if (itemID not in orderList):
      orderList[itemID] = True
      name = item['name']
      department = item['description']
      print('发现新订单:' + itemID)
      sendMessage("项目编号: %s\n项目名称: %s\n%s" % (itemID, name, ddxx(item)))
      with open('data.json', 'w') as f:
        f.write(json.dumps(orderList))
        f.close()

def sendMessage(content):
  weixin.getToken()
  weixin.sendMessage({
    # PuGe
    "touser" : "@all",
    # "touser" : "PuGe",
    "msgtype" : "text",
    "agentid" : 1000002,
    "text" : {
      "content" : content
    },
    "safe":0
  })

def getPageCode():
  cookie_jar = RequestsCookieJar()
  print("获取最新订单信息-" + time.asctime(time.localtime(time.time())))
  cookie_jar.set("PHPSESSID", cookiesData["PHPSESSID"], domain="project.peopleurl.cn")
  cookie_jar.set("sso_s", cookiesData["sso_s"], domain="peopleurl.cn")
  cookie_jar.set("sso_u", cookiesData["sso_u"], domain="peopleurl.cn")
  response = requests.post("https://project.peopleurl.cn/interface/public/index.php/order/xqlists", '{"demand_type":1,"pageInfo":{"page":1,"pageSize":15,"total":1},"searchInfo":{"status":"","dep_id":"","name":"","form_type":""}}', cookies = cookie_jar)
  # print(response.text)
  resData = response.json()
  # print(resData['data']['lists'])
  content = weiqiang(resData['data']['lists'])
  # 获取临时单子
  response = requests.post("https://project.peopleurl.cn/interface/public/index.php/order/xqlists", '{"demand_type":2,"pageInfo":{"page":1,"pageSize":15,"total":1},"searchInfo":{"status":"","dep_id":"","name":"","form_type":""}}', cookies = cookie_jar)
  # print(response.text)
  resData = response.json()
  # print(resData['data']['lists'])
  content = weiqiang(resData['data']['lists'])
  alive.updata()


def getPageDeadLine(key):
  cookie_jar = RequestsCookieJar()
  cookie_jar.set("PHPSESSID", cookiesData["PHPSESSID"], domain="project.peopleurl.cn")
  cookie_jar.set("sso_s", cookiesData["sso_s"], domain="peopleurl.cn")
  cookie_jar.set("sso_u", cookiesData["sso_u"], domain="peopleurl.cn")
  response = requests.get("https://project.peopleurl.cn/partyb/view.php?id=" + key, cookies = cookie_jar)
  date = Tool.subString(response.text, '<td>完成时间</td><td><input type="text" value="', '" readonly></td>')
  dateTime_p = datetime.datetime.strptime(date,'%Y-%m-%d')
  # 需求名称
  name = Tool.subString(response.text, 'id="ordername" value="', '" readonly>')
  returnText = ''
  if dateTime_p.__le__(datetime.datetime.now()):
    return returnText + key + '. ' + name + '\n'
  return ''

getPageCode()

scheduler = BlockingScheduler(timezone="Asia/Shanghai")
# 每60分钟获取cook
scheduler.add_job(getcookie, 'interval', seconds=3600, id='job1')

# 每10秒获取最新订单
scheduler.add_job(getPageCode, 'interval', seconds=20, id='job2')

# 每5小时登陆一次wifi
scheduler.add_job(login, 'interval', seconds=3600 * 5, id='job3')
scheduler.start()


# scheduler.add_job(alertDeadLine, 'cron', hour='17', minute='00', second='00', id='job3')
