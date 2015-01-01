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

class DB:
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

  def execute(self,sql):
    print sql
    self.cur.execute(sql)
    self.conn.commit()

  def select(self,sql):
    print sql
    self.cur.execute(sql)
    result = self.cur.fetchall()
    return result

class EVENT_STATUS:
  stop = 0
  running = 1
  monitoring = 2


class GET_TEST:
  def __init__(self,filepath):
    self.db = DB(filepath)
    self.db.startDB()

  def close(self):
    self.db.endDB()



  def extractData(self,tds):
    '''

    '''
    #no of row, but its useless
    no = tds[0]
    #event type: 道路施工
    event_type = tds[1].text
    #熱心聽眾
    event_provider = tds[6].text
    #地點
    event_name = " ".join(tds[2].xpath('.//text()')).replace("\n","").replace("\t","")
    #路況說明
    description = tds[3].text
    #路況說明: 持續, 排除, 後續
    event_status = EVENT_STATUS.running
    for status in tds[3].xpath('./font/text()'):
      if status =="排除":
        event_status = EVENT_STATUS.stop
        break

    #事件起始時間
    if len(tds[4].xpath('./div/text()'))>0:
      start_dt = tds[4].xpath('./div/text()')[0]+' '+tds[5].xpath('./div/text()')[0]
    else:
      start_dt = '1970-01-01'

    return [no,event_type,event_prodiver,event_name,event_status,start_dt,description]

  def addLog(self,event_id,status):
    sql = "INSERT INTO event_log (event_id,status,log_dt) VALUES (%d,%d,now());"%(event_id,status)
    self.db.execute(sql)

  def updateEvent(self,event_id,status,event_source):
    sql = "UPDATE event SET update_dt=now() where event_id = %d"%event_id
    self.db.execute(sql)
    self.addLog(event_id,status)

  def closeEvent(self,event_id,status,event_source):
    sql = "UPDATE event SET update_dt=now(), status=%d,end_dt=now() WHERE event_id=%d "%(event_status,event_id)
    self.db.execute(sql)
    self.addLog(event_id,status,event_source)

  def createEvent(self,event_name,event_type,start_dt,event_source,event_provider,description):
    sql = "INSERT INTO event (name,type,start_dt,update_dt,status,source,provider,description) VALUES ('%s','%s','%s',now(),%d,'%s','%s','%s');"%(event_name,event_type,start_dt,event_source,Event_Status.running,event_provider,description)
    self.db.execute(sql)
    event_id = self.getEventId(data_dt,description)
    self.addLog(event_id,"新增活動",event_source)
    return event_id

  def forceCloseEvent(self,id_list,source):
    ids = ",".join(map(str,id_list))
    sql = "SELECT event_id FROM event WHERE event_id not in (%s) and source='%s' and status=%d"%(ids,source,EVENT_STATUS.running)
    result = self.db.select(sql)
    close_ids = [r[0] for r in result]
    print close_ids
    sql = "UPDATE event SET status=%d where event_id in (%s)"%(EVENT_STATUS.stop,",".join(map(str,close_ids)))
    self.db.execute(sql)

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

    #download data from 警廣
    f = os.path.dirname(__file__)+'/data.dat'
    os.system('wget http://rtr.pbs.gov.tw/realtime/RoadAll.php -O %s'%f)

    #convert html file to object
    root = etree.parse(f,etree.HTMLParser())
    rows = root.xpath('//*[@id="myTable"]/tbody/tr')
    length = len(rows)
    # data source
    event_source = '警察廣播電台'
    event_link = 'http://rtr.pbs.gov.tw/realtime/RoadAll.php'
    id_list = []
    for i in range(length):
      #Process on each row
      tds = rows[i].xpath('.//td')
      [no,event_type,event_prodiver,event_name,event_status,start_dt,description] = self.extractData(tds)
      event_id = self.getEventId(event_source,data_dt,description,event_source)

      if event_id > 0 :
        if event_status==EVENT_STATUS.stop:
          self.closeEvent(event_id,event_status,event_source)
        else:
          self.updateEvent(event_id,event_status,event_source)
        id_list.append(event_id)
      else:
          id = self.createEvent(self,event_name,event_type,start_dt,event_source,event_provider,description)
          id_list.append(id)
    #清掉其他沒被更新，但目前還在進行中的事件
    self.forceCloseEvent(id_list)
    #結束這個檔案的處理
    os.system('rm %s'%f)




  def getEventId(self,event_source,start_dt,description):
    sql ="SELECT event_id from event where start_dt='%s' and description = '%s' and source='%s' "%(start_dt,description,event_source)
    result = self.db.select(sql)
    if len(result)>0:
      data_num  = result[0][0]
    else:
      data_num = 0
    return data_num




if __name__ == '__main__':
  print os.path.dirname(__file__)+'/../../link.info'
  ahaDB = GET_TEST(os.path.dirname(__file__)+'/../../link.info')
  ahaDB.getDATA()
  ahaDB.close()



