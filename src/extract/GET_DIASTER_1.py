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
    url = 'http://thb-gis.thb.gov.tw/HistoryEventListDetail.aspx?EVTNO=254,thb'
    #value = urllib.urlencode( {'date' : d.strftime("%Y%m%d")})
    #print url
    #print value
    response = urllib2.build_opener().open(url)
    the_page = response.read()
    response.close()
    page = etree.parse(StringIO.StringIO(the_page))
    namespace={'kml': "http://www.opengis.net/kml/2.2"}
    name = page.xpath('//kml:Document/kml:Folder/kml:name',namespaces={'kml': "http://www.opengis.net/kml/2.2"})[0].text
    folders = page.xpath('//kml:Document/kml:Folder/kml:Folder',namespaces={'kml': "http://www.opengis.net/kml/2.2"})
    for folder in folders:
      event_status = folder.xpath('.//kml:name',namespaces=namespace)[0].text
      events = folder.xpath(".//kml:Folder",namespaces=namespace)
      for event_categories in events:
          event_type = event_categories.xpath('.//kml:name',namespaces=namespace)[0].text
          events = event_categories.xpath('.//kml:Placemark',namespaces=namespace)
          for event in events:
              event_name = event.xpath('.//kml:name',namespaces=namespace)[0].text
              description = event.xpath('.//kml:description',namespaces=namespace)[0].text
              point = event.xpath('.//kml:Point/kml:coordinates',namespaces=namespace)[0].text
              [lng,lat,alt] = map(float,point.split(","))
              event_id = self.getEventId(lat,lng,event_name)

              sql = "INSERT INTO event (event_id,event_name,event_type,data_dt,event_status,description,lng,lat,alt) VALUES (%d,'%s','%s',now(),'%s','%s',%f,%f,%f);"%(event_id,event_name,event_type,event_status,description.replace("\'","\'\'"),lng,lat,alt)
              self.cur.execute(sql)
              self.conn.commit()




  def getEventId(self,lat,lng,event_name):
    sql ="SELECT count(*) from event where lat=%f and lng=%f and event_name = '%s' "%(lat,lng,event_name)
    self.cur.execute(sql)
    data_num  = self.cur.fetchall()[0][0]
    if data_num==0:
      sql ="SELECT max(event_id)+1 from event";
      self.cur.execute(sql)
      event_id  = self.cur.fetchall()[0][0]
    else:
      sql ="SELECT event_id from event where lat=%f and lng=%f and event_name = '%s'"%(lat,lng,event_name)
      self.cur.execute(sql)
      event_id  = self.cur.fetchall()[0][0]
    return event_id




def main():
  print "\nHI";


if __name__ == '__main__':
  print os.path.dirname(__file__)+'/../../link.info'
  ahaDB = GET_TEST(os.path.dirname(__file__)+'/../../link.info')
  ahaDB.run()
  ahaDB.getDATA()
  ahaDB.endDB()

  main()

