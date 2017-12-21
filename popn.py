#!/usr/bin/python
# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
from azuinfo import Session
from azuinfo import mysqlConnect
from azuinfo import mysqlClose
import sys
import re
import hashlib
import json
import uuid

diff_db = ["easy","normal","hyper","ex"]
diff_full = ["EASY","NORMAL", "HYPER", "EX"]

CDN = "CDNDIR"

tools = Session()

if __name__ == "__main__":
	konamiId = sys.argv[1]
	outputId = sys.argv[2]

	if tools.validateSession(konamiId) == False:
		sys.exit()

	userdata = tools.getUserdata(konamiId)
	outuserdata = tools.getUserdata(outputId)

	output = {}
	output["api"] = {}
	output["user"] = {}
	output["song"] = {}
	output["db"] = {}

	output["api"]["etag"] = str(uuid.uuid4())
	output["api"]["cdn"] = "cdn.azu.kr"
	output["api"]["id"] = hashlib.sha1(("%d_popn" % outuserdata[0]).encode("UTF-8")).hexdigest()

	profile_src = tools.get("http://p.eagate.573.jp/game/popn/eclale/p/playdata/index.html",konamiId)

	if profile_src.find(u"このコンテンツの閲覧には『pop'n music &eacute;clale』のプレーデータが必要です。")!=-1:
		sys.exit()
	if profile_src.find(u"ご利用にはeAMUSEMENTへのログインが必要です")!=-1:
		sys.exit()

	profile = BeautifulSoup(profile_src,"html.parser")

	output["user"]["name"] = profile.find("div",{"id": "status_table"}).contents[3].contents[2].get_text()
	output["user"]["img"] = "/popn/character/%s.png" % output["api"]["id"]
	output["user"]["character"] = profile.find("div",{"id": "status_table"}).contents[3].contents[12].get_text()
	output["user"]["lumina"] = int(profile.find("div",{"id": "status_table"}).contents[3].contents[22].get_text())
	output["user"]["normal"] = int(profile.find("div",{"id": "status_table"}).contents[3].contents[32].get_text())
	output["user"]["battle"] = int(profile.find("div",{"id": "status_table"}).contents[3].contents[37].get_text())
	output["user"]["special"] = int(profile.find("div",{"id": "status_table"}).contents[3].contents[42].get_text())
	output["user"]["time"] = profile.find("div",{"id": "status_table"}).contents[3].contents[47].get_text()

	if tools.download("http://p.eagate.573.jp/game/popn/eclale/p%s" % profile.find("div",{"class": "fpass_img"}).get("style")[17:][:-40],"%s%s" % (CDN,output["user"]["img"]),konamiId) == False:
		output["user"]["img"] = "/system/apcard_fail.png"

	cnt = 0
	detail_list = {}
	artist_list = {}
	
	for level in range(50,0,-1):
		for page in range(0,100):
			table_src = tools.get("http://p.eagate.573.jp/game/popn/eclale/p/playdata/mu_lv.html?page=%d&level=%d" % (page,level),konamiId)

			if table_src.find(u"データがありません｡")!=-1:
				break
			if table_src.find(u"ご利用にはeAMUSEMENTへのログインが必要です")!=-1:
				sys.exit()
			if table_src.find(u"このコンテンツの閲覧には『pop'n music &eacute;clale』のプレーデータが必要です。")!=-1:
				sys.exit()
			if table_src.find(u"このサービスはe-AMUSEMENT ベーシックコース(月額324円)の加入が必要です。")!=-1:
				sys.exit()
			
			table = BeautifulSoup(table_src,"html.parser")

			breaker = cnt

			for song in table.findAll("li"):
				if len(song.contents)!=11:
					continue
				if len(song.contents[1])!=4:
					continue

				title = song.contents[1].contents[0].contents[0].strip()
				genre = song.contents[1].contents[3].get_text().strip()
				uniq = hashlib.sha1(("%s/%s" % (title,genre)).encode("UTF-8")).hexdigest()

				while True:
					db = mysqlConnect()
					cursor = db.cursor()
					cursor.execute("SELECT * FROM `azuinfo_popn_song` WHERE `uniq`=%s",(uniq))
					chk = cursor.fetchone()
					cursor.close()

					if chk==None:
						cursor = db.cursor()
						cursor.execute("INSERT INTO `azuinfo_popn_song` (`uniq`,`title`,`genre`) VALUES (%s,%s,%s)",(uniq,title,genre))
						cursor.close()
						mysqlClose(db,True)
					else:
						mysqlClose(db)
						break

				diff = song.contents[3].get_text().strip()
				score = int(song.contents[7].contents[2])
				meda = "l"

				if score!=0:
					try:
						meda = song.contents[7].contents[0].get("src")[:-4][28:]
					except:
						pass

					detail_list[uniq] = song.contents[1].contents[0].get("href")

					if chk[4]==None:
						artist_list[uniq] = True
					else:
						artist_list[uniq] = False

				for i in range(4):
					if diff_full[i]==diff:
						if chk[5+i]==None:
							db = mysqlConnect()
							cursor = db.cursor()
							cursor.execute("UPDATE `azuinfo_popn_song` SET `"+diff_db[i]+"`=%s WHERE `id`=%s",(level,chk[0]))
							cursor.close()
							mysqlClose(db,True)

						if score!=0:
							if uniq not in output["song"]:
								output["song"][uniq] = {}

							output["song"][uniq][diff_db[i]] = {}
							output["song"][uniq][diff_db[i]]["score"] = score
							output["song"][uniq][diff_db[i]]["meda"] = meda

						break

				cnt+=1

			if breaker==cnt:
				break

	for uniq in detail_list:
		detail_src = tools.get("http://p.eagate.573.jp%s" % detail_list[uniq],konamiId)

		detail = BeautifulSoup(detail_src,"html.parser")

		if artist_list[uniq] == True:
			db = mysqlConnect()
			cursor = db.cursor()
			cursor.execute("UPDATE `azuinfo_popn_song` SET `artist`=%s WHERE `uniq`=%s",(detail.find("div",{"id": "artist"}).get_text().strip(),uniq))
			cursor.close()
			mysqlClose(db,True)

		db = mysqlConnect()
		cursor = db.cursor()
		cursor.execute("SELECT * FROM `azuinfo_popn_song` WHERE `uniq`=%s",(uniq))
		chk = cursor.fetchone()
		cursor.close()
		mysqlClose(db)

		output["db"][chk[1]] = {"title": chk[2], "genre": chk[3], "artist": chk[4]}

		for i in range(4):
			info = detail.find("div",{"id": diff_db[i], "class": "dif_tbl"})

			if info==None:
				continue

			if diff_db[i] not in output["song"][uniq]:
				continue


			output["song"][uniq][diff_db[i]]["judge"] = {}
			output["song"][uniq][diff_db[i]]["judge"]["cool"] = int(info.contents[1].contents[1].contents[5].contents[1].get_text().replace("-","0"))
			output["song"][uniq][diff_db[i]]["judge"]["great"] = int(info.contents[1].contents[1].contents[7].contents[1].get_text().replace("-","0"))
			output["song"][uniq][diff_db[i]]["judge"]["good"] = int(info.contents[1].contents[1].contents[9].contents[1].get_text().replace("-","0"))
			output["song"][uniq][diff_db[i]]["judge"]["bad"] = int(info.contents[1].contents[1].contents[11].contents[1].get_text().replace("-","0"))

			output["song"][uniq][diff_db[i]]["cnt"] = {}
			output["song"][uniq][diff_db[i]]["cnt"]["highlight"] = int(info.contents[1].contents[1].contents[13].contents[1].get_text()[:-1].replace("-","0"))
			output["song"][uniq][diff_db[i]]["cnt"]["play"] = int(info.contents[1].contents[1].contents[15].contents[1].get_text()[:-1].replace("-","0"))
			output["song"][uniq][diff_db[i]]["cnt"]["clear"] = int(info.contents[1].contents[1].contents[17].contents[1].get_text()[:-1].replace("-","0"))
			output["song"][uniq][diff_db[i]]["cnt"]["fc"] = int(info.contents[1].contents[1].contents[19].contents[1].get_text()[:-1].replace("-","0"))
			output["song"][uniq][diff_db[i]]["cnt"]["perfect"] = int(info.contents[1].contents[1].contents[21].contents[1].get_text()[:-1].replace("-","0"))

			if chk[i+5]!=None:
				output["db"][chk[1]][diff_db[i]] = chk[i+5]

	fp = open("%s/popn/json/%s.json" % (CDN,output["api"]["id"]) ,"w")
	fp.write(json.dumps(output))
	fp.close()
