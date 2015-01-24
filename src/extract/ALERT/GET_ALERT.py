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




if __name__ == "__main__":
	
