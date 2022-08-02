# -*- coding: UTF-8 -*-
#
# MODULE: runweb || CherryPy Server
# FILE: runweb.py
# USE: python3 start.py (at root directory)
#
#> @author
#> Francisco Tun
#
#  DESCRIPTION:
#> This is the main script for the Creator of Permittees for Genobank.io.  (Genobank.io),
# is intended to work within the blockchain network.
#
# REVISION HISTORY:
#
# 14 July 2022 - Initial Version
# -- -- 2022 - Final Version
#
# MODIFICATIONS:
#
# Initial mod. version: --------
# Final mod. version:   --------
#
# TODO_dd_mmm_yyyy - TODO_describe_appropriate_changes - TODO_name
#--------------------------------------------------------------------------

from email import message
from dotenv import load_dotenv
from libs import database
from libs.dao import permitte_dao
from libs.service import permittee_service
from mako.template import Template
from mako.lookup import TemplateLookup
from math import perm
from os.path import abspath

# import ServerAdapter
from cherrypy import wsgi


import cherrypy
import hmac
import json
import os

# from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
# from web3.contract import ConciseContract
# import math

from settings import settings

class AppUnoServer(object):
	def __init__(self):
		# self.db = database.database()
		permitte = permitte_dao.permittee_dao()
		self.permittee_service = permittee_service.permittee_service(permitte)
		self.mylookup = TemplateLookup(directories=['public/pages'])
		return None

	load_dotenv()

	def jsonify_error(status, message, traceback, version):
		return json.dumps({'status': 'Failure', 'status_details': {
			'message': status,
			'description': message
		}})

	_cp_config = {"error_page.default": jsonify_error}

	def CORS():
		if cherrypy.request.method == 'OPTIONS':
			cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
			cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
			cherrypy.response.headers['Access-Control-Allow-Origin']  = '*'
			return True
		else:
			cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
	
	cherrypy.tools.CORS = cherrypy._cptools.HandlerTool(CORS)

	#Methods -------------------------------------------------------------------
	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	def index(self):
		t = Template(filename="public/pages/index.mako")
		return t.render(message=os.getenv('ENVIROMENT'))


	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['GET'])
	def adminpage(self, place=None):
		# print("\n\nplace: " + place+"\n\n")
		if place == None:
			t = self.mylookup.get_template("adminpage.mako")
			return t.render(plc = "AdminPage", env=os.getenv('ENVIROMENT'))
		elif place == "permittee":
			t = self.mylookup.get_template("adminpage.mako")
			return t.render(plc = place, env=os.getenv('ENVIROMENT'))
		elif place == "profiles":
			t = self.mylookup.get_template("profiles.mako")
			return t.render(plc = place, env=os.getenv('ENVIROMENT'))


	# @cherrypy.expose
	# @cherrypy.config(**{'tools.CORS.on': True})
	# @cherrypy.tools.allow(methods=['GET'])
	# def profiles(self):
	# 	t = self.mylookup.get_template("profiles.mako")
	# 	return t.render(place = "Profiles", env=os.getenv('ENVIROMENT'))


	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def create_permitee(self, id, address, secret):
		try:
			created, msg = self.permittee_service.create_permittee(id, address, secret)
			return msg
		except :
			raise

	
	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def delete_permittee(self, id):
		try:
			deleted = self.permittee_service.delete_permittee(id)
			return True
		except Exception as e:
			print(e)


	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def create_experimental_permitee(self, id, address, secret):
		try:
			message=id+address
			hash1 = hmac.new(secret.encode('utf-8'),msg=message.encode(), digestmod="sha256")
			permittee = self.permittee_service.create_permittee(id, address, hash1.hexdigest())
			return {"created_id":str(permittee)}
		except Exception as e:
			msg = ""
			if 'message' in e.args[0]:
				msg = str(e.args[0]['message'])
			else:
				msg = str(e)
			raise cherrypy.HTTPError("500 Internal Server Error", msg)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def testing_db(self):
		try:
			return self.permittee_service.testing_mongo_db()
		except Exception as e:
			print(e)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def search_all_by_table(self, table=None):
		try:
			return self.permittee_service.find_all_by_table(table)
		except Exception as e:
			print(e)

			# addition

class AppUno(object):
	def __init__(self):
		return None

	def start(self, port = 8080):
		CONF = {
			'/static': {
				'tools.staticdir.on': True,
				'cors.expose.on': True,
				'tools.staticdir.dir': abspath('./public'),
			},
			'/': {
				'tools.sessions.on': True,
				'server.socket_port': os.path.abspath(os.getcwd()),
				'response.timeout': False
			},
		}

		cherrypy.server.socket_host = '0.0.0.0'
		cherrypy.server.socket_port = port
		cherrypy.quickstart(AppUnoServer(), '/', CONF)


# Avocado Blockchain Services at Merida, Yucatan
