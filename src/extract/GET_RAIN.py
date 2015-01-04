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


class GET_RAIN(GET):
  SOURCE = '中央氣象局'
  SOURCE_TYPE = '中央氣象局_雨量'
  SOURCE_LINK = 'http://www.cwb.gov.tw/V7/observe/rainfall/A136.htm'


  def getData(self):
    #從中央氣象局
    response = urllib2.build_opener().open(self.SOURCE_LINK)
    the_page = response.read()
    response.close()
    # 將網頁轉成結構化資料
    parser = etree.HTMLParser()
    root = etree.parse(StringIO.StringIO(the_page),parser)
    # 資料時間
    datecode = root.xpath('//center/table[1]//tr/td[4]/text()')[0].strip()
    update_dt = datetime.datetime.strptime(datecode,'資料時間 : %Y/%m/%d %H:%M:%S')

    rows = root.xpath('//center/table[2]//tr')
    length = len(rows)-1
    data = []
    for i in range(length):
      if i ==0:
        continue
      tds = rows[i].xpath('.//td')

      datum = {}
      datum['source'] = self.SOURCE
      datum['type'] = self.SOURCE_TYPE

      #datum['lat'] = None
      #datum['lng'] = None
      #datum['alt'] = None

      datum['start_dt'] = "2015-01-01 0:0:0"
      datum['update_dt'] = update_dt.strftime("%Y-%m-%d %H:%M:%S")
      detail_data= {}
      detail_data['no']= tds[1].text.strip().split(" ")[1][1:-1]
      detail_data['10m']= tds[2].xpath(".//text()")[0].strip()
      detail_data['1h']= tds[3].xpath(".//text()")[0].strip()
      detail_data['3h']= tds[4].xpath(".//text()")[0].strip()
      detail_data['6h']= tds[5].xpath(".//text()")[0].strip()
      detail_data['12h']= tds[6].xpath(".//text()")[0].strip()
      detail_data['24h']= tds[7].xpath(".//text()")[0].strip()
      detail_data['d']= tds[8].xpath(".//text()")[0].strip()
      detail_data['1d']= tds[9].xpath(".//text()")[0].strip()
      detail_data['2d']= tds[10].xpath(".//text()")[0].strip()
      datum['DATA'] = json.dumps(detail_data)

      town = tds[0].text.strip()
      poi = tds[1].text.strip().split(" ")[0]

      datum['address'] = town+poi

      datum['status'] = self.WATCHING
      datum['title'] = town+'-'+poi+'-'+detail_data['no']
      datum['description'] = datum['DATA']
      datum['provider'] = self.SOURCE
      data.append(datum)
    return data



  def reset(self):
    self.db.execute("DELETE from event WHERE type='%s'"%(self.SOURCE_TYPE))
    self.db.execute("DELETE from event_log WHERE type='%s'"%(self.SOURCE_TYPE))

  def getIdString(self,datum):
    sql_string = []
    sql_string.append("title='%s'"%datum['title'])
    return sql_string



if __name__ == '__main__':
  ahaDB = GET_RAIN(os.path.dirname(__file__)+'/../../link.info')
  if len(sys.argv)>1:
    if sys.argv[1] == 't':
      ahaDB.reset()
  ahaDB.run()




