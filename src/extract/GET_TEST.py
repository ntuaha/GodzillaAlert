# -*- coding: utf-8 -*-



import re

#處理掉unicode 和 str 在ascii上的問題
import sys
import os
import psycopg2
import datetime
import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO

#自己的libaray
#from DB_NOW import DB_NOW
#from READSITE import READSITE

reload(sys)
sys.setdefaultencoding('utf8')


class GET_TEST:
  def __init__(self):
    pass

def main():
  print "HI";


if __name__ == '__main__':
  main()
