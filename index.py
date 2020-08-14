# -*- coding: utf-8 -*
import time
import json
import requests
import datetime
from tool import Tool
from weixin import Weixin
from aliveClient import AliveClient
from requests.cookies import RequestsCookieJar
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

def login():
  response = requests.post("http://172.31.9.1:8080/PortalServer/Webauth/webAuthAction!login.action", {'userName': 'puge', 'password': 'MMit7750'})
  print(response.text)

# 先自动登录网络
login()

weixin = Weixin(corpid="ww7192afc91d2f618a", corpsecret="lmLChwwkbfleWMUxJKkk2QLp121Lse-BU92Z08fC_fc")
alive = AliveClient(name="全媒体抢单监控", interval = 5 * 60 * 1000)
cookiesData = ''



def getcookie():
  global cookiesData
  response = requests.post("https://project.peopleurl.cn/php/interface/login.php", {'username': '蒲鸽', 'password': 'MMit7750'})
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

# 数据清理
def clear(text):
  text = text.replace('\r', '')
  text = text.replace('\n', '')
  text = text.replace('\t', '')
  return text


def ddxx(id):
  cookie_jar = RequestsCookieJar()
  cookie_jar.set("PHPSESSID", cookiesData["PHPSESSID"], domain="project.peopleurl.cn")
  cookie_jar.set("sso_s", cookiesData["sso_s"], domain="peopleurl.cn")
  cookie_jar.set("sso_u", cookiesData["sso_u"], domain="peopleurl.cn")
  response = requests.get("https://project.peopleurl.cn/partyb/bid.php?id=" + id, cookies = cookie_jar)
  # print(response.text)

  # 分析处理数据
  # 申请人
  sqr = Tool.subString(response.text, '<td>申请人</td><td><input type="text" value="', '" id=')
  sqbm = Tool.subString(response.text, '<td>申请部门</td><td><input type="text" value="', '" id=')
  lxfs = Tool.subString(response.text, '<td>联系方式</td><td><input type="text" id="contact" value="', '" readonly')
  wcsj = Tool.subString(response.text, '<td>完成时间</td><td><input type="text" id="dealtime" value="', '" readonly')
  xxxq = Tool.subString(response.text, '<p><span>详细需求：</span></p>', '</div>')
  xqms = Tool.subString(response.text, '<textarea id="description" readonly>', '</textarea>')
  return "申请人: %s\n申请部门: %s\n联系方式: %s\n完成时间: %s\n详细需求: %s\n需求描述: %s\n" % (sqr, sqbm, lxfs, wcsj, xxxq, xqms)

def weiqiang(text):
  dataList = Tool.subStringArr(text, '<tr>', '</tr>')
  returnData = ''
  for item in dataList:
    itemList = Tool.subStringArr('sdsd' + item, '<td', '</td>')
    itemID = itemList[0]
    itemID = itemID.replace('>', '')
    if not itemID.isdigit():
      print("跳过异常订单: " + itemID)
      continue
    if (itemID not in orderList):
      orderList[itemID] = True
      name = itemList[1]
      name = name.replace('<a href="order.php?id=' + itemID + '">', '')
      name = name.replace('</a>', '')
      name = name.replace('>', '')
      
      department = itemList[4]
      
      department = department.replace(' style="width: 130px;">', '')
      department = department.replace('>', '')
      print('发现新订单:' + itemID)
      sendMessage("项目编号: %s\n项目名称: %s\n%s" % (itemID, name, ddxx(itemID)))
      with open('data.json', 'w') as f:
        f.write(json.dumps(orderList))
        f.close()

def sendMessage(content):
  weixin.getToken()
  weixin.sendMessage({
    "touser" : "@all",
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
  response = requests.get("https://project.peopleurl.cn/partyb/main.php", cookies = cookie_jar)
  # print(response.text)
  htmlData = clear(response.text)
  dataList = Tool.subStringArr(htmlData, '<td>操作</td>', '</table>')
  content = weiqiang(dataList[0])
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

# # 提醒编辑确认
# def alertDeadLine():
#   cookie_jar = RequestsCookieJar()
#   cookie_jar.set("PHPSESSID", cookiesData["PHPSESSID"], domain="project.peopleurl.cn")
#   response = requests.get("https://project.peopleurl.cn/partyb/list.php", cookies = cookie_jar)
#   # print(response.text)
#   # htmlData = clear(response.text)
#   dataList = Tool.subStringArr(response.text, 'href="view.php?id=', '">')
  
#   # content = weiqiang(dataList[0])
#   alertText = ''
#   for key in dataList:
#     # 判断是否过期
#     alertText += getPageDeadLine(key)
#   if (alertText != ''):
#     sendMessage('有编辑未点击完成项目:\n' + alertText)

# alertDeadLine()

scheduler = BlockingScheduler()
# 每60分钟获取cook
scheduler.add_job(getcookie, 'interval', seconds=3600, id='job1')

# 每10秒获取最新订单
scheduler.add_job(getPageCode, 'interval', seconds=20, id='job2')

# 每5小时登陆一次wifi
scheduler.add_job(login, 'interval', seconds=3600 * 5, id='job3')
scheduler.start()


# scheduler.add_job(alertDeadLine, 'cron', hour='17', minute='00', second='00', id='job3')
