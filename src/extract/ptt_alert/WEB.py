# -*- coding: utf-8 -*-

#import re

#處理掉unicode 和 str 在ascii上的問題
import sys
#import os
import psycopg2
import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO
import datetime
import json

reload(sys)
sys.setdefaultencoding('utf8')


class WEB:
  def getRawData(self,url,d=None):
    if d is not None:
      value = urllib.urlencode( d)
      response = urllib2.build_opener().open(url,value)
    else:
      response = urllib2.build_opener().open(url)
    the_page = response.read()
    response.close()
    return the_page

if __name__ =="__main__":
  url = 'http://news.cnyes.com/Ajax.aspx?Module=GetRollNews'
  d=  {'date' : datetime.datetime.now().strftime("%Y%m%d")}
  web = WEB()
  print web.getRawData(url,d)


