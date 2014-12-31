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

reload(sys)
sys.setdefaultencoding('utf8')


class GET_TEST:
  database=""
  user=""
  password=""
  host=""
  port=""
  conn = None
  cur = None
  def __init__(self,filepath):
    f = open(filepath,'r')
    self.database = f.readline()[:-1]
    self.user = f.readline()[:-1]
    self.password = f.readline()[:-1]
    self.host = f.readline()[:-1]
    self.port =f.readline()[:-1]
    f.close()
    self.startDB()

  #啟用DB
  def startDB(self):
    self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
    self.cur = self.conn.cursor()


  #結束DB
  def endDB(self):
    self.cur.close()
    self.conn.close()

  def run(self):
    sql = "SELECT count(distinct event_id) from event;";
    self.cur.execute(sql)
    data_num  = self.cur.fetchall()[0][0]
    sql = "INSERT INTO event (event_id,data_dt,event_name) VALUES (%d,now(),'%s')" %(data_num+1,"HI")
    self.cur.execute(sql)
    self.conn.commit()


  def getDATA(self):
    '''
    GET /realtime/RoadAll.php HTTP/1.1
    Host: rtr.pbs.gov.tw
    Connection: keep-alive
    Pragma: no-cache
    Cache-Control: no-cache
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36
    Referer: http://rtr.pbs.gov.tw/realtime/RoadAll.php
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4


    url = 'http://rtr.pbs.gov.tw/realtime/RoadAll.php'
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'),('Accept-Encoding',' gzip, deflate, sdch'),('Accept-Language','zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4'),('Cache-Control','no-cache'),('Pragma','no-cache'),('Connection','keep-alive'),('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')]
    response = opener.open(url)
    the_page = response.read()
    response.close()
    parser = etree.HTMLParser()
    '''
    f = os.path.dirname(__file__)+'/data.dat'
    os.system('wget http://rtr.pbs.gov.tw/realtime/RoadAll.php -O %s'%f)
    #print f
    root = etree.parse(f,etree.HTMLParser())
    rows = root.xpath('//*[@id="myTable"]/tbody/tr')
    #print len(rows)
    length = len(rows)

    for i in range(length):
      tds = rows[i].xpath('.//td')
      no = tds[0]
      event_type = tds[1].text
      event_source = '警察廣播電台'
      event_provider = tds[6].text
      event_name = " ".join(tds[2].xpath('.//text()')).replace("\n","").replace("\t","")
      position_desc = tds[3].text
      event_status = ",".join(tds[3].xpath('./font/text()')).replace("\n","").replace("\t","").replace(" ","")
      if len(tds[4].xpath('./div/text()'))>0:
        data_dt = tds[4].xpath('./div/text()')[0]+' '+tds[5].xpath('./div/text()')[0]
      else:
        data_dt = '1970-01-01'
      #print event_type
      #print event_source
      #print event_provider
      #print event_name
      #print position_desc
      #print event_status
      #print data_dt
      event_id = self.getEventId(event_name,position_desc,data_dt)
      if event_id > 0 :
        sql = "INSERT INTO event (event_id,event_name,event_type,data_dt,event_status,event_source,event_provider,position_desc,etl_dt) VALUES (%d,'%s','%s','%s','%s','%s','%s','%s',now());"%(event_id,event_name,event_type,data_dt,event_status,event_source,event_provider,position_desc)
        print sql
        self.cur.execute(sql)
        self.conn.commit()
      else:
        print 'no'
    os.system('rm %s'%f)




  def getEventId(self,event_name,position_desc,data_dt):
    sql ="SELECT count(*) from event where event_name='%s' and position_desc = '%s' and data_dt ='%s'"%(event_name,position_desc,data_dt)
    self.cur.execute(sql)
    data_num  = self.cur.fetchall()[0][0]
    if data_num==0:
      sql ="SELECT max(event_id)+1 from event";
      self.cur.execute(sql)
      event_id  = self.cur.fetchall()[0][0]
    else:
      event_id= 0
    return event_id

  def getString(self,node):
    return node.text


def main():
  print "\nHI";


if __name__ == '__main__':
  print os.path.dirname(__file__)+'/../../link.info'
  ahaDB = GET_TEST(os.path.dirname(__file__)+'/../../link.info')
  ahaDB.run()
  ahaDB.getDATA()
  ahaDB.endDB()

  main()

