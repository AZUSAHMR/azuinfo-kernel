#!/usr/bin/python
# -*- coding: utf8 -*-
from flask import Flask
from flask import Response
from flask import request
from azuinfo import mysqlConnect
from azuinfo import mysqlClose
from api import dict2jsonp
import json

CDN = "CDNDIR"
DEV = ["sdvx","popn"]

app = Flask(__name__)

@app.route("/사용자:<username>")
def userpage(username):
	output = {}

	output["username"] = username
	
	return Response(dict2jsonp(output,request.args.get("callback")) if request.args.get("callback") else json.dumps(output),mimetype="application/javascript" if request.args.get("callback") else "application/json",headers={"Access-Control-Allow-Origin": "*"})

@app.route("/<title>")
def redirect(title):
	output = {}

	output["title"] = title
	
	return Response(dict2jsonp(output,request.args.get("callback")) if request.args.get("callback") else json.dumps(output),mimetype="application/javascript" if request.args.get("callback") else "application/json",headers={"Access-Control-Allow-Origin": "*"})

@app.route("/<title>(<device>)")
def document(title,device):
	output = {}

	output["title"] = title
	output["device"] = device

	return Response(dict2jsonp(output,request.args.get("callback")) if request.args.get("callback") else json.dumps(output),mimetype="application/javascript" if request.args.get("callback") else "application/json",headers={"Access-Control-Allow-Origin": "*"})

if __name__ == "__main__":
	app.run(host="0.0.0.0",debug=True,port=5000,threaded=True)
