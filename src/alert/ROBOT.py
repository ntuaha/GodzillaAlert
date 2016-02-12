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

class ROBOT:
  def __init__(self):
    self.api = os.environ.get('AHA_FB_API')
    self.api_secret = os.environ.get('AHA_FB_SECRET_API')
    self.callback_website = 'http://104.46.234.139/GA/index.html'
    self.facebook_id = os.environ.get('AHA_USER_FB_ID')
    print self.api
    print self.api_secret

  def getFBToken(self):
    '''
    https://graph.facebook.com/100000185149998/feed?access_token=688430041191592%7C1apOpKzaTmbqC6AIjvSSlJF-4Jo&message=%E6%9C%AC%E6%97%A5%E9%87%8D%E9%BB%9E%E6%96%B0%E8%81%9E%0A
    /usr/local/bin/curl -F grant_type=client_credentials -F client_id=688430041191592 -F client_secret=6bb097ca9fe10f1bca0c1c320232eba2 -k https://graph.facebook.com/oauth/access_token
    '''
    opener = urllib2.build_opener()
    urllib2.install_opener(opener)
    ff={}
    ff['client_id']=self.api
    ff['client_secret']=self.api_secret
    ff['grant_type']='client_credentials'
    param = urllib.urlencode(ff)
    if __debug__:
      print 'https://graph.facebook.com/oauth/access_token?%s'%(param)
    response = opener.open('https://graph.facebook.com/oauth/access_token?%s'%(param))
    data = response.read()
    response.close()
    access_token = data.split('=')[1]
    if __debug__:
      print access_token
    return access_token

  def buildFBcommand(self,author,event):
    fb_description = []
    fb_description.append("-F '%s=%s'"%('access_token', self.getFBToken()))
    fb_description.append("-F '%s=%s'"%('message', "%s 發表%s"%(author, event["message"])))
    fb_description.append("-F '%s=%s'"%('name', "[%s] %s"%(event['createdAT'].strftime("%Y-%m-%d %H:%M:%S"),event['title'])))
    fb_description.append("-F '%s=%s'"%('icon', 'http://media-cache-ec0.pinimg.com/originals/ad/50/b1/ad50b19f53a97e8d577c665040d426dd.jpg' ))
    fb_description.append("-F '%s=%s'"%('caption',"Godzilla Alert" ))
    fb_description.append("-F '%s=%s'"%('link', event['link']))
    cmd = "/usr/bin/curl %s  -k https://graph.facebook.com/%s/feed"%( " ".join(fb_description), self.facebook_id)
    if __debug__:
      print "[cmd] %s"%cmd
    return cmd

  def sendFB(self,cmd):
    result = os.popen(cmd)
    print result


def unitTest(robot):
  (author,createdAt,link,message,title) = sys.argv[1:]
  event = {}
  event["message"]  = message
  event["title"] = title
  event["link"] = link
  event["createdAT"]  = datetime.datetime.strptime(createdAt,"%Y-%m-%dT%H:%M:%S+08:00")
  with open(os.path.split(os.path.abspath(__file__))[0]+'/link.info','r') as f:
    (api,api_secret,facebook_id) = f.readlines()
  robot.api = api.strip()
  robot.api_secret = api_secret.strip()
  robot.facebook_id = facebook_id.strip()
  cmd = robot.buildFBcommand(author,event)
  robot.sendFB(cmd)

def main():
  robot = ROBOT()
  unitTest(robot)


if __name__ =="__main__":
  main()
