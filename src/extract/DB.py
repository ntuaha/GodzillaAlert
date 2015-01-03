# -*- coding: utf-8 -*-




#處理掉unicode 和 str 在ascii上的問題
import sys
import psycopg2



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
  def __init__(self,filepath,beta):
    f = open(filepath,'r')
    self.database = f.readline()[:-1]
    #改為測試用
    if beta==True:
      self.database = 'godzilla_alert_b'
    else:
      self.database = 'godzilla_alert'
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
