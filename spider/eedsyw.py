# -*- coding:utf-8 -*- 
import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
print(sys.getdefaultencoding())
import json
import requests
import chardet
from bs4 import BeautifulSoup
import os
import datetime
import re
import time
import logging
import random
import calendar
import traceback

logging.basicConfig(filename='spider.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s') 
PLATEFORM='windows'
#PLATEFORM='linux'
# 假设你有一个Python字典
data = [
	{'root' : 'https://inews.nmgnews.com.cn/msxw/eeds/',
	'url': 'https://inews.nmgnews.com.cn/msxw/eeds/',
	'area': '内蒙古',
	'code': 'nmg-yw',
	'keyDic': 'us.dic',
	'id': 2}
]
pattern=r'<img\s.*?/img>'
pattern2=r'<img\s.*?/>'
gRoot=''
gOutRoot = ''
sections = "title,origin,published_time, content, del_flag,url"

#日期格式2024-01-01
def run(full_config,_config, date):
	global sections
	if PLATEFORM == 'linux':
		gRoot = r'/home/spider/'
	else:
		gRoot = r'E:\\'
	global gOutRoot
	gOutRoot = gRoot + 'out/'
	printInfo(gOutRoot)
	#dbConfig = getConfig(_config)
	# 目标网页的URL
	print(_config)
	url = _config['url']
	printInfo("begin capture")
	# 发送HTTP请求获取网页内容
	bStart = True
	response = requests.get(url)
	# 检查请求是否成功
	if response.status_code == 200:
		#print(response.text)
		printInfo(response.encoding)
		# 解析网页内容
		#网页内容为ISO-8859-1 解码为utf-8
		text = response.text.encode('ISO-8859-1').decode('UTF-8')
		#text = response.text.decode(response.encoding)
		#text = response.text
		soup = BeautifulSoup(text.replace('&nbsp;', ' '), "html.parser")
		#print(soup.original_encoding)
		printInfo("soup success")
		# 在这里添加你的爬虫逻辑
		# 例如，提取特定的元素或属性
		# 例如，提取所有的段落
		spdName = "爬取"+date+"-"+_config['code']
		result=[]
		#print(content_div)
		rows = soup.find('section',class_='text_list')
		#printInfo(rows)
		newsContent  =BeautifulSoup(str(rows).replace('&nbsp;', ' '), "html.parser")
		#printInfo(newsContent)
		#printInfo(len(newsContent.find_all("li")))
		#printInfo("after")
		if len(newsContent) <=0 :
			logging.info("***exception main")
			return
		#printInfo(len(soup.find_all('span',class_='homepage-recent')))
		db = full_config.getMysql()
		if db is None:
			db = full_config.getMysql()		
		for row in newsContent.find_all("li"):
			try:
				#print(row)
				#print(td_list)
				body = {}
				#print(td_list[2])
				print("==========")
				body['url'] =  row.a.attrs['href']
				body['name'] = row.a.text
				if _config['last'] is not None and _config['last'] == body['name']:
					printInfo("no new news")
					break
				printInfo(body)
				result.append(body)
				today = datetime.date.today()
				date_string = today.strftime("%Y-%m-%d")
				(dtl,content) = getDetail(body, _config)
				#print(dtl,content)
				row_id = db.insert_data('news_info', 
				sections,(body['name'], 
				"鄂尔多斯新闻", 
				body['date'],
				body['content'],'0', 
				body['url']))
				if row_id is not None:
					db.insert_data('news_label', 'news_id,label', (row_id, '鄂尔多斯'))					
				if bStart:
					db.update_data('web_list', "last='{}',update_date='{}'".format(body['name'],date_string), f"id={_config['id']}")	
					bStart = False
				printInfo("end capture one")
				'''
				with open(folder(_config['code']) + "/" + 'hk.txt', 'a', encoding='utf-8') as f:
					json.dump(result, f)
				'''
			except Exception as e:
				logging.info("***exception "+str(e))
				stack_trace = traceback.format_exc()
				print("stack_trace:", stack_trace)
	else:
		printInfo("request failed code:"+response.status_code)
	printInfo("end capture nmg")
def containsDic(_new):
	pass
def getDetail(body, _config):
	time.sleep(1)
	# 目标网页的URL
	printInfo("begin capture")
	# 发送HTTP请求获取网页内容
	printInfo("link is "+body['url'])
	response = requests.get(body['url'])
	printInfo("begin capture dtl")
	# 检查请求是否成功
	if response.status_code == 200:
		printInfo("request success")
		try:
			text = response.text.encode('ISO-8859-1').decode('UTF-8')
			soup = BeautifulSoup(text.replace('&nbsp;', ' '), "html.parser")
			info = soup.find('div',class_='article-infos')
			content = soup.find('div',class_='article-content')
			newsInfo  =BeautifulSoup(str(info).replace('&nbsp;', ' '), "html.parser")
			body['date'] = newsInfo.find('time', class_='date').text.replace("年", "-").replace("月", "-").replace("日", "")
			#for row in soup.find_all('tr',class_ =None):
			content_div = content.text
			#print(content_dtl.text)
			#so = BeautifulSoup(str(content_div), "html.parser")
			if PLATEFORM == 'linux':
				#nanoseconds = time.perf_counter()
				nanoseconds = calendar.timegm(time.gmtime())
			else:
				nanoseconds = time.time_ns()
			#for news in so.find_all("p"):
			#content = str(content_div)[str(content_div).find("<br/>")+5:-1].replace("<p>","").replace("<div>","").replace("</div","").replace("</div>","").replace("</p>","\r\n")
			content = str(content_div)
			content = re.sub(pattern,'',content)
			content = re.sub(pattern2,'',content)
			content = content.replace(">","")
			content = content.replace("\t","")
			#content = content.replace(" ","")
			content = content.replace("　","")
			content = content.replace("\n","")
			content = content.replace("\r","#")
			content = content.replace("				","")
			content = content.replace("##","")
			content = content.replace("#","-")
			content = content.replace("\r\r\n","\r\n")
			content = content.replace("***","\r")
			#printInfo(content)
			#content = content.replace("\r\r","")
			'''
			with open(folder(_config['code']) + "/" + str(nanoseconds) + 'aaa.txt', 'a', encoding='utf-8') as f:
				f.write(body['name']+"\r\n"+str(content_div))
			'''
			body['content']=content
			'''
			with open(folder(_config['code']) + "/" + str(nanoseconds) + '.txt', 'a', encoding='utf-8') as f:
				f.write(body['name']+"\r\n"+content)
			'''
		except Exception as e:
			stack_trace = traceback.format_exc()
			print("stack_trace:", stack_trace)
		printInfo("end capture dtl")
		return (folder(str(_config['code'])) + "/" + str(nanoseconds) + '.txt',content)
	else:
		print("request failed code:"+response.status_code)
def folder(prefix=''):
	global gOutRoot 
	today = datetime.date.today()
	date_string = today.strftime("%Y%m%d")
	folder_path = gOutRoot + date_string + '/' + prefix
	if not os.path.exists(folder_path):
		os.makedirs(folder_path)
		printInfo("create folder "+date_string)
	return folder_path
def getConfig(_config):
	sql = mysqlUtil.select_sql + str(_config['id'])
	result = mysqlUtil.qry(sql)
	return result
def test():
	body={'name':"test","link":"https://38.fsvps.gov.ru/news/upravlenie-rosselhoznadzora-informiruet-profilaktika-zaraznogo-uzelkovogo-dermatita-2/"}
	config={'code':'test'}
	getDetail(body,config)
def printInfo(msg):
	print(msg)
	logging.info(msg)
def errorInfo(msg):
	mysqlUtil.handleException(msg,__file__)
	logging.error(msg)
if __name__ == "__main__":
	printInfo("starting -----")
	#logging.info('arg1 is :', str(sys.argv[0])) 
	#test()
	if sys.argv[1] is None:
		sys.argv[1] = '2025-04-16'
	for item in data:
		printInfo("==== now id is "+str(item['id']))
		#run(item,str(sys.argv[1]))
		run(item,'2025-04-16')
