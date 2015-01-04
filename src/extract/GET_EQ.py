# -*- coding: utf-8 -*-



import re

#處理掉unicode 和 str 在ascii上的問題
import sys
import os
import datetime
import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO
import json

#自己的library
from DB import *
from GET import *

reload(sys)
sys.setdefaultencoding('utf8')


class GET_EQ(GET):
  SOURCE = '中央氣象局'
  SOURCE_TYPE = '中央氣象局_地震'
  SOURCE_LINK = 'http://www.cwb.gov.tw/V7/modules/MOD_EC_Home.htm'


  def getData(self):
    #從中央氣象局
    response = urllib2.build_opener().open(self.SOURCE_LINK)
    the_page = response.read()
    response.close()
    # 將網頁轉成結構化資料
    parser = etree.HTMLParser()
    root = etree.parse(StringIO.StringIO(the_page),parser)
    rows = root.xpath('//tr')
    length = len(rows)
    data = []
    for i in range(length):
      if i ==0:
        continue
      tds = rows[i].xpath('.//td')

      datum = {}
      datum['source'] = self.SOURCE
      datum['type'] = self.SOURCE_TYPE

      datum['lat'] = float(tds[2].text.strip())
      datum['lng'] = float(tds[3].text.strip())
      datum['alt'] = float(tds[5].text.strip())*(-1000.0) #深度 所以是負的（原始單位為km)
      detail_data= {}
      if tds[7].text[0:3]=="ECL":
        detail_data['link']= "http://www.cwb.gov.tw/V7/earthquake/Data/local/"+tds[7].text
        datecode = tds[7].text[3:13]
      else:
        detail_data['link']= "http://www.cwb.gov.tw/V7/earthquake/Data/quake/"+tds[7].text
        datecode = tds[7].text[2:12]
      start_dt = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y')+datecode,'%Y%m%d%H%M%S')
      if datetime.datetime.now()<= start_dt:
        start_dt = start_dt.replace(year=start_dt.year-1)
      datum['start_dt'] = start_dt.strftime("%Y-%m-%d %H:%M:%S")
      detail_data['level']= float(tds[4].text.strip())
      detail_data['no']= tds[0].text.strip()
      datum['DATA'] = json.dumps(detail_data)
      rough_area = tds[6].xpath(".//text()")[0].replace("\"","").strip()
      town = tds[6].xpath(".//text()")[1].replace("(","").replace(")","")[2:].strip()
      datum['address'] = town
      datum['description'] = "時間:%s 規模:%f 地點:%s 原始資料:%s"%(datum["start_dt"],detail_data['level'],town,detail_data['link'])
      datum['status'] = self.RUNNING
      datum['title'] = rough_area
      datum['provider'] = self.SOURCE
      data.append(datum)
    return data

  def updateEvent(self,data):
    #補上log
    #self.appendLog(data)
    #只是單純更新不加資料
    pass

  def reset(self):
    self.db.execute("DELETE from event WHERE type='%s'"%(self.SOURCE_TYPE))
    self.db.execute("DELETE from event_log WHERE type='%s'"%(self.SOURCE_TYPE))

  def getIdString(self,datum):
    sql_string = []
    sql_string.append("lat='%f'"%datum['lat'])
    sql_string.append("lng='%f'"%datum['lng'])
    sql_string.append("alt='%f'"%datum['alt'])
    sql_string.append("type='%s'"%datum['type'])
    sql_string.append("start_dt='%s'"%datum['start_dt'])
    return sql_string



if __name__ == '__main__':
  ahaDB = GET_EQ(os.path.dirname(__file__)+'/../../link.info')
  if len(sys.argv)>1:
    if sys.argv[1] == 't':
      ahaDB.reset()
  ahaDB.run()




