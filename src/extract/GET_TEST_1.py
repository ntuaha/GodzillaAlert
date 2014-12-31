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




  def getDATA(self):
    '''
  event_id bigserial,
  start_dt timestamp,
  end_dt timestamp,
  update_dt timestamp,
  predict_time timestamp,
  name varchar,
  type varchar,
  status varchar,
  source varchar,
  provider varchar,
  position_desc varchar,
  lat real,
  lng real,
  alt real,
  address varchar,
  description varchar,
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
      description = tds[3].text
      #event_status = ",".join(tds[3].xpath('./font/text()')).replace("\n","").replace("\t","").replace(" ","")
      event_status = "事件發生中"
      for status in tds[3].xpath('./font/text()'):
        if status =="排除":
          event_status = "事件已排除"
          break
        elif status =="持續":
          event_status = "事件發生中"
        else:
          event_status = "事件發生中"

      if len(tds[4].xpath('./div/text()'))>0:
        data_dt = tds[4].xpath('./div/text()')[0]+' '+tds[5].xpath('./div/text()')[0]
      else:
        data_dt = '1970-01-01'

      event_id = self.getEventId(data_dt,description)
      if event_id > 0 :
        #Update
        if event_status =="事件發生中":
          sql = "UPDATE event SET update_dt=now() where event_id = %d"%event_id
          print sql
        elif event_status =="事件已排除":
          sql = "UPDATE event SET update_dt=now(), event_status='%s',end_dt=now() WHERE event_id=%d "%(event_status,event_id)
          print sql
        else:
          sql = "UPDATE event SET update_dt=now() where event_id = %d"%event_id
          print sql
      else:
        sql = "INSERT INTO event (name,type,start_dt,update_dt,status,source,provider,description) VALUES ('%s','%s','%s',now(),'事件發生中','%s','%s','%s');"%(event_name,event_type,data_dt,event_source,event_provider,description)
        print sql
      self.cur.execute(sql)
      self.conn.commit()


    os.system('rm %s'%f)




  def getEventId(self,start_dt,description):
    sql ="SELECT event_id from event where start_dt='%s' and description = '%s' "%(start_dt,description)
    self.cur.execute(sql)
    result = self.cur.fetchall()
    if len(result)>0:
      data_num  = result[0][0]
    else:
      data_num = 0
    return data_num

  def getString(self,node):
    return node.text


def main():
  print "\nHI";


if __name__ == '__main__':
  print os.path.dirname(__file__)+'/../../link.info'
  ahaDB = GET_TEST(os.path.dirname(__file__)+'/../../link.info')
  ahaDB.getDATA()
  ahaDB.endDB()

  main()

