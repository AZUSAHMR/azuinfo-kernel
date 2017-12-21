#!/usr/bin/python
# -*- coding: utf8 -*
from azuinfo import Session
from azuinfo import mysqlConnect
from azuinfo import mysqlClose
import sys
import time
import os

tools = Session()

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

if __name__ == "__main__":
	while True:
		hour = time.localtime().tm_hour

		if hour>=4 and hour<8:
			time.sleep(300)
			continue

		db = mysqlConnect()
		cursor = db.cursor()
		cursor.execute("SELECT * FROM `azuinfo_waiting` WHERE `status`=0 AND `swap`=0 ORDER BY `id` ASC LIMIT 0,1")
		chk = cursor.fetchone()
		cursor.close()
		mysqlClose(db)

		if chk == None:
			time.sleep(1)
			continue

		db = mysqlConnect()
		cursor = db.cursor()
		cursor.execute("SELECT * FROM `azuinfo_user` WHERE `id`=%s",chk[1])
		user = cursor.fetchone()
		cursor.close()
		mysqlClose(db)

		updateStatus(chk[0],user[1],1)

		if tools.validateSession(user[1]) == False:
			updateStatus(chk[0],user[1],2,1)
			continue

		os.system("./parser %s %s %d" % (user[1],user[1],chk[2]))

		updateStatus(chk[0],user[1],2)