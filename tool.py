#-*-coding: utf-8-*-
import re

class Tool(object):
  # 截取字符串
  def subString(str, start, end = "", startInd = 0):
    startIndex = str.find(start, startInd)
    if (startIndex == -1): return ''
    if end == "":
      return str[startIndex + len(start):]
    else:
      # print(startIndex)
      endIndex = str.find(end, startIndex + len(start))
      if (endIndex == -1): return ''
      # print(endIndex)
      # print(str[startIndex + len(start):endIndex])
      return str[startIndex + len(start):endIndex]

  # 截取字符串组
  def subStringArr(str, start, end):
    arr = []
    nextIndex = 0
    while True:
      nextIndex = str.find(start, nextIndex + 1)
      if nextIndex == -1:
        return arr
      temp = Tool.subString(str, start, end, nextIndex)
      if str == '':
        return arr
      arr.append(temp)

  def clearIP (ipString):
    # 不管是ip还是网址都应该存在.
    if "." not in ipString:
      return False
    # 过滤掉内网地址
    temp = ipString.split('.')[0]
    if temp == '10':
      return False
    if temp == '127':
      return False
    temp2 = ipString.split('.')[1]
    if temp == '172' and temp2 == '16':
      return False
    if temp == '192' and temp2 == '168':
      return False
    return True

  def clearText (text):
    text = text.replace('&#39;', "'")
    text = text.replace('&quot;', "'")
    # text = re.sub(r'<span class="pl.*">', '', text)
    text = text.replace('<span class="pl-c1">', ':')
    text = text.replace('<span class="pl-v">', '')
    text = text.replace('<span class="pl-k">', '')
    text = text.replace('<span class="pl-s">', '')
    text = text.replace('<span class="pl-en">', '')
    text = text.replace('<span class="pl-pds">', '')
    # text = text.replace('<span class="pl-v">', '')
    text = text.replace('</span>', '')
    text = text.replace(' ', "")
    return text