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

  target_dt = datetime.datetime.now()-datetime.timedelta(days=1)
  #message = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y-%m-%d")+'重點新聞\n'
  api = '688430041191592'
  api_secret = '6bb097ca9fe10f1bca0c1c320232eba2'
  callback_website = 'http://104.46.234.139/GA/index.html'
  picture_url_tick = 'http://media-cache-ec0.pinimg.com/originals/ad/50/b1/ad50b19f53a97e8d577c665040d426dd.jpg'
  caption='快逃啊'
  facebook_id = '100000185149998'

  def __init__(self):
    self.pgsql = PGSQL_AHA()




  def sendFB(self,datum):

    opener = urllib2.build_opener()
    urllib2.install_opener(opener)
    ff={}
    ff['client_id']=self.api
    ff['client_secret']=self.api_secret
    ff['grant_type']='client_credentials'
    param = urllib.urlencode(ff)
    print 'https://graph.facebook.com/oauth/access_token?%s'%(param)
    response = opener.open('https://graph.facebook.com/oauth/access_token?%s'%(param))

    data = response.read()
    response.close()
    self.access_token = data.split('=')[1]
    print self.access_token

    f = {}

    f['message'] = "[%s] %s"%(datum['occur_dt'].strftime("%Y-%m-%d %H:%M:%S"),datum['title'])
    #f['picture'] = self.picture_url_tick
    #f['caption'] = self.caption
    #f['link'] = self.callback_website
    #param = urllib.urlencode(f)
    #for k,v in f.iteritems():
      #print v
      #f[k] = urllib.quote(v.encode('utf8'))
      #print f[k]
    #url = 'https://graph.facebook.com/%s/feed?%s&'%(self.facebook_id,data)+param
    url = 'https://graph.facebook.com/%s'%self.facebook_id
    print url

    cmd = []
    cmd.append("-F '%s=%s'"%('access_token',self.access_token))
    cmd.append("-F '%s=%s'"%('message',"PTT鄉民%s 發表地震訊息! 塊陶阿"%datum['author'] ))
    cmd.append("-F '%s=%s'"%('name',f['message'] ))
    cmd.append("-F '%s=%s'"%('icon',self.picture_url_tick ))
    cmd.append("-F '%s=%s'"%('caption',"Godzilla Alert" ))
    cmd.append("-F '%s=%s'"%('link',datum['link'] ))
    f_words = " ".join(cmd)


    work = "/usr/bin/curl %s  -k https://graph.facebook.com/%s/feed"%(f_words,self.facebook_id)
    print work
    cmd = os.popen(work)
    #opener = urllib2.build_opener()
    #reponse = opener.open(url,urllib.urlencode(f))
    #reponse = opener.open(url)
    #data = response.read()
    #reponse.close()
    print data

    return self
#https://graph.facebook.com/100000185149998/feed?access_token=688430041191592%7C1apOpKzaTmbqC6AIjvSSlJF-4Jo&message=%E6%9C%AC%E6%97%A5%E9%87%8D%E9%BB%9E%E6%96%B0%E8%81%9E%0A
#/usr/local/bin/curl -F grant_type=client_credentials -F client_id=688430041191592 -F client_secret=6bb097ca9fe10f1bca0c1c320232eba2 -k https://graph.facebook.com/oauth/access_token


  def close(self):
    self.pgsql.close()
    return self






if __name__ =="__main__":

  mongo = MONGO_AHA(os.path.dirname(__file__)+"/../mongodb.inf")
  robot = ROBOT().pickNews().sendFB().close()
  #print robot.pickNews()
  #robot.close()


