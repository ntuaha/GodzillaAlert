# -*- coding: utf-8 -*-



import re

#處理掉unicode 和 str 在ascii上的問題
import sys
import os

#自己的library
from DB import *

reload(sys)
sys.setdefaultencoding('utf8')



class EVENT_STATUS:
  STOP = 0
  RUNNING = 1
  WATCHING = 2


class GET(EVENT_STATUS):
  SOURCE = None
  LINK = None
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
    if 'lat' in data:
      sql_string.append(['lat',"%f"%data['lat']])
    if 'lng' in data:
      sql_string.append(['lng',"%f"%data['lng']])
    if 'alt' in data:
      sql_string.append(['alt',"%f"%data['alt']])

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
    if 'update_dt' in data:
      sql_string.append(["update_dt","'%s'"%data['update_dt']])
    else:
      sql_string.append(["update_dt","now()"])
    if 'predict_dt' in data:
      sql_string.append(["predict_dt","'%s'"%data['predict_dt']])

    sql_string.append(["description","'%s'"%data['description']])
    if data['status']==EVENT_STATUS.STOP:
      sql_string.append("end_dt=now()")
    if 'lat' in data:
      sql_string.append(["lat","%f"%data['lat']])
    if 'lng' in data:
      sql_string.append(["lng","%f"%data['lng']])
    if 'alt' in data:
      sql_string.append(["alt","%f"%data['alt']])

    sql_string.append(["type","'%s'"%data['type']])
    sql_string.append(["status","%d"%data['status']])
    if 'address' in data:
      sql_string.append(["address","'%s'"%data['address']])
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
    if 'lat' in data:
      sql_string.append(["lat=%f"%data['lat']])
    if 'lng' in data:
      sql_string.append(["lng=%f"%data['lng']])
    if 'alt' in data:
      sql_string.append(["alt=%f"%data['alt']])
    if 'update_dt' in data:
      sql_string.append("update_dt='%s'"%data['update_dt'])
    else:
      sql_string.append("update_dt=now()")
    if 'description' in data:
      sql_string.append("description='%s'"%data['description'])

    sql_string.append("type='%s'"%data['type'])
    sql_string.append("status=%d"%data['status'])
    content = ",".join(sql_string)
    sql = "UPDATE event SET %s WHERE event_id=%d"%(content,data['event_id'])
    self.db.execute(sql)
    #補上log
    self.appendLog(data)



  def run(self):
    data = self.getData()
    for d in data:
      id = self.getEventId(d)
      if id>0:
        d['event_id'] = id
        self.updateEvent(d)
      elif id==0:
        self.createEvent(d)
        print "create"
    self.close()


  def getData(self):
    raise '得到data'

  def getIdString(self,datum):
    raise '如何得到資料識別'


  def getEventId(self,datum):
    try:
      where = " AND ".join(self.getIdString(datum))
      sql ="SELECT event_id from event where %s "%where
      result = self.db.select(sql)
      if len(result)>0:
        data_num  = result[0][0]
      else:
        data_num = 0
      return data_num
    except Exception as e:
      print e
      print datum





if __name__ == '__main__':
  pass



