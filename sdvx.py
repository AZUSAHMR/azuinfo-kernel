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

diff_db = ["nov","adv","exh","mxm","inf"]
diff_full = ["novice","advanced","exhaust","maximum","infinite"]

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
	output["api"]["id"] = hashlib.sha1(("%d_sdvx" % outuserdata[0]).encode("UTF-8")).hexdigest()

	profile_src = tools.get("http://p.eagate.573.jp/game/sdvx/iv/p/playdata/profile/index.html",konamiId)

	if profile_src.find(u"このコンテンツの閲覧には『SOUND VOLTEX IV HEAVENLY HAVEN』のプレーデータが必要です。")!=-1:
		sys.exit()
	if profile_src.find(u"このページのご利用にはeAMUSEMENT へのログインが必要です。")!=-1:
		sys.exit()

	profile = BeautifulSoup(profile_src,"html.parser")

	output["user"]["name"] = profile.find("div",{"id": "name_str"}).get_text()
	output["user"]["play"] = int(re.sub("[^0-9]*","",profile.find("li",{"id": "playnum"}).get_text()[:-1]))
	output["user"]["packet"] = int(re.sub("[^0-9]*","",profile.find("li",{"id": "packet"}).get_text()[:-2]))
	output["user"]["block"] = int(re.sub("[^0-9]*","",profile.find("li",{"id": "block"}).get_text()[:-3]))
	output["user"]["skill_name"] = profile.find("li",{"id": "skil"}).contents[0].get_text()
	output["user"]["apcard"] = "/sdvx/apcard/%s.png" % output["api"]["id"]

	if tools.download("http://p.eagate.573.jp%s" % profile.find("div",{"id": "apcard"}).contents[0].get("src"),"%s%s" % (CDN,output["user"]["apcard"]),konamiId) == False:
		output["user"]["apcard"] = "/system/apcard_fail.png"

	if profile.find("li",{"id": "skil"}).contents[0].get("id") == "skill_inf":
		output["user"]["skill_no"] = 12
	else:
		try:
			output["user"]["skill_no"] = int(re.sub("[^0-9]*","",profile.find("li",{"id": "skil"}).contents[0].get("id")))
		except:
			output["user"]["skill_no"] = -1

	for page in range(1,100):
		table_src = tools.get("http://p.eagate.573.jp/game/sdvx/iv/p/playdata/musicdata/index.html?page=%d&sort=0" % page,konamiId)

		if table_src.find(u"このページのご利用にはeAMUSEMENT へのログインが必要です。")!=-1:
			sys.exit()
		if table_src.find(u"このコンテンツの閲覧には『SOUND VOLTEX IV HEAVENLY HAVEN』のプレーデータが必要です。")!=-1:
			sys.exit()
		if table_src.find(u"このサービスはe-AMUSEMENT ベーシックコース(月額324円)の加入が必要です｡")!=-1:
			sys.exit()
		if table_src.find(u"データがありません。")!=-1:
			break
			
		table = BeautifulSoup(table_src,"html.parser")

		for song in table.findAll("tr",{"class": "data_col"}):
			title = song.contents[1].contents[0].get_text().strip()
			artist = song.contents[1].contents[1].get_text().strip()
			uniq = hashlib.sha1(("%s/%s" % (title,artist)).encode("UTF-8")).hexdigest()
			
			output["song"][uniq] = {}

			while True:
				db = mysqlConnect()
				cursor = db.cursor()
				cursor.execute("SELECT * FROM `azuinfo_sdvx_song` WHERE `uniq`=%s",(uniq))
				chk = cursor.fetchone()
				cursor.close()
				
				if chk==None:
					cursor = db.cursor()
					cursor.execute("INSERT INTO `azuinfo_sdvx_song` (`uniq`,`title`,`artist`) VALUES (%s,%s,%s)",(uniq,title,artist))
					cursor.close()
					mysqlClose(db,True)
				else:
					mysqlClose(db)
					break

			for i in range(5):
				output["song"][uniq][diff_db[i]] = {}
				
				if song.contents[3+i*2].contents[0]!="-":
					raw = str(song.contents[3+i*2])
					
					if raw.find("rival_mark_per.png")!=-1:
						clear = 4
					elif raw.find("rival_mark_uc.png")!=-1:
						clear = 3
					elif raw.find("rival_mark_comp_ex.png")!=-1:
						clear = 2
					elif raw.find("rival_mark_comp.png")!=-1:
						clear = 1
					else:
						clear = 0

					if raw.find("rival_grade_d.png")!=-1:
						rank = 0
					elif raw.find("rival_grade_c.png")!=-1:
						rank = 1
					elif raw.find("rival_grade_b.png")!=-1:
						rank = 2
					elif raw.find("rival_grade_a.png")!=-1:
						rank = 3
					elif raw.find("rival_grade_a_plus.png")!=-1:
						rank = 4
					elif raw.find("rival_grade_aa.png")!=-1:
						rank = 5
					elif raw.find("rival_grade_aa_plus")!=-1:
						rank = 6
					elif raw.find("rival_grade_aaa.png")!=-1:
						rank = 7
					elif raw.find("rival_grade_aaa_plus.png")!=-1:
						rank = 8
					elif raw.find("rival_grade_s.png")!=-1:
						rank = 9

					output["song"][uniq][diff_db[i]]["clear"] = clear
					output["song"][uniq][diff_db[i]]["rank"] = rank

			failcnt = 0
			
			while True:
				detail_src = tools.get("http://p.eagate.573.jp%s" % song.contents[1].contents[0].contents[1].get("href"),konamiId)
				detail = BeautifulSoup(detail_src,"html.parser")

				if len(detail_src)==0:
					sys.exit()
				if detail.find("div",{"id": diff_full[0], "class": "music_box"}):
					break

				failcnt += 1

				if failcnt==5:
					sys.exit()

			for i in range(5):
				info = detail.find("div",{"id": diff_full[i], "class": "music_box"})
				
				if info==None:
					continue
				
				if chk[i+15]==None:
					src = info.contents[9].get("src")
					dst = "/sdvx/albumart/%s_%s.jpg" % (uniq,diff_db[i])
					
					if tools.download("http://p.eagate.573.jp%s" % src,"%s%s" % (CDN,dst),konamiId) == True:
						effector = info.contents[3].get_text()[12:]
						illustrator = info.contents[5].get_text()[15:]
						
						db = mysqlConnect()
						cursor = db.cursor()
						cursor.execute("UPDATE `azuinfo_sdvx_song` SET `"+diff_db[i]+"`=%s, `albumart_"+diff_db[i]+"`=%s, `effector_"+diff_db[i]+"`=%s, `illustrator_"+diff_db[i]+"`=%s WHERE `id`=%s",(int(info.contents[1].get_text()),dst,effector,illustrator,chk[0]))
						cursor.close()
						mysqlClose(db,True)

						if i==4:
							grv = 0

							if info.contents[1].get("id")=="diff_gra":
								grv = 1
							elif info.contents[1].get("id")=="diff_hvn":
								grv = 2

							db = mysqlConnect()
							cursor = db.cursor()
							cursor.execute("UPDATE `azuinfo_sdvx_song` SET `grv`=%s WHERE `id`=%s",(grv,chk[0]))
							cursor.close()
							mysqlClose(db,True)

						db = mysqlConnect()
						cursor = db.cursor()
						cursor.execute("SELECT * FROM `azuinfo_sdvx_song` WHERE `id`=%s",(chk[0]))
						chk = cursor.fetchone()
						cursor.close()
						mysqlClose(db)
				
				
				score = int(info.contents[7].contents[1].contents[1].contents[1].get_text().replace("--","0"))
				play = int(info.contents[7].contents[1].contents[3].contents[1].get_text()[:-1].replace("--","0"))
				clear = int(info.contents[7].contents[1].contents[5].contents[1].get_text()[:-1].replace("--","0"))
				ultimate = int(info.contents[7].contents[1].contents[7].contents[1].get_text()[:-1].replace("--","0"))
				perfect = int(info.contents[7].contents[1].contents[9].contents[1].get_text()[:-1].replace("--","0"))
				oldscore = int(info.contents[7].contents[1].contents[11].contents[1].get_text().replace("--","0"))
				oldplay = int(info.contents[7].contents[1].contents[13].contents[1].get_text()[:-1].replace("--","0"))
				oldclear = int(info.contents[7].contents[1].contents[15].contents[1].get_text()[:-1].replace("--","0"))
				oldultimate = int(info.contents[7].contents[1].contents[17].contents[1].get_text()[:-1].replace("--","0"))
				oldperfect = int(info.contents[7].contents[1].contents[19].contents[1].get_text()[:-1].replace("--","0"))

				output["song"][uniq][diff_db[i]]["score"] = score
				output["song"][uniq][diff_db[i]]["cnt"] = {}
				output["song"][uniq][diff_db[i]]["cnt"]["play"] = play
				output["song"][uniq][diff_db[i]]["cnt"]["clear"] = clear
				output["song"][uniq][diff_db[i]]["cnt"]["ultimate"] = ultimate
				output["song"][uniq][diff_db[i]]["cnt"]["perfect"] = perfect
				output["song"][uniq][diff_db[i]]["oldscore"] = oldscore
				output["song"][uniq][diff_db[i]]["oldcnt"] = {}
				output["song"][uniq][diff_db[i]]["oldcnt"]["play"] = play
				output["song"][uniq][diff_db[i]]["oldcnt"]["clear"] = clear
				output["song"][uniq][diff_db[i]]["oldcnt"]["ultimate"] = ultimate
				output["song"][uniq][diff_db[i]]["oldcnt"]["perfect"] = perfect

			output["db"][chk[1]] = {"title": chk[2], "artist": chk[3], "grv": chk[14]}

			for i in range(5):
				if chk[i+15]==None:
					continue
					
				output["db"][chk[1]][diff_db[i]] = chk[i+15]
				output["db"][chk[1]]["albumart_%s" % diff_db[i]] = chk[i+20]

	fp = open("%s/sdvx/json/%s.json" % (CDN,output["api"]["id"]) ,"w")
	fp.write(json.dumps(output))
	fp.close()
