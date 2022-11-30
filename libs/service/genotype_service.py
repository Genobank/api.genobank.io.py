# from re import T
from time import sleep
from cryptography.fernet import Fernet
from libs.dao import genotype_dao
from libs.dao import posp_dao
from libs.exceptions import DomainInjectionError
from libs.domain import Encryption
import requests
import os
import uuid
import hmac
import io
import json
import web3


class genotype_service:
	def __init__(self, _genotype, _posp_dao):
		if not isinstance(_genotype, genotype_dao.genotype_dao):
			raise DomainInjectionError.DomainInjectionError("genotype_service", "genotype")
		if not isinstance(_posp_dao, posp_dao.posp_dao):
			raise DomainInjectionError.DomainInjectionError("posp_service", "posp")

		self.genotype = _genotype
		self.posp = _posp_dao
		self.encryption = Encryption.Encryption()

	def create(self, data, file):
		data["filename"] = str(uuid.uuid4())
		data["key"] = (Fernet.generate_key()).decode("utf-8")
		file.file.seek(0)
		bucket_send = self.genotype.upload_file_to_bucket(file, "genotypes/"+data["filename"]+"."+data["extension"], data["labAddress"])
		if not bucket_send:			
			raise Exception("Error uploading file to bucket")
		token_hash = self.genotype.mint_nft(data)
		if not token_hash:
			raise Exception("Error minting token")
		data["token_hash"] = token_hash
		save_db_file = self.genotype.save_db_file(data)
		if not save_db_file:
			raise Exception("Error saving file in database")
		data["key"] = bytes(data["key"],  'utf-8')
		file_name = self.genotype.save_file(file, data)
		if not file_name:
			raise Exception("Error saving file")
		return {"token": token_hash}

	def reset_wallet(self, file_name, user_addr, permittee_addr, secret):
		resseted = self.genotype.reset_wallet(file_name, user_addr, permittee_addr, secret)
		return resseted

	def upload_file_to_bucket(self):
		# add boto to upload to the bucket
		bucket_send = self.genotype.upload_file_to_bucket("55052008713979.zip", "somos-genobank")
		if not bucket_send:
			raise Exception("Error uploading file to bucket")
		return {"response": bucket_send}

	def validate_file(self, file):
		f = file.file.read()
		source =  self.genotype.Manejador(f)
		if source < 0:
			raise Exception("Not valid File Source")
		return source
		# print(source)

	def validate_extension(self, ext):
		if ext != "txt":
			raise Exception("Invalid extension you file needs to be a txt extension")
		return True


	def validate_consents_metadata(self, data):
		if "agreements" not in data:
			# raise Exception("Invalid consent metadata")
			raise Exception("Invalid consent metadata")
		agreements = data['agreements']
		if "questions" not in agreements:
			raise Exception('Consent #1 is required for consent metadata')
		if "document" not in agreements:
			raise Exception('Consent #2 is required for consent metadata')
		if "read" not in agreements:
			raise Exception('Consent #3 is required for consent metadata')
		if "permission" not in agreements:
			raise Exception('Consent #4 is required for consent metadata')
		if "providing" not in agreements:
			raise Exception('Consent #5 is required for consent metadata')
		if "results" not in agreements:
			raise Exception('Consent #6 is required for consent metadata')

	def validate_snips(self, file):
		file.file.seek(0)
		# print(file.file.read().decode('utf8'))
		# print(file)
		lines = file.file.readlines()
		count = 0
		_json_snips = {}
		for line in lines:
			count+=1
			decoded_line = str(line.decode('utf8'))
			if(self.snipid_in_line(decoded_line)):
				line_elements = decoded_line[:-1]
				line_elements = line_elements.split("\t")
				_json_snips[line_elements[0]] = line_elements[3]
		
		print(_json_snips)
		return True

	def snipid_in_line(self, line):
		pref_list = [
			'rs952718', 'rs7803075', 'rs9319336', 'rs2397060', 'rs1344870', 'rs2946788',
			'rs6591147', 'rs2272998', 'rs7229946', 'rs9951171', 'rs525869', 'rs530501',
			'rs2040962', 'rs2032624', 'rs1865680', 'rs17307398', 'rs3795366', 'rs2460111',
			'rs1675126', 'rs1061629', 'rs538847', 'rs76432344', 'rs3750390', 'rs1624844',
			'rs3803390', 'rs2293768', 'rs9358890', 'rs11197835', 'rs1806191', 'rs7953',
			'rs3736757', 'rs2940779'
			]
		res = line.startswith(tuple(pref_list))
		return res


	def find_by_owner(self, owner):
		genotype = self.genotype.find_genotype_by_owner(owner)
		if not genotype:
			return {}
		return genotype

	def find_by_permittee(self, owner):
		genotype = self.genotype.find_genotype_by_permittee(owner)
		if not genotype:
			return {}
		return genotype

	def only_basic_data(self, genotype_list):
		if not genotype_list:
			return []
		for index in genotype_list:
			if "_id" in index: del index["_id"]
			if "filesigned" in index: del index["filesigned"]
			if "hash" in index: del index["hash"]
			if "signature" in index: del index["signature"]
			if "key" in index: del index["key"]
			if "updated" in index: del index["updated"]
			index["stake_nfts"] = self.posp.find_by_owner_and_permittee(index["owneraddr"], index["labaddr"])
			# print(index["stake_nfts"])
		return genotype_list

	def list_to_json(self, gen_list):
		_json = {}
		for gen in gen_list:
			for key in gen:
				_json[key] = gen[key]

	def basic_reference(self, _genotype):
		if not _genotype:
			return []
		_json = {}
		_json["name"] = _genotype["filename"]
		_json["ext"] = _genotype["extension"]
		_json["lab"] = _genotype["labaddr"]
		_json["status"] = _genotype["status"]
		_json["filesize"] = _genotype["filesize"]
		_json["consents"] = _genotype["consents"]
		_json["created"] = _genotype["created"]
		# _json["interpretation"] = {"ancestry":{"AFR_ESTE":1.8547,"AFR_NORTE":0.001,"AFR_OESTE":0.001,"ASIA_ESTE":0.001,"ASIA_SUR":0.001,"ASIA_SURESTE":0.001,"EUR_ESTE":0.001,"EUR_NORESTE":5.0803,"EUR_NORTE":0.001,"EUR_OESTE":0.001,"EUR_SUROESTE":65.7974,"JUDIO":15.8035,"MEDIO_ORIENTE":0.001,"OCEANIA":0.8112,"AMAZONAS":0.001,"ANDES":0.001,"MAYA":0.001,"PIMA":0.001,"ZAPOTECA":0.001,"HUICHOL":1.283,"MIXTECA":0.001,"NAHUA_OTOMI":9.3528,"TARAHUMARA":0.001,"TRIQUI":0.001,"Hp_m":None,"Hp_y":None}}
		results = self.genotype.find_ancestry_db(_genotype["filename"], _genotype["owneraddr"], _genotype["labaddr"])
		_json["interpretation"] = {}
		exception_account = int(web3.Web3.toChecksumAddress(_genotype["labaddr"]), 16)

		acc_except = [
			119291188120719338625660708458653265813805800094,
			451629096598492253986138676752610719961088798814
		]

		if exception_account not in acc_except:
			if not results:
				results = self.genotype.download_file_from_bucket(_genotype["labaddr"],  _genotype["filename"] +"."+ _genotype["extension"])
				if not results:
					_json["interpretation"] = False
					return _json
				self.genotype.save_ancestry_db(_genotype, results)
			_json["interpretation"] = json.loads(results)

		return _json

	def authorize_download(self, wallet, signature):
		# signature = data["signature"]
		# wallet = data["wallet"]
		# # message = signature+wallet
		# # mark_key = hmac.new(signature.encode('utf-8'),msg=message.encode(), digestmod="sha256")
		validation, name, ext= self.genotype.verify_signature(wallet, signature)
		if not validation:
			raise Exception("Invalid signature")
		return name, ext

	def real_validation(self, signature, msg, permittee):
		valid = self.genotype.real_validation(signature, msg, permittee)
		if not valid:
			raise Exception("You permittee is not valid")
		return valid

	def is_file_enable(self, file_name):
		is_enable = self.genotype.is_file_enable(file_name)
		if not is_enable:
			raise Exception("This file has consents revoked")
		return is_enable

	def download_file(self, file_name, file_ext):
		file = self.genotype.download_file(file_name, file_ext)
		# if not file:
		#   raise Exception("Couldn't find file")
		return file

	def revoke_consents(self, owner, signature, permittee):
		authorized, name, ext= self.genotype.verify_signature(owner, signature)
		if not authorized:
			raise Exception("Invalid signature")
		revoked = self.genotype.revoke_consents(owner, permittee)
		# if not revoked:
		#   raise Exception("Couldn't revoke consent")
		return revoked

	def checkPermitteeSecret(self, id, address, secret):
		try:
			secret = str(secret)
			message=id+address
			hmac1 = hmac.new(os.getenv('TEST_APP_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
			hmac1 = str(hmac1.hexdigest())

			return hmac1 == secret
		except Exception as e:
			raise e

	def check_generic_secret(self, message, secret):
		checked = self.genotype.check_generic_secret(message, secret)
		if not checked:
			raise Exception("wrong password")
		return checked

	def validate_permitte(self, id):
		resp = requests.get(
			os.getenv('API_PERMITTEES')+"{0}".format(id)
		)

	def create_table(self, name):
		created = self.genotype.create_table(name)
		if not created:
			raise Exception("Failed to create new table, please try again later")
		return created
	
	def insert_many_on_table(self, table, list):
		return self.genotype.insert_many(table, list)

	def find_all_by_table(self, table):
		if table == None or table == "":
			tables = self.genotype.get_list_collection_names()
			return {"Requires table name":tables}
		else:
			search = self.genotype.find_all_by_table(table)
			if not search:
				return []
		return search








	# WARNIGN ZONE, FRO TEST ONLY
	def list_bucket_files(self, permitte, file):
		files_list = self.genotype.list_bucket_files(permitte, file)
		return files_list
