# -*- coding: utf-8 -*-



import re

#處理掉unicode 和 str 在ascii上的問題
import sys
import os
import datetime
import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO

#自己的library
from DB import *

reload(sys)
sys.setdefaultencoding('utf8')



class EVENT_STATUS:
  STOP = 0
  RUNNING = 1
  WATCHING = 2


class GET_PTS(EVENT_STATUS):
  SOURCE = '警察廣播電台'
  LINK = 'http://rtr.pbs.gov.tw/realtime/RoadAll.php'
  TEAM = 'SAW'

  def __init__(self,filepath):
    self.db = DB(filepath,beta=True)
    self.db.startDB()


  def close(self):
    self.db.endDB()

  def appendLog(self,data):
    '''
    event_id  bigint,
    update_dt  timestamp with time zone,
    type  char(3),
    status  integer,
    address  varchar,
    lat  real,
    lng  real,
    alt  real,
    description  varchar,
    source  varchar,
    provider  varchar,
    DATA  json,
    '''

    sql_string = []
    sql_string.append(['event_id',"%d"%data['event_id']])
    sql_string.append(['update_dt',"now()"])
    sql_string.append(['type',"'%s'"%data['type']])
    sql_string.append(['status',"%d"%data['status']])
    if 'address' in data:
      sql_string.append(['address',"'%s'"%data['address']])
    sql_string.append(['description',"'%s'"%data['description']])
    sql_string.append(['provider',"'%s'"%data['provider']])
    sql_string.append(['source',"'%s'"%data['source']])
    if 'DATA' in data:
      sql_string.append(['DATA',"'%s'"%data['DATA']])
    col = ",".join(map(str,[i[0] for i in sql_string]))
    values = ",".join(map(str,[i[1] for i in sql_string]))
    sql  = "INSERT INTO event_log (%s) VALUES (%s)"%(col,values)
    #print sql
    self.db.execute(sql)

  def createEvent(self,data):
    sql_string = []
    sql_string.append(["title","'%s'"%data['title']])
    sql_string.append(["start_dt","'%s'"%data['start_dt']])
    sql_string.append(["update_dt","now()"])
    sql_string.append(["description","'%s'"%data['description']])
    if data['status']==EVENT_STATUS.STOP:
      sql_string.append("end_dt=now()")
    sql_string.append(["type","'%s'"%data['type']])
    sql_string.append(["status","%d"%data['status']])
    if 'address' in data:
      sql_string.append(["address","'%d'"%data['address']])
    col = ",".join(map(str,[i[0] for i in sql_string]))
    values = ",".join(map(str,[i[1] for i in sql_string]))
    sql = "INSERT INTO event (%s) VALUES (%s)"%(col,values)
    #print sql
    self.db.execute(sql)
    #補上log
    id = self.getEventId(data)
    data['event_id'] = id
    self.appendLog(data)
    return id





  def updateEvent(self,data):
    '''
    包含更新資料，與結束資料
    event_id
name
start_dt
end_dt
update_dt
predict_time
type
description
status
lat
lng
alt
address
    '''
    sql_string = []
    sql_string.append("title='%s'"%data['title'])
    sql_string.append("start_dt='%s'"%data['start_dt'])
    if data['status']==EVENT_STATUS.STOP:
      sql_string.append("end_dt=now()")
    sql_string.append("update_dt=now()")
    sql_string.append("type='%s'"%data['type'])
    sql_string.append("status=%d"%data['status'])
    content = ",".join(sql_string)
    sql = "UPDATE event SET %s WHERE event_id=%d"%(content,data['event_id'])
    self.db.execute(sql)
    #補上log
    self.appendLog(data)




  def extractData(self,tds):

    #no of row, but its useless
    data = {}
    no = tds[0]
    #event type: 道路施工
    data['type'] = self.SOURCE+"_"+tds[1].text.strip()
    #熱心聽眾
    data['provider'] = tds[6].text.strip()
    if data['provider'] == None:
      data['provider'] = ""
    #地點
    data['title'] = " ".join(tds[2].xpath('.//text()')).replace("\n","").replace("\t","")
    #路況說明
    data['description'] = tds[3].text.strip()
    #路況說明: 持續, 排除, 後續
    event_status = self.RUNNING
    for status in tds[3].xpath('./font/text()'):
      if status.strip() =="排除":
        event_status = self.STOP
        break
    data['status'] = event_status

    #事件起始時間
    if len(tds[4].xpath('./div/text()'))>0:
      data['start_dt'] = tds[4].xpath('./div/text()')[0]+' '+tds[5].xpath('./div/text()')[0]
    else:
      #因為沒有數字  亂填
      data['start_dt'] = '1970-01-01 0:0:0'

    return data


  #強迫事件結束
  def forceCloseEvent(self,id_list):
    print id_list
    ids = ",".join(map(str,id_list))
    sql = "SELECT event_id FROM event WHERE event_id not in (%s) and status=%d and type like '%s%%' "%(ids,self.RUNNING,self.SOURCE)
    result = self.db.select(sql)
    close_ids = [r[0] for r in result]
    print close_ids
    if len(close_ids)>0:
      values= ",".join(map(str,close_ids))
      sql = "UPDATE event SET status=%d where event_id in (%s)"%(self.STOP,values)
      #print sql
      self.db.execute(sql)

      #系統更新到資料裡
      sql = "SELECT event_id,update_dt,type,status,description from event WHERE event_id in (%s)"%values
      result = self.db.select(sql)
      for r in result:
        data = {}
        data['event_id'] = r[0]
        data['update_dt'] = r[1]
        data['type'] = r[2]
        data['status'] = r[3]
        data['description'] = r[4]
        data['source'] = self.SOURCE
        data['provider'] = self.TEAM
        data['status'] = self.STOP

        self.appendLog(data)


  def getDATA(self):

    #download data from 警廣
    f = os.path.dirname(__file__)+'/data.dat'
    os.system('wget http://rtr.pbs.gov.tw/realtime/RoadAll.php -O %s'%f)
    root = etree.parse(f,etree.HTMLParser())
    rows = root.xpath('//*[@id="myTable"]/tbody/tr')
    length = len(rows)

    # data source
    id_list = []
    for i in range(length):
      data = {}
      data['source'] = self.SOURCE
      data['link'] = self.LINK

      #Process on each row
      data.update(self.extractData(rows[i].xpath('.//td')))
      #print data
      data['event_id'] = self.getEventId(data)
      if data['event_id'] > 0 :
        self.updateEvent(data)
        id_list.append(data['event_id'])
      else:
        del data['event_id']
        #找不到id  就新增
        id = self.createEvent(data)
        id_list.append(id)
    #清掉其他沒被更新，但目前還在進行中的事件

    self.forceCloseEvent(id_list)
    #結束這個檔案的處理
    os.system('rm %s'%f)




  def getEventId(self,data):
    try:
      start_dt = data['start_dt']
      description = data['description']
      sql ="SELECT event_id from event where start_dt='%s' and description = '%s' and status=%d "%(start_dt,description,self.RUNNING)
      result = self.db.select(sql)
      if len(result)>0:
        data_num  = result[0][0]
      else:
        data_num = 0
      return data_num
    except Exception as e:
      print e
      print data




if __name__ == '__main__':
  if len(sys.argv)>1:
    if sys.argv[1] == 't':
      os.system('psql -d godzilla_alert_b -f '+os.path.dirname(__file__)+'/../../sql/event.sql')
      os.system('psql -d godzilla_alert_b -f '+os.path.dirname(__file__)+'/../../sql/event_log.sql')

  #print os.path.dirname(__file__)+'/../../link.info'
  ahaDB = GET_PTS(os.path.dirname(__file__)+'/../../link.info')
  ahaDB.getDATA()
  ahaDB.close()



