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

from logging import raiseExceptions
import cherrypy
from cherrypy.lib import static

import json
import uuid
import os


# from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
# from web3.contract import ConciseContract
# import math

from settings import settings

class AppUnoServer(object):

	def __init__(self):

		return None

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
		return "Genobank.io (TM) Permittee Creator API"

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def create_permitee(self, data, file=None):
		try:
			data = json.loads(data)
			# file_name = self.geno_service.save_file_test(data, file)
			return {"data" : data, "file_name" : file}
		except Exception:
			raiseExceptions



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
				'response.timeout' : False
			}
		}

		cherrypy.server.socket_host = '0.0.0.0'
		cherrypy.server.socket_port= port
		cherrypy.quickstart(AppUnoServer(), '/', conf)


# Avocado Blockchain Services at Merida, Yucatan
