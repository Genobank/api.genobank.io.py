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

import cherrypy
import os

import json
import os
from libs import database
from dotenv import load_dotenv
from libs.dao import permitte_dao
from libs.service import permittee_service
import hmac




# from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
# from web3.contract import ConciseContract
# import math

from settings import settings

class AppUnoServer(object):
	def __init__(self):
		# self.db = database.database()
		permitte = permitte_dao.permittee_dao()
		self.permittee_service = permittee_service.permittee_service(permitte)
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
		return """
		<title>genobank.api</title>
		<h3>Genobank.io (TM)</h3>
		Permittee Creator API 
		"""+ os.getenv('MESSAGE')

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def create_permitee(self, id, address, secret):
		try:
			# create a web3 address object
			data = self.permittee_service.create_permittee(id, address, secret)

			# data = json.loads(data)
			# print(data)
			# file_name = self.geno_service.save_file_test(data, file)
			return data
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
			self.create_permitee(id, address, hash1.hexdigest())

			return hash1.hexdigest()
		except Exception as e:
			print(e)

			

class AppUno(object):
	def __init__(self):
		return None

	def start(self, port = 8080):
		conf = {
			'/static': {
				'tools.staticdir.on': True,
				'cors.expose.on': True,
				'tools.staticdir.dir': './public',
			},
			'/': {
				'tools.sessions.on': True,
				'server.socket_port': os.path.abspath(os.getcwd()),
				'response.timeout': False
			}

		}

		cherrypy.server.socket_host = '0.0.0.0'
		cherrypy.server.socket_port = port
		cherrypy.quickstart(AppUnoServer(), '/', conf)


# Avocado Blockchain Services at Merida, Yucatan
