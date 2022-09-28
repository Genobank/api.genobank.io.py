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
import random
from unicodedata import name
from dotenv import load_dotenv
from cryptography.fernet import Fernet
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
from cherrypy import wsgi
from cherrypy.process.plugins import Daemonizer
import cherrypy
import hmac
import json
import os


class AppUnoServer(object):
	def __init__(self):
		permitte = permitte_dao.permittee_dao()
		test_permitte = test_permitte_dao.test_permittee_dao()
		genotype = genotype_dao.genotype_dao()
		self.permittee_service = permittee_service.permittee_service(permitte)
		self.test_permittee_service = test_permittee_service.test_permittee_service(test_permitte)
		self.genotype_service = genotype_service.genotype_service(genotype)
		self.mylookup = TemplateLookup(directories=['public/pages'])

		# delete despues
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
			cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE'
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
			if "extension" not in data:
				raise Exception("This extension is not supported")
			self.genotype_service.validate_consents_metadata(data)
			# return {"harcodedhash":"this is only hardcoded test", "token":"0x987fy9sduf9sduyf98sdufshd9fhsdifhsid"}
			return self.genotype_service.create(data, file)
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
	def upload_file_to_bucket(self,):
		return self.genotype_service.upload_file_to_bucket()


	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def test_process_1(self, data):
		try:
			data = json.loads(data)
			if "extension" not in data:
				raise Exception("This extension is not supported")
			self.genotype_service.validate_consents_metadata(data)
			return self.genotype_service.mint_nft(data)
		except:
			raise

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def test_process_2(self, data):
		try:
			try:
				data = json.loads(data)
			except:
				raise Exception("'data' is not a json object")
			if "extension" not in data:
				raise Exception("This extension is not supported")
			self.genotype_service.validate_consents_metadata(data)
			return self.genotype_service.save_db_file(data)
		except:
			raise

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def test_process_3(self, data, file):
		try:
			try:
				data = json.loads(data)
			except:
				raise Exception("'data' is not a json object")
			if "extension" not in data:
				raise Exception("This extension is not supported")
			self.genotype_service.validate_consents_metadata(data)
			data["key"] = bytes(data["key"],  'utf-8')
			return self.genotype_service.storage_file(data, file)
		# except:
		# 	raise
		except Exception as e:
			msg = ""
			if 'message' in e.args[0]:
				msg = str(e.args[0]['message'])
			else:
				msg = str(e)
			raise cherrypy.HTTPError("500 Internal Server Error", msg)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['GET'])
	@cherrypy.tools.json_out()
	def get_serial_permittee_by_address(self, address):
		return self.test_permittee_service.get_serial_from_address(address)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['GET'])
	@cherrypy.tools.json_out()
	def find_file(self, owner):
		try:
			file_data = self.genotype_service.find_by_owner(owner)
			return self.genotype_service.basic_reference(file_data)
		except Exception as e:
			msg = ""
			if 'message' in e.args[0]:
				msg = str(e.args[0]['message'])
			else:
				msg = str(e)
			raise cherrypy.HTTPError("500 Internal Server Error", msg)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['GET'])
	@cherrypy.tools.json_out()
	def find_genotypes(self, owner):
		try:
			return self.genotype_service.find_by_owner(owner)
		except Exception as e:
			msg = ""
			if 'message' in e.args[0]:
				msg = str(e.args[0]['message'])
			else:
				msg = str(e)
			raise cherrypy.HTTPError("500 Internal Server Error", msg)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['GET'])
	@cherrypy.tools.json_out()
	def find_genotypes_by_permittee(self, permittee):
		try:
			return self.genotype_service.find_by_permittee_only_basic_data(permittee)
		except Exception as e:
			msg = ""
			if 'message' in e.args[0]:
				msg = str(e.args[0]['message'])
			else:
				msg = str(e)
			raise cherrypy.HTTPError("500 Internal Server Error", msg)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	def download_file(self, wallet, signature):
		try:
			name, ext = self.genotype_service.authorize_download(wallet, signature)
			file = self.genotype_service.download_file(name, ext)
			return file
		except:
			raise

		# except Exception as e:
		# 	msg = ""
		# 	if 'message' in e.args[0]:
		# 		msg = str(e.args[0]['message'])
		# 	else:
		# 		msg = str(e)
		# 	raise cherrypy.HTTPError("500 Internal Server Error", msg)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	def download_lab_file(self, signature, msg, permittee):
		try:
			self.test_permittee_service.is_permittee(permittee)
			self.genotype_service.real_validation(signature, msg, permittee)
			name = msg.split(".")[0]
			ext = msg.split(".")[1]
			self.genotype_service.is_file_enable(name)
			file = self.genotype_service.download_file(name, ext)
			return file
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
	def revoke_consents(self, owner, signature, permittee):
		try:
			revoked = self.genotype_service.revoke_consents(owner, signature, permittee)
			return revoked
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
	def create_permitee(self, id, address, secret, env):
		try:
			if env == "test":
				created = self.test_permittee_service.create_permittee(id, address, secret)
				return created
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
	@cherrypy.tools.allow(methods=['GET'])
	@cherrypy.tools.json_out()
	def test_validate_permittee(self, permittee):
		try:
			permittee = self.test_permittee_service.validate_permittee(permittee)
			permittee = self.test_permittee_service.basic_reference(permittee)
			return permittee
		except:
			raise
		# except Exception as e:
		# 	msg = ""
		# 	if 'message' in e.args[0]:
		# 		msg = str(e.args[0]['message'])
		# 	else:
		# 		msg = str(e)
		# 	raise cherrypy.HTTPError("500 Internal Server Error", msg)

# addition


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


	# WARNING ZONE FOR TEST ONLY
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
	@cherrypy.tools.allow(methods=['GET'])
	def test_bucker(self):
		try:
			return self.genotype_service.list_bucket_files()
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

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def search_all_by_table_test(self, table=None):
		try:
			return self.genotype_service.find_all_by_table(table)
		except Exception as e:
			print(e)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def create_table(self, table_name, fields):
		try:
			return self.genotype_service.create_table(table_name, fields)
		except Exception as e:
			msg = ""
			if 'message' in e.args[0]:
				msg = str(e.args[0]['message'])
			else:
				msg = str(e)
			raise cherrypy.HTTPError("500 Internal Server Error", msg)

	# @cherrypy.expose
	# @cherrypy.config(**{'tools.CORS.on': True})
	# @cherrypy.tools.allow(methods=['POST'])
	# @cherrypy.tools.json_out()
	# def delete_permittee(self, id):
	# 	try:
	# 		deleted = self.permittee_service.delete_permittee(id)
	# 		return True
	# 	except Exception as e:
	# 		print(e)

	# @cherrypy.expose
	# @cherrypy.config(**{'tools.CORS.on': True})
	# @cherrypy.tools.allow(methods=['DELETE'])
	# @cherrypy.tools.json_out()
	# def reset_genotype_table(self):
	# 	try:
	# 		self.genotype_service.delete_table()
	# 		return "You will need to deploy a new Smartcontract and change on the enviroment file"
	# 	except Exception as e:
	# 		print(e)

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
			'/js': {
				'tools.staticdir.on': True,
				'cors.expose.on': True,
				'tools.staticdir.dir': abspath('./public/pages/js'),
			},
			'/': {
				'tools.sessions.on': True,
				'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', 'http://127.0.0.1:5502/')],
				'server.socket_port': os.path.abspath(os.getcwd()),
				'response.timeout': False
			},
		}
		
		# when 	UPLOAD to SERVER descomment the following lines
		d = Daemonizer(cherrypy.engine)
		d.subscribe()

		cherrypy.server.socket_host = '0.0.0.0'
		cherrypy.server.socket_port = port
		cherrypy.quickstart(AppUnoServer(), '/', CONF)


# Avocado Blockchain Services at Merida, Yucatan