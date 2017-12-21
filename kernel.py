#!/usr/bin/python
# -*- coding: utf8 -*
from azuinfo import Session
from azuinfo import mysqlConnect
from azuinfo import mysqlClose
from bs4 import BeautifulSoup
import tweepy
import sys
import time
import os

auth = tweepy.OAuthHandler("","")
auth.set_access_token("","")
api = tweepy.API(auth)
tools = Session()

def uploadNotify():
	api.update_status("@ 세션이 만료되었어요~ (%d)" % int(time.time()))

def updateStatus(no,konamiId,status,error=None):
	db = mysqlConnect()
	cursor = db.cursor()

	if error == None:
		cursor.execute("UPDATE `azuinfo_waiting` SET `status`=%s WHERE `id`=%s",(status,no))
	else:
		cursor.execute("UPDATE `azuinfo_waiting` SET `status`=%s, `error`=%s WHERE `id`=%s",(status,error,no))

	cursor.close()
	mysqlClose(db,True)

	if status == 1 or status==2:
		target = "start"

		if status==2:
			target = "end"

		db = mysqlConnect()
		cursor = db.cursor()
		cursor.execute("UPDATE `azuinfo_waiting` SET `"+target+"`=%s WHERE `id`=%s",(int(time.time()),no))
		cursor.close()
		mysqlClose(db,True)

	if status==2:
		tools.delRefreshdata(konamiId)

def detachCard(card,konamiId):
	raw = tools.get("http://p.eagate.573.jp/gate/p/eamusement/detach/index.html",konamiId)

	if raw.find(card)==-1:
		return False

	raw = tools.get("http://p.eagate.573.jp/gate/p/eamusement/detach/setting1.html?ucdto=%s" % card,konamiId)
	html = BeautifulSoup(raw,"lxml")

	for tmp in html.findAll("a"):
		if tmp.get_text().strip()==u"確認して切り離す":
			url = "http://p.eagate.573.jp%s" % (tmp.get("href"))
			req = tools.get(url,konamiId)
			return True

	return False

def attachCard(card,card_pass,konamiId):
	raw = tools.get("https://p.eagate.573.jp/gate/p/eamusement/attach/index.html",konamiId)

	if len(raw)==0:
		return False

	html = BeautifulSoup(raw,"lxml")

	form = html.find("form",action="end.html")

	data = {
		"token_value": form.contents[1].get("value"),
		"ucd": card,
		"pass": card_pass,
		"snsid": form.contents[8].get("value")
	}

	if raw.find(u"PASELI利用設定")!=-1:
		data["ecprop"] = 2

	raw = tools.post("https://p.eagate.573.jp/gate/p/eamusement/attach/end.html",data,konamiId)

	if raw.find(u"e-AMUSEMENT PASSの新規登録が完了しました。")==-1:
		return False
	else:
		return True

if __name__ == "__main__":
	lastReq = 0

	while True:
		hour = time.localtime().tm_hour

		if hour>=4 and hour<8:
			time.sleep(300)
			continue

		db = mysqlConnect()
		cursor = db.cursor()
		cursor.execute("SELECT * FROM `azuinfo_waiting` WHERE `status`=0 AND `swap`=1 ORDER BY `id` ASC LIMIT 0,1")
		chk = cursor.fetchone()
		cursor.close()
		mysqlClose(db)

		if chk == None:
			if lastReq+300<=int(time.time()):
				if tools.validateSession(tools.MASTERID) == False:
					uploadNotify()
					sys.exit()
				else:
					lastReq = int(time.time())

			time.sleep(1)
			continue

		if tools.validateSession(tools.MASTERID) == False:
			uploadNotify()
			sys.exit()

		db = mysqlConnect()
		cursor = db.cursor()
		cursor.execute("SELECT * FROM `azuinfo_user` WHERE `id`=%s",chk[1])
		user = cursor.fetchone()
		cursor.close()
		mysqlClose(db)

		updateStatus(chk[0],user[1],1)

		card = tools.getRefreshdata(user[1])

		if detachCard(card["card"],user[1]) == False:
			updateStatus(chk[0],user[1],2,1)
			continue

		if attachCard(card["card"],card["password"],tools.MASTERID) == False:
			updateStatus(chk[0],user[1],2,2)
			continue

		os.system("./parser %s %s %d" % (tools.MASTERID,user[1],chk[2]))

		if detachCard(card["card"],tools.MASTERID) == False:
			updateStatus(chk[0],user[1],2,3)
			continue

		if tools.validateSession(user[1]) == False:
			updateStatus(chk[0],user[1],2,4)
			continue

		if attachCard(card["card"],card["password"],user[1]) == False:
			updateStatus(chk[0],user[1],2,5)
			continue

		updateStatus(chk[0],user[1],2)
