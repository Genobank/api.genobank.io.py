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
from time import sleep
from unicodedata import name
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from pathlib import Path
from libs import database
from libs.dao import permitte_dao
from libs.dao import test_permitte_dao
from libs.dao import genotype_dao
from libs.dao import license_dao
from libs.dao import posp_dao
from libs.service import permittee_service
from libs.service import test_permittee_service
from libs.service import genotype_service
from libs.service import license_service
from libs.service import posp_service

from libs.dao import restore_api_dao
from libs.service import restore_api_service

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
		licence = license_dao.license_dao()
		posp = posp_dao.posp_dao()
		self.permittee_service = permittee_service.permittee_service(permitte)
		self.test_permittee_service = test_permittee_service.test_permittee_service(test_permitte)
		self.genotype_service = genotype_service.genotype_service(genotype, posp)
		self.licence_service = license_service.license_service(licence)
		self.posp_service = posp_service.posp_service(posp)

		restore = restore_api_dao.restore_api_dao()
		self.restore_api_service = restore_api_service.restore_api_serivice(restore)
		# self.RESTORE_API_SERVICE = RESTORE_API()
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
			cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE'
			cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
			cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
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
	@cherrypy.tools.allow(methods=['POST', 'OPTIONS'])
	@cherrypy.tools.json_out()
	def save_genotype(self, data, file):
		try:
			valid_file = self.genotype_service.validate_file(file)
			print("\n\n", valid_file, "\n\n")
			data = json.loads(data)
			if "extension" not in data:
				raise Exception("This file does not have extension")
			self.genotype_service.validate_extension(data["extension"])
			self.genotype_service.validate_consents_metadata(data)
			created = self.genotype_service.create(data, file)
			minted_posp = self.posp_service.mint_posp_auto(data["labAddress"], data["userAddress"])
			if minted_posp:
				self.posp_service.save_posp_hash(minted_posp)
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
	def reset_wallet(self, file_name, user_addr, permittee_addr, secret):
		try:
			message=file_name+user_addr+permittee_addr
			hash1 = hmac.new(secret.encode('utf-8'),msg=message.encode(), digestmod="sha256")
			resetted = self.genotype_service.reset_wallet(file_name, user_addr, permittee_addr, hash1.hexdigest())
			return resetted
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
			posp_licence = self.licence_service.find_license_by_permitte_and_type(permittee, 2)
			if posp_licence:
				posp_licence = True
			genotype = self.genotype_service.only_basic_data(
				self.genotype_service.find_by_permittee(permittee)
				)
			token = self.posp_service.find_token_by_permittee(permittee)
			genotype.insert(0, token)
			genotype.insert(0, posp_licence)
			print(json.dumps(genotype, indent=2))
			return genotype
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
	def download_file(self, wallet, signature):
		try:
			name, ext = self.genotype_service.authorize_download(wallet, signature)
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
	def emit_posp(self, metadata):
		try:
			# _json_metadata = self.genotype_service.is_json(metadata)
			_json_metadata = json.loads(metadata)
			self.posp_service.validate_posp(_json_metadata)
			# check if file is enabled () thif cuntion recieves the file name
			name = _json_metadata["filename"]
			print(name)
			self.genotype_service.is_file_enable(name)
			self.test_permittee_service.validate_permittee_signature(_json_metadata)
			_json_metadata["hash"] = self.posp_service.mint_posp_or_fail(_json_metadata)
			self.posp_service.save_posp_hash(_json_metadata)
			return {"posp_token_hash": _json_metadata["hash"]}


			# print("\n\nVALIDATED SUCCESSFULLY \n\n")
			# return {"Server_message":"Successfully"}
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
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def create_token(self, metadata):
		try:
			_jsonmetadata =  json.loads(metadata)
			return self.posp_service.create_sm_token(_jsonmetadata)
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
	@cherrypy.tools.allow(methods=['GET'])
	@cherrypy.tools.json_out()
	def get_posp_token(self, lab_address, user_address):
		token_data = self.posp_service.get_posp_token(lab_address, user_address)
		return token_data[0]

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['GET'])
	@cherrypy.tools.json_out()
	def start_posp_airdrop(self):
		try:
			# all_users = self.posp_service.get_all_users()
			all_users = [
				"0xB931751fA194463AE252DE424911Bd5c51dF2174",
				"0x966C6E7E80682b4EFCD7063904cBD88F3fD3eC04",
				"0xEb62Cf01F71673C151080437cF404d97B6243600"
				]
			laboratory_destination = "0xD85D1F5Fd5af08cdE8b99Eff4921573503921266"
			count = 0
			for user in all_users:
				count +=1
				print("\nSTEP NUMBER [",count,"]\n")
				minted_posp = self.posp_service.mint_posp_airdrop_from_list(laboratory_destination, user)
				if minted_posp:
					self.posp_service.save_posp_hash(minted_posp)
				# print(user["owner"])
		except:
			raise #cherrypy.HTTPError("Error")

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['POST'])
	@cherrypy.tools.json_out()
	def revoke_consents(self, owner, signature, permittee):
		try:
			revoked = self.genotype_service.revoke_consents(owner, signature, permittee)
			return revoked
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
	def add_test_licence(self, permittee, secret, licence_metadata):
		try:
			secret = hmac.new(secret.encode('utf-8'),msg=permittee.encode(), digestmod="sha256")		# remove this line when we have the web page
			secret = secret.hexdigest()																 	# remove this line when we have the web page
			self.genotype_service.check_generic_secret(permittee, secret)
			return self.licence_service.create_licence(licence_metadata)
			# return True
		except Exception as e:
			msg = ""
			if 'message' in e.args[0]:
				msg = str(e.args[0]['message'])
			else:
				msg = str(e)
			raise cherrypy.HTTPError("500 Internal Server Error", msg)

	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['DELETE'])
	@cherrypy.tools.json_out()
	def delete_test_license(self, permittee, type, secret):
		try:
			secret = hmac.new(secret.encode('utf-8'),msg=permittee.encode(), digestmod="sha256")		# remove this line when we have the web page
			secret = secret.hexdigest()																 	# remove this line when we have the web page
			self.genotype_service.check_generic_secret(permittee, secret)
			return self.licence_service.delete_license(permittee, type)
		except Exception as e:
			msg = ""
			if 'message' in e.args[0]:
				msg = str(e.args[0]['message'])
			else:
				msg = str(e)
			raise cherrypy.HTTPError("500 Internal Server Error", msg)


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



	@cherrypy.expose
	@cherrypy.config(**{'tools.CORS.on': True})
	@cherrypy.tools.allow(methods=['DELETE'])
	@cherrypy.tools.json_out()
	def reset_all_ancestry_API(self):
		try:
			return self.restore_api_service.restore_api_service()
		except:
			raise





class AppUno(object):
	def __init__(self) -> None:
		return None

	def start(self, port):
		CONF = {
			'/static': {
				'tools.staticdir.on': True,
				'tools.staticdir.dir': abspath('./public'),
			},'/js': {
				'tools.staticdir.on': True,
				'tools.staticdir.dir': abspath('./public/pages/js'),
			},'/': {
				'tools.sessions.on': True,
				'tools.response_headers.on': True,
				# 'server.socket_port': os.path.abspath(os.getcwd()),
				# 'response.timeout': False
			},
		}
		
		# when 	UPLOAD to SERVER descomment the following lines
		# d = Daemonizer(cherrypy.engine)
		# d.subscribe()

		
		cherrypy.server.socket_host = '0.0.0.0'
		cherrypy.server.socket_port = port
		cherrypy.quickstart(AppUnoServer(), '/', CONF)

# Avocado Blockchain Services at Merida, Yucatan