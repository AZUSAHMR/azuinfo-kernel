#!/usr/bin/python
# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
import redis
import requests
import pymysql
import uuid
import time
import json

class Session:
	def __init__(self,master="ac9547c7-8844-47ef-baaa-b1c57509d3b3",masterId="COURSEID"):
		self.r = redis.StrictRedis(host="localhost",port=6379,db=0,password="PASSWORD")
		self.MASTER = master
		self.MASTERID = masterId

	def getRequester(self):
		requester = requests.Session()
		adapter = requests.adapters.HTTPAdapter(max_retries=5)
		requester.mount("http://",adapter)
		requester.mount("https://",adapter)

		return requester

	def get(self,url,konamiId,post=None):
		cookie = self.r.get("cookie:%s" % konamiId)

		if cookie == None:
			return ""

		cookie = cookie.decode("UTF-8")

		with self.getRequester() as requester:
			if post == None:
				req = requester.get(url,cookies=requests.utils.cookiejar_from_dict({"M573SSID": cookie}),headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0"})
			else:
				req = requester.post(url,cookies=requests.utils.cookiejar_from_dict({"M573SSID": cookie}),headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0"},data=post)

		try:
			newCookie = requests.utils.dict_from_cookiejar(req.cookies)["M573SSID"]
		except:
			return ""
			
		data = req.content.decode("SHIFT-JIS","ignore")

		if cookie != newCookie:
			self.setCookie(newCookie,konamiId)

		return data

	def post(self,url,data,konamiId):
		return self.get(url,konamiId,data)

	def download(self,url,local,konamiId):
		cookie = self.r.get("cookie:%s" % konamiId)

		if cookie == None:
			return False

		with self.getRequester() as requester:
			req = requester.get(url,cookies=requests.utils.cookiejar_from_dict({"M573SSID": cookie.decode("UTF-8")}),headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0"})

		with open(local,"wb") as fp:
			for chunk in req.iter_content(chunk_size=1024):
				if chunk:
					fp.write(chunk)
					fp.flush()

		return True

	def setCookie(self,cookie,konamiId):
		expire = int(time.time())+28800
		session = self.r.get("session:%s" % konamiId).decode("UTF-8")

		self.r.set("cookie:%s" % konamiId,cookie)
		self.r.expireat("cookie:%s" % konamiId,expire)
		self.r.expireat("session:%s" % konamiId,expire)
		self.r.expireat("konamiId:%s" % session,expire)

	def validateSession(self,konamiId):
		data = self.get("http://p.eagate.573.jp/gate/p/mypage/index.html",konamiId)

		target = BeautifulSoup(data,"lxml").find("p",{"class": "id_text"})

		if target==None:
			self.removeSession(konamiId)
			return False

		return True

	def removeSession(self,konamiId):
		session = self.r.get("session:%s" % konamiId)

		self.r.delete("cookie:%s" % konamiId)
		self.r.delete("session:%s" % konamiId)

		if session:
			self.r.delete("konamiId:%s" % session.decode("UTF-8"))

	def appendSession(self,cookie,konamiId):
		session = self.r.get("session:%s" % konamiId)

		if session:
			self.r.delete("konamiId:%s" % session.decode("UTF-8"))

		session = str(uuid.uuid4())

		self.r.set("session:%s" % konamiId,session)
		self.r.set("konamiId:%s" % session,konamiId)

		self.setCookie(cookie,konamiId)

		return session

	def setMaster(self,cookie):
		self.r.set("session:%s" % self.MASTERID,self.MASTER)
		self.r.set("konamiId:%s" % self.MASTER,self.MASTERID)

		self.setCookie(cookie,self.MASTERID)

	def getUserdata(self,konamiId):
		db = mysqlConnect()
		cursor = db.cursor()
		cursor.execute("SELECT * FROM `azuinfo_user` WHERE `konamiId`=%s",(konamiId))
		chk = cursor.fetchone()
		cursor.close()
		db.close()

		return chk

	def getCard(self,konamiId):
		if self.validateSession(konamiId)==False:
			return False

		data = self.get("https://p.eagate.573.jp/gate/p/eapass/api/eapassinfo_json.html",konamiId)

		try:
			card = json.loads(data)
		except:
			return None

		return card["cardnumber"]

	def setRefreshdata(self,card,password,konamiId):
		user = self.getUserdata(konamiId)

		if user == None:
			return False

		key = "card:%d" % user[0]

		self.r.hset(key,"card",card)
		self.r.hset(key,"password",password)

		return True

	def getRefreshdata(self,konamiId):
		user = self.getUserdata(konamiId)

		if user == None:
			return False

		key = "card:%d" % user[0]

		if self.r.hgetall(key) == None:
			return False

		return {"card": self.r.hget(key,"card").decode("UTF-8"), "password": self.r.hget(key,"password").decode("UTF-8")}

	def delRefreshdata(self,konamiId):
		user = self.getUserdata(konamiId)

		if user == None:
			return False

		self.r.delete("card:%d" % user[0])

	def session2konamiId(self,session):
		konamiId = self.r.get("konamiId:%s" % session)

		if konamiId == None:
			return False

		return konamiId.decode("UTF-8")

def mysqlConnect():
	try:
		db = pymysql.connect(unix_socket="/var/run/mysqld/mysqld.sock",user="root",passwd="PASSWORD",db="azuinfo",charset="utf8",init_command="SET NAMES UTF8")
	except:
		return mysqlConnect()
	else:
		db.begin()
		return db

def mysqlClose(db,commit=None):
	if commit == True:
		db.commit()
	elif commit == False:
		db.rollback()

	db.close()
