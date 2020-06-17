#-*-coding: utf-8-*-

import requests
import json

class Weixin(object):
  def __init__ (self, corpid = None, corpsecret = None):
    self.corpid = corpid
    self.corpsecret = corpsecret
    self.access_token = ''
  # 获取ACCESS_TOKEN
  def getToken (self):
    if (self.corpid and self.corpsecret):
      # 拼接请求地址
      requrl = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + self.corpid +'&corpsecret=' + self.corpsecret
      # 存储接收到的数据
      res = requests.get(requrl).json()
      if (res['errcode'] == 0):
        self.access_token = res['access_token']
      # print(res)
      return res['errcode'], res['access_token']
  # 发送消息
  def sendMessage (self, option = None):
    # 拼接请求地址
    requrl = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.access_token
    # print(option)
    # print(self.access_token)
    res = requests.post(requrl, data = json.dumps(option)).json()
    return res
  # 获得JS-SDK使用权限签名
  def getJsApiTicket (self):
    # 拼接请求地址
    requrl = 'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token=' + self.access_token
    # print(option)
    res = requests.get(requrl).json()
    return res