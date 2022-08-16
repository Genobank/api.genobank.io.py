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
from pathlib import Path
from libs import database
from libs.dao import permitte_dao
from libs.dao import test_permitte_dao
from libs.dao import genotype_dao
from libs.service import permittee_service
from libs.service import test_permittee_service
from libs.service import genotype_service
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
		test_permitte = test_permitte_dao.test_permittee_dao()
		genotype = genotype_dao.genotype_dao()
		self.permittee_service = permittee_service.permittee_service(permitte)
		self.test_permittee_service = test_permittee_service.test_permittee_service(test_permitte)
		self.genotype_service = genotype_service.genotype_service(genotype)
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
		if place == None or place == "test":
			t = self.mylookup.get_template("adminpage.mako")
			return t.render(plc = "AdminPage", env=os.getenv('ENVIROMENT'))
		elif place == "permittee" or place == "test-permittee":
			t = self.mylookup.get_template("adminpage.mako")
			return t.render(plc = "Permittee", env=os.getenv('ENVIROMENT'))
		elif place == "profile" or place == "test-profile":
			t = self.mylookup.get_template("profiles.mako")
			return t.render(plc = "Profiles", env=os.getenv('ENVIROMENT'))


	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def save_genotype(self, data, file):
		try:
			try:
				data = json.loads(data)
			except:
				raise Exception("'data' is not a json object")
			# print("\n\n\n\n",data,"\n\n\n\n")
			if "extension" not in data:
				raise Exception("This extension is not supported")
			return self.genotype_service.create(data, file)

		except Exception as e:
			msg = ""
			if 'message' in e.args[0]:
				msg = str(e.args[0]['message'])
			else:
				msg = str(e)
			raise cherrypy.HTTPError("500 Internal Server Error", msg)


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
	def create_permitee(self, id, address, secret, env):
		try:
			if env == "test":
				created = self.test_permittee_service.create_permittee(id, address, secret)
				return created
				# return self.permittee_service.create_permitee(id, address, secret)
			if env == "main":
				created = self.permittee_service.create_permittee(id, address, secret)
				return created
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
				# 'cors.expose.on': True,
				'tools.staticdir.dir': abspath('./public'),
			},
			'/js': {
				'tools.staticdir.on': True,
				# 'cors.expose.on': True,
				'tools.staticdir.dir': abspath('./public/pages/js'),
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
