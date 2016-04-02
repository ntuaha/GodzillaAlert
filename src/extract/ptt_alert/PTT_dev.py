# -*- coding: utf-8 -*-

import re
import sys
import os
import psycopg2
import cookielib, urllib2,urllib
from lxml import html,etree
import lxml
import StringIO
import datetime
import json
#處理掉unicode 和 str 在ascii上的問題
reload(sys)
sys.setdefaultencoding('utf8')

from pymongo import ASCENDING, DESCENDING
#aha's library
from WEB import WEB
from RAW_DB import RAW_DB
from ROBOT_dev import ROBOT



class PTT_DB(RAW_DB):
  db = "diaster"
  #table = "foreign_ex"
  def __init__(self,path,table,diaster_type,source_type):
    RAW_DB.__init__(self,path,self.db)
    self.table = self.db[table]
    self.table_name = table
    self.diaster_type = diaster_type
    self.source_type = source_type

  # Type 災難類型
  # Occur_dt 發生時間
  # Source_link 來源連結
  def isExistNews(self,record):
    if self.table.find({"link":record['link']}).count()>0:
      return True
    else:
      return False

  def bulkInsertNews(self,news):
    print "asdfsend News %d"%len(news)
    insert_data = []
    early_dt = datetime.datetime.now()
    event = None
    postFB = False
    for n in news:
      #if self.isExistNews(n) ==False:
      #如果是新事件
      if early_dt >= n['occur_dt']:
        early_dt = n['occur_dt']
        event = n
        postFB=True
      insert_data.append(n)
      #print n
    #else:
      #如果是舊事件
      print "OLD [%s]:%s:%s"% (n['occur_dt'].strftime("%Y-%m-%d %H:%M:%S"),n['title'],n["link"])
    #送看到的最新一筆
    if postFB==True:
      print "send to FB"
      ROBOT().sendFB(event)
    count = len(insert_data)
    if count >0:
      self.table.insert(insert_data)
      #Build index
      self.table.create_index([("diaster_type", DESCENDING), ("occur_dt", ASCENDING)])
      self.log()
    return count

  def log(self):
    #Insert to LOG
    self.db["log"].insert({"crawler_dt":datetime.datetime.now(),"source_type":self.source_type,"diaster_type":self.diaster_type})



class PTT:
  def __init__(self,init_link,diaster_type):
    self.web = WEB()
    self.init_link = init_link
    self.diaster_type = diaster_type

  def getRawData(self,url):
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'over18=1'))
    print url
    response = opener.open(url)
    the_page = response.read()
    response.close()
    return the_page



  def fetchListDOM(self,url):
    the_page = self.getRawData(url)
    # 將網頁轉成結構化資料
    parser = etree.HTMLParser()
    root = etree.parse(StringIO.StringIO(the_page),parser)
    # 抓指定位置的連結

    link = root.xpath(u".//div[contains(@class, 'btn-group pull-right')]//a[contains(text(),'‹ 上頁')]/@href")
    if link is not None:
      return [root.xpath(".//*[contains(@class, 'r-ent')]"),"https://www.ptt.cc"+link[0]]
    else:
      return [root.xpath(".//*[contains(@class, 'r-ent')]"),None]

  def fetchListPage(self,url,time):
    rows,prev = self.fetchListDOM(url)
    rows_cnt = len(rows)
    links = []
    next_page = True
    for row in rows:
      add_flag = False
      datum = {}
      datum['author'] = row.xpath(".//*[contains(@class, 'author')]")[0].text.strip()
      if datum['author'] =='-':
        continue
      temp = row.xpath(".//*[contains(@class, 'title')]/a")[0].text.strip()
      #print "title: %s"%temp
      #猜是主文
      m = re.match(u"\[(\w+)\](.*)",temp,re.U)
      if m is not None:
        datum['category'] = m.group(1).strip()
        datum['title'] = m.group(2).strip()
        datum['article_leader']= 1
        #是地震文才納入
        if datum['category']=="爆卦" and self.diaster_type in datum['title'] and datum['title'][0:2]!='R:':
          add_flag = True

      else:
        #猜是回文
        m = re.match(u"Re:.*\[(\w+)\](.*)",temp,re.U)
        if m is not None:
          datum['category'] = m.group(1).strip()
          datum['title'] = m.group(2).strip()
          datum['article_leader']= 0
        else:
          datum['title'] = temp
      datum['link'] = "https://www.ptt.cc"+row.xpath(".//*[contains(@class, 'title')]/a/@href")[0].strip()
      month,day = map(int,rows[0].xpath(".//*[contains(@class, 'date')]")[0].text.strip().split("/"))
      if datetime.datetime.now().month < month:
        year = datetime.datetime.now().year-1
      else:
        year = datetime.datetime.now().year
      #datum['date'] = datetime.datetime(year,month,day)
      m = re.match(u".+\.(\d{10})\..+",datum['link'],re.U)
      datum['date'] = datetime.datetime.fromtimestamp(int(m.group(1)))

      datum['author'] = row.xpath(".//*[contains(@class, 'author')]")[0].text.strip()

      nrec = row.xpath(".//*[contains(@class, 'nrec')]/span//text()")
      #推噓計數器
      if len(nrec)>0:
        datum['nrec'] = nrec[0].strip()
      else:
        datum['nrec'] = "0"
      mark = row.xpath(".//*[contains(@class, 'mark')]//text()")
      if len(mark)>0:
        datum['mark'] = mark[0].strip()


      if add_flag==True:
        print "%s:%s"%(datum['title'],datum['link'])
        d = self.fetchContent(datum['link'])
        for key,value in d.iteritems():
          datum[key] = value
        #print datum['occur_dt']
        #print time
        #if datum['occur_dt'] >= time:
        links.append(datum)
      if datum['date'] < time and url!=self.init_link:
          next_page=False
      #print '%s: %s'%(datum['date'].strftime('%Y-%m-%d %H:%M:%S'),datum['title'])

    print len(links)
    return (links,prev,next_page)

#https://www.ptt.cc/bbs/Loan/M.1421172025.A.797.html
  def fetchContent(self,url):
      print url
      the_page = self.getRawData(url)
      parser = etree.HTMLParser()
      root = etree.parse(StringIO.StringIO(the_page),parser)
      datum = {}
      #作者與心情
      temp = root.xpath(u'.//div[@class="article-metaline" and span[@class="article-meta-tag"]="作者"]/span[@class="article-meta-value"]/text()')
      datum['author']=""
      datum['mood']=""
      if len(temp)>0:
        m = re.match(u"(\w+) \((.*)\)+",temp[0].strip(),re.U)
        if m is not None:
          datum['author'] = m.group(1).strip()
          datum['mood'] = m.group(2).strip()

      #article time
      temp = root.xpath(u'.//div[@class="article-metaline" and span[@class="article-meta-tag"]="時間"]/span[@class="article-meta-value"]/text()')
      datum['edittime'] = []
      if len(temp)>0:
        datum['edittime'].append(datetime.datetime.strptime(temp[0].strip(),'%a %b %d %H:%M:%S %Y'))
        datum['occur_dt'] = datetime.datetime.strptime(temp[0].strip(),'%a %b %d %H:%M:%S %Y')

      #content && footer
      datum['author_ip'] = []
      datum['content'] = []
      contents = root.xpath(".//div[@id='main-content']/node()[not(@class='article-metaline' or @class='article-metaline-right' or @class='push')]")
      for content in contents:
        color = ""
        text = ""
        if type(content) == lxml.etree._Element:
          #link
          if len(content.xpath("./@href"))>0:
            datum['content'].append({'color':'','text':content.xpath("./@href")[0].strip()})
            continue

          c_class = content.xpath("./@class")
          if c_class is not None:
            c_class = c_class[0].strip()
          else:
            c_class =''

          text = content.xpath("./text()")
          if len(text)>0:
            text = text[0].strip()
          else:
            text = ''

          #可能是結尾
          if c_class =='f2':
            #跳過
            m = re.match(u"※ 文章網址:",text,re.U)
            if m is not None:
              continue
            #找發文IP
            m = re.match(u"※ 發信站: 批踢踢實業坊\(ptt.cc\), 來自: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",text,re.U)
            if m is not None:
              datum['author_ip'].append(m.group(1))
              continue
            m = re.match(u"※ 編輯: \w+ \((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\), (\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})",text,re.U)
            if m is not None:
              datum['author_ip'].append(m.group(1))
              datum['edittime'].append(datetime.datetime.strptime(m.group(2),'%m/%d/%Y %H:%M:%S'))
              continue
          elif c_class=='hl':
            m = re.match(u"◆ From: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",text,re.U)
            if m is not None:
              datum['author_ip'].append(m.group(1))
              continue
          #都不是就放出
          datum['content'].append({'color':c_class,'text':text})

        elif type(content) == lxml.etree._ElementUnicodeResult or type(content) == lxml.etree._ElementStringResult:
          datum['content'].append({'color':'','text':content.replace("\n\n","\n").strip()})
        else:
          raise 'ERROR TYPE'

      return datum


  def fetchData(self,time,limit=0):
    total_links = []
    jump = False
    url = self.init_link
    count = 0
    page = 0
    while 1:
      links,url,next_page = self.fetchListPage(url,time)
      total_links.extend(links)
      if next_page ==False:
        break
    return total_links


#顯示文章內容
def show(rows):
  for post in posts:
    print "=============="
    for k,v in post.iteritems():
      if k!='content' and k!='pushs':
        print '%s:%s'%(k,v)
      elif k=='content':
        for c in v:
          print "%s:%s"%(c['color'],c['text'])
      elif k=='pushs':
        for c in v:
          print "%s:%s:%s:%s"%(c['user'],c['ip'],c['tag'],c['content'])


if __name__ =="__main__":
  DIASTER_TYPE = "地震"
  ptt = PTT('https://www.ptt.cc/bbs/Gossiping/index.html',DIASTER_TYPE)
  #ptt = PTT('https://www.ptt.cc/bbs/Gossiping/index7908.html',DIASTER_TYPE)
  #db = PTT_DB(os.path.dirname(__file__)+"/mongodb.inf","diaster","ptt_gossiping",DIASTER_TYPE)
  now = datetime.datetime.now()
  t = datetime.datetime(now.year,now.month,now.day,now.hour,now.minute,now.second) - datetime.timedelta(minutes=3)
  #t = datetime.datetime(2015,1,18,2,30,38)
  print t
  if len(sys.argv)>1:
    limit = int(sys.argv[1])
  else:
    limit = 0
  posts = ptt.fetchData(t,limit)



  #Append News
  #print db.bulkInsertNews(posts)
