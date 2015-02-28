# -*- coding: utf-8 -*-


import sys
import os
import psycopg2
import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO
import datetime
import json
#處理掉unicode 和 str 在ascii上的問題


reload(sys)
sys.setdefaultencoding('utf8')

from pymongo import ASCENDING, DESCENDING
#aha's library
sys.path.append('/home/aha/Project/NewsInsight/src/lab2/rawdata/')
from WEB import WEB
from RAW_DB import RAW_DB



class PGSQL_AHA():
  def __init__(self):
    f = open('/home/aha/Project/NewsInsight/src/lab/link.info','r')
    database = f.readline()[:-1]
    user = f.readline()[:-1]
    password = f.readline()[:-1]
    host = f.readline()[:-1]
    port =f.readline()[:-1]
    f.close()
    self.conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    self.cur = self.conn.cursor()

  def close(self):
    self.conn.close()



class MONGO_AHA(RAW_DB):
  def __init__(self,path):
    RAW_DB.__init__(self,path,"robot")
    self.table = self.db["fb_log"]

  def addLog(self,data):
    self.table.insert({"post_dt":datetime.datetime.now(),"data":data})


class ROBOT:
  url = 'http://ga-saw.cloudapp.net/fb/feed'
  target_dt = datetime.datetime.now()-datetime.timedelta(days=1)

  def __init__(self):
    self.pgsql = PGSQL_AHA()




  def sendFB(self,datum):
    print '地震'
    f = {}
    if "author" in datum:
      f['message'] = "PTT鄉民%s 發表地震訊息! 塊陶阿"%datum['author']
    if "title" in datum and "occur_dt" in datum:
      f['name'] = "[%s] %s"%(datum['occur_dt'].strftime("%Y-%m-%d %H:%M:%S"),datum['title'])
    #if "content" in datum:
    #  f['description'] = "搞笑ㄇ"
    if "link" in datum:
      f['link'] = datum['link']

    opener = urllib2.build_opener()
    response = opener.open(self.url,urllib.urlencode(f))
    data = response.read()
    response.close()
    print data
    return self


  def close(self):
    self.pgsql.close()
    return self






if __name__ =="__main__":

  mongo = MONGO_AHA(os.path.dirname(__file__)+"/mongodb.inf")
  data = {}
  data['author'] = "aha"
  data["occur_dt"] = datetime.datetime.now()
  data["title"] = "2015新春愉快"
  #data["link"] = "https://www.ptt.cc/bbs/WomenTalk/M.1423685800.A.04B.html"
  data["content"] = "恭賀新禧 你今天精彩嗎 祝你今年事事順心快樂!"
  robot = ROBOT().sendFB(data).close()


