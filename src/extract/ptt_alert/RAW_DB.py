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
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding('utf8')


class RAW_DB:
  def __init__(self,path,db):
    f = open(path,'r')
    address = f.readline()[:-1]
    port = int(f.readline()[:-1])
    self.client = MongoClient(address,port)
    self.db = self.client[db]
    return self.db
    f.close()

  def close(self):
    self.client.close()


if __name__=="__main__":
  pass
