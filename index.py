# -*- coding: utf-8 -*
import time
import requests
import datetime
from tool import Tool
from weixin import Weixin
from requests.cookies import RequestsCookieJar
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

weixin = Weixin(corpid="ww7192afc91d2f618a", corpsecret="lmLChwwkbfleWMUxJKkk2QLp121Lse-BU92Z08fC_fc")

cookiesData = ''

def getcookie():
  global cookiesData
  response = requests.post("https://project.peopleurl.cn/php/interface/login.php", {'username': '蒲鸽', 'password': 'MMit7750'})
  print(response.text)
  #获取response中的cookies

  cookies=response.cookies.get_dict()

  print("获取到cookies: " + cookies["PHPSESSID"])

  cookiesData = cookies["PHPSESSID"]

# 获取cookie
getcookie()

# 已经提醒的订单
orderList = {"39": True, "38": True, "30": True, "40": True}

# 数据清理
def clear(text):
  text = text.replace('\r', '')
  text = text.replace('\n', '')
  text = text.replace('\t', '')
  return text


def ddxx(id):
  cookie_jar = RequestsCookieJar()
  cookie_jar.set("PHPSESSID", cookiesData, domain="project.peopleurl.cn")
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
    if (itemID in orderList):
      # print(orderList)
      print("跳过重复的订单: " + itemID)
    else:
      orderList[itemID] = True
      name = itemList[1]
      name = name.replace('<a href="order.php?id=' + itemID + '">', '')
      name = name.replace('</a>', '')
      name = name.replace('>', '')
      
      department = itemList[4]
      
      department = department.replace(' style="width: 130px;">', '')
      department = department.replace('>', '')
      sendMessage("项目编号: %s\n项目名称: %s\n%s" % (itemID, name, ddxx(itemID)))

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
  print("获取最新订单信息")
  cookie_jar.set("PHPSESSID", cookiesData, domain="project.peopleurl.cn")
  response = requests.get("https://project.peopleurl.cn/partyb/main.php", cookies = cookie_jar)
  # print(response.text)
  htmlData = clear(response.text)
  dataList = Tool.subStringArr(htmlData, '<table>', '</table>')
  content = weiqiang(dataList[0])


def getPageDeadLine(key):
  cookie_jar = RequestsCookieJar()
  cookie_jar.set("PHPSESSID", cookiesData, domain="project.peopleurl.cn")
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
#   cookie_jar.set("PHPSESSID", cookiesData, domain="project.peopleurl.cn")
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
# 每10分钟获取cook
scheduler.add_job(getcookie, 'cron', minute="1", id='job1')

# 每10秒获取最新订单
scheduler.add_job(getPageCode, 'interval', seconds=5, id='job2')
scheduler.start()

# scheduler.add_job(alertDeadLine, 'cron', hour='17', minute='00', second='00', id='job3')
