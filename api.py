#!/usr/bin/python
# -*- coding: utf8 -*-
from flask import Flask
from flask import Response
from flask import request
from bs4 import BeautifulSoup
from azuinfo import Session
from azuinfo import mysqlConnect
from azuinfo import mysqlClose
import requests
import json
import re
import time
import hashlib

CDN = "CDNDIR"

app = Flask(__name__)
tools = Session()

def dict2jsonp(raw,callback):
	if callback==None:
		callback = "callback"

	return "%s(%s);" % (callback,json.dumps(raw))

@app.route("/userdata/konami/<cookie>.<returntype>")
def cookie2session(cookie,returntype):
	output = {}

	with tools.getRequester() as requester:
		req = requester.get("http://p.eagate.573.jp/gate/p/mypage/index.html",cookies=requests.utils.cookiejar_from_dict({"M573SSID": cookie}),headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0"})
	data = req.content.decode("SHIFT-JIS")
	konamiId = BeautifulSoup(data,"lxml").find("p",{"class": "id_text"})

	if konamiId == None:
		output = {"resCode": -1, "res": "Invalid Cookie"}
	else:
		konamiId = konamiId.get_text().strip()

		if konamiId == tools.MASTERID:
			tools.setMaster(cookie)
			session = tools.MASTER
		else:
			session = tools.appendSession(cookie,konamiId)

		user = tools.getUserdata(konamiId)

		if user == None:
			db = mysqlConnect()
			cursor = db.cursor()
			cursor.execute("INSERT INTO `azuinfo_user` (`konamiId`) VALUES (%s)",(konamiId))
			cursor.close()
			mysqlClose(db,True)

		output = {"resCode": 0, "res": "success", "konamiId": konamiId, "session": session}

	return Response(dict2jsonp(output,request.args.get("callback")) if returntype=="jsonp" else json.dumps(output),mimetype="application/javascript" if returntype=="jsonp" else "application/json",headers={"Access-Control-Allow-Origin": "*"})

@app.route("/userdata/<session>.<returntype>")
def session2userdata(session,returntype):
	output = {}

	konamiId = tools.session2konamiId(session)

	if konamiId == False:
		output = {"resCode": -2, "res": "Invalid Session"}
	else:
		user = tools.getUserdata(konamiId)

		output = {"resCode": 0, "res": "success", "konamiId": user[1], "nickname": user[2]}

	return Response(dict2jsonp(output,request.args.get("callback")) if returntype=="jsonp" else json.dumps(output),mimetype="application/javascript" if returntype=="jsonp" else "application/json",headers={"Access-Control-Allow-Origin": "*"})

@app.route("/userdata/eula/<session>.<returntype>")
def session2eula(session,returntype):
	output = {}

	konamiId = tools.session2konamiId(session)

	if konamiId == False:
		output = {"resCode": -2, "res": "Invalid Session"}
	else:
		user = tools.getUserdata(konamiId)

		output = {"resCode": 0, "res": "success"}

	return Response(dict2jsonp(output,request.args.get("callback")) if returntype=="jsonp" else json.dumps(output),mimetype="application/javascript" if returntype=="jsonp" else "application/json",headers={"Access-Control-Allow-Origin": "*"})
	
@app.route("/userdata/nickname/<session>.<returntype>",methods=["POST"])
def setNickname(session,returntype):
	output = {}

	konamiId = tools.session2konamiId(session)

	if konamiId == False:
		output = {"resCode": -2, "res": "Invalid Session"}
	else:
		user = tools.getUserdata(konamiId)

		nickname = request.form.get("nickname")
	
		if nickname == None:
			output = {"resCode": -3, "res": "Empty Nickname"}
		else:
			if re.match("^[A-Za-z0-9_]+$",nickname):
				db = mysqlConnect()
				cursor = db.cursor()
				cursor.execute("SELECT * FROM `azuinfo_user` WHERE `nickname`=%s",(nickname))
				chk = cursor.fetchone()
				cursor.close()
				
				if chk == None:
					cursor = db.cursor()
					cursor.execute("UPDATE `azuinfo_user` SET `nickname`=%s WHERE `id`=%s",(nickname,user[0]))
					cursor.close()
					mysqlClose(db,True)

					output = {"resCode": 0, "res": "success"}
				else:
					mysqlClose(db)

					output = {"resCode": -4, "res": "Already used Nickname"}

			else:
				output = {"resCode": -5, "res": "Invalid Nickname Form"}
			

	return Response(dict2jsonp(output,request.args.get("callback")) if returntype=="jsonp" else json.dumps(output),mimetype="application/javascript" if returntype=="jsonp" else "application/json",headers={"Access-Control-Allow-Origin": "*"})

@app.route("/playdata/<device>/<nickname>.<returntype>")
def getPlaydata(device,nickname,returntype):
	output = {}

	if re.match("^[A-Za-z0-9_]+$",nickname):
		db = mysqlConnect()
		cursor = db.cursor()
		cursor.execute("SELECT * FROM `azuinfo_user` WHERE `nickname`=%s",(nickname))
		chk = cursor.fetchone()
		cursor.close()

		if chk == None:
			output = {"resCode": -6, "res": "Invalid Nickname"}
		else:
			if device in ["sdvx","popn"]:
				code = hashlib.sha1(("%d_%s" % (chk[0],device)).encode("UTF-8")).hexdigest()

				try:
					with open("%s/%s/json/%s.json" % (CDN,device,code)) as fp:
						output = {"resCode": 0, "res": "success", "data": json.load(fp)}
				except:
					output = {"resCode": -7, "res": "No Data"}
			else:
				output  = {"resCode": -8, "res": "Invalid Device"}

	else:
		output = {"resCode": -5, "res": "Invalid Nickname Form"}

	return Response(dict2jsonp(output,request.args.get("callback")) if returntype=="jsonp" else json.dumps(output),mimetype="application/javascript" if returntype=="jsonp" else "application/json",headers={"Access-Control-Allow-Origin": "*"})

@app.route("/metadata/<device>.<returntype>")
def getMetadata(device,returntype):
	output = {}

	if device in ["sdvx","popn"]:
		output["data"] = {}

		if device=="sdvx":
			db = mysqlConnect()
			cursor = db.cursor()
			cursor.execute("SELECT * FROM `azuinfo_sdvx_song`")

			chk = cursor.fetchone()
			while chk!=None:
				output["data"][chk[1]] = {"title": chk[2], "artist": chk[3], "effector_nov": chk[4], "effector_adv": chk[5], "effector_exh": chk[6], "illustrator_nov": chk[9], "illustrator_adv": chk[10], "illustrator_exh": chk[11], "grv": chk[14], "nov": chk[15], "adv": chk[16], "exh": chk[17], "albumart_nov": chk[20], "albumart_adv": chk[21], "albumart_exh": chk[22]}

				if chk[14]!=None:
					output["data"][chk[1]]["effector_inf"] = chk[8]
					output["data"][chk[1]]["illustrator_inf"] = chk[13]
					output["data"][chk[1]]["inf"] = chk[19]
					output["data"][chk[1]]["albumart_inf"] = chk[24]
					
				if chk[18]!=None:
					output["data"][chk[1]]["effector_mxm"] = chk[7]
					output["data"][chk[1]]["illustrator_mxm"] = chk[12]
					output["data"][chk[1]]["mxm"] = chk[18]
					output["data"][chk[1]]["albumart_mxm"] = chk[23]

				chk = cursor.fetchone()

			cursor.close()
			mysqlClose(db)
		elif device=="popn":
			db = mysqlConnect()
			cursor = db.cursor()
			cursor.execute("SELECT * FROM `azuinfo_popn_song`")

			chk = cursor.fetchone()
			while chk!=None:
				output["data"][chk[1]] = {"title": chk[2], "genre": chk[3], "artist": chk[4], "easy": chk[5], "normal": chk[6], "hyper": chk[7], "ex": chk[8]}

				chk = cursor.fetchone()

			cursor.close()
			mysqlClose(db)
	else:
		output  = {"resCode": -8, "res": "Invalid Device"}

	return Response(dict2jsonp(output,request.args.get("callback")) if returntype=="jsonp" else json.dumps(output),mimetype="application/javascript" if returntype=="jsonp" else "application/json",headers={"Access-Control-Allow-Origin": "*"})

@app.route("/userdata/card/<session>.<returntype>")
def getCard(session,returntype):
	output = {}

	konamiId = tools.session2konamiId(session)

	if konamiId == False:
		output = {"resCode": -2, "res": "Invalid Session"}
	else:
		card = tools.getCard(konamiId)

		if card == False:
			output = {"resCode": -2, "res": "Invalid Session"}
		elif card == None:
			output = {"resCode": -9, "res": "No Card"}
		else:
			output = {"resCode": 0, "res": "success", "card": card}

	return Response(dict2jsonp(output,request.args.get("callback")) if returntype=="jsonp" else json.dumps(output),mimetype="application/javascript" if returntype=="jsonp" else "application/json",headers={"Access-Control-Allow-Origin": "*"})

@app.route("/userdata/refresh/<session>.<returntype>",methods=["POST"])
def requestRefresh(session,returntype):
	output = {}

	konamiId = tools.session2konamiId(session)

	if konamiId == False:
		output = {"resCode": -2, "res": "Invalid Session"}
	else:
		card = tools.getCard(konamiId)

		if card == False:
			output = {"resCode": -2, "res": "Invalid Session"}
		elif card == None:
			output = {"resCode": -9, "res": "No Card"}
		else:
			if card != request.form.get("card"):
				output = {"resCode": -10, "res": "Card Not Matched"}
			else:
				password = request.form.get("password")

				if password == None:
					password = ""

				if re.match("^[0-9]+$",password) and len(password)==4:
					device = request.form.get("device")

					if device == None:
						device = ""

					if re.match("^[0-9]+$",device):
						device = int(device)
						swap = 0

						if request.form.get("swap") == "1":
							swap = 1

						user = tools.getUserdata(konamiId)

						db = mysqlConnect()
						cursor = db.cursor()
						cursor.execute("SELECT * FROM `azuinfo_waiting` WHERE `owner`=%s ORDER BY `id` DESC LIMIT 0,1",(user[0]))
						chk = cursor.fetchone()
						cursor.close()
						mysqlClose(db)

						visit = False

						if chk == None:
							visit = True
						else:
							if chk[3] == 2:
								visit = True
							else:
								output = {"resCode": -11, "res": "Already Requested"}

						if visit:
							tools.setRefreshdata(card,password,konamiId)

							db = mysqlConnect()
							cursor = db.cursor()
							cursor.execute("INSERT INTO `azuinfo_waiting` (`owner`,`device`,`status`,`swap`,`request`) VALUES (%s,%s,0,%s,%s)",(user[0],device,swap,int(time.time())))
							cursor.close()
							mysqlClose(db,True)

							output = {"resCode": 0, "res": "success"}

					else:
						output = {"resCode": -12, "res": "Invalid Device Form"}	
				else:
					output = {"resCode": -13, "res": "Invalid Password Form"}

	return Response(dict2jsonp(output,request.args.get("callback")) if returntype=="jsonp" else json.dumps(output),mimetype="application/javascript" if returntype=="jsonp" else "application/json",headers={"Access-Control-Allow-Origin": "*"})

@app.route("/userdata/refresh/<session>.<returntype>")
def getHistory(session,returntype):
	output = {}

	konamiId = tools.session2konamiId(session)

	if konamiId == False:
		output = {"resCode": -2, "res": "Invalid Session"}
	else:
		user = tools.getUserdata(konamiId)

		if user == None:
			output = {"resCode": -2, "res": "Invalid Session"}
		else:
			db = mysqlConnect()
			cursor = db.cursor()
			cursor.execute("SELECT * FROM `azuinfo_waiting` WHERE `owner`=%s ORDER BY `id` DESC LIMIT 0,10" ,(user[0]))
			chk = cursor.fetchall()
			cursor.close()
			mysqlClose(db)

			output = {"resCode": 0, "res": "success", "data": []}

			for data in chk:
				output["data"].append({"id": data[0], "device": data[2], "status": data[3], "swap": data[4], "error": data[5], "request": data[6], "start": data[7], "end": data[8]})

	return Response(dict2jsonp(output,request.args.get("callback")) if returntype=="jsonp" else json.dumps(output),mimetype="application/javascript" if returntype=="jsonp" else "application/json",headers={"Access-Control-Allow-Origin": "*"})

if __name__ == "__main__":
	app.run(host="0.0.0.0",debug=True,port=5000,threaded=True)
