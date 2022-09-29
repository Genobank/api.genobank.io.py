import boto3
import re
import logging

from botocore.exceptions import ClientError
from cherrypy.lib import static
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from eth_account.messages import encode_defunct
from pymongo import MongoClient
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.auto import w3

import base64
import datetime
import json
import os, os.path

class genotype_dao:
	def __init__(self):
		self.w3 = Web3(HTTPProvider(os.getenv('BIOSAMPLE_PROVIDER')))
		self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
		self.account = self.w3.eth.account.privateKeyToAccount(os.getenv('BIOSAMPLE_EXECUTOR'))
		self.w3.eth.default_account = self.account.address
		self.SM_JSONINTERFACE = self.load_smart_contract(os.getenv('ABI_BIOSAMPLE_PATH'))
		self.client = MongoClient(os.getenv('TEST_MONGO_DB_HOST'))
		self.db = self.client[os.getenv('TEST_DB_NAME')]
		self.table = self.db.genotypes

	def load_smart_contract(self,path):
				solcOutput = {}
				try:
						with open(path) as inFile:
								solcOutput = json.load(inFile)
				except Exception as e:
						print(f"ERROR: Could not load file {path}: {e}")
				return solcOutput

	def mint_nft(self, metadata):
		file_name = metadata["filename"]
		owner = metadata["userAddress"]
		permittee = metadata["labAddress"]

		contract = self.w3.eth.contract(address=os.getenv('TEST_BIOSAMPLE_COTRACT'), abi=self.SM_JSONINTERFACE['abi'])

		tx = contract.functions.addGenotype(file_name, owner, permittee).buildTransaction({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
			})
		signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
		self.w3.eth.waitForTransactionReceipt(tx_hash)    
		print("tx hash\n",tx_hash.hex())
		return tx_hash.hex()

	def save_db_file(self, data):
		try:
			_fields = {
				"labaddr": data["labAddress"],
				"owneraddr": data["userAddress"],
				"filename": data["filename"],
				"genetic_test": data["genetic_test"],
				"extension": data["extension"],
				"key": bytes(data["key"], 'utf-8'),
				"consents": data['agreements'],
				"hash": data["token_hash"],
				"signature": data["signature"],
				"status": True,
				"filesigned":data["filesigned"],
				"filesize":data["filesize"],
				"created": datetime.datetime.now(),
				"updated": datetime.datetime.now()
			}
			self.table.insert_one(_fields)
			return True
		except:
			raise

	def save_file(self, file, data):
		try:
			ext = data["extension"]
			file_name = data["filename"]
			fernet = Fernet(data["key"])

			content_file = file.file.read()
			encrypted_file = fernet.encrypt(content_file)

			with open(f"storage/genotypes/{file_name}."+ext, "wb") as f:
				f.write(encrypted_file)
			return file_name
		except:
			raise

	def download_file (self, name, ext):
		try:
			collection = self.db.genotypes
			cur = collection.find_one({"filename": name})
			file_path = os.path.abspath("storage/genotypes/"+name+"."+ext)
			key = cur['key']
			print(key)
			key = bytes(key)
			# key = key[2:-1]
			print(key)
			fernet = Fernet(key)
			with open(file_path, 'rb') as enc_file:
				encrypted = enc_file.read()
			decrypted = fernet.decrypt(encrypted)
			return decrypted


			# return static.serve_file(file_path, 'application/x-download','attachment', os.path.basename(file_path))  #<---extension file
		except Exception as e:
			print(e)
			return False

	def upload_file_to_bucket(self, file_name, bucket, object_name = None):
		if object_name is None:
			object_name = os.path.basename("storage/genotypes/"+file_name)
		s3_client = boto3.client(service_name='s3',
								aws_access_key_id='AKIAUFOG4Q6XPT3LMZHB',
								aws_secret_access_key='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')
		try:
			response = s3_client.upload_file("storage/genotypes/"+file_name, bucket, object_name)
			# return response
		except ClientError as e:
			print(e)
			logging.error(e)
			return False
		return True


	def list_bucket_files(self):
		s3 = boto3.resource(service_name='s3',
								aws_access_key_id='AKIAUFOG4Q6XPT3LMZHB',
								aws_secret_access_key='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')

		s3_client = boto3.client(service_name='s3',
								aws_access_key_id='AKIAUFOG4Q6XPT3LMZHB',
								aws_secret_access_key='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')

		my_bucket = s3.Bucket('somos-genobank')

		for my_bucket_object in my_bucket.objects.all():
			print(my_bucket_object.key)

		s3_client.download_file('somos-genobank', 'prub.txt', 'my_localfile.txt')
		print(open('my_localfile.txt').read())
		# print(my_bucket.obje)

		# if object_name is None:
		# 	object_name = os.path.basename("storage/genotypes/"+file_name)
		# s3_client = boto3.client(service_name='s3',
		# 						aws_access_key_id='AKIAUFOG4Q6XPT3LMZHB',
		# 						aws_secret_access_key='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')
		# try:
		# 	response = s3_client.upload_file("storage/genotypes/"+file_name, bucket, object_name)
			# return response

	def find_genotype_by_owner(self, owner):
		try:
			collection = self.db.genotypes
			cur = collection.find({"owneraddr": owner})
			_json = {}
			row = []
			for doc in cur:
				for key in doc:
					if (not isinstance(doc[key], str)) or (not isinstance(doc[key], int)) or (not isinstance(doc[key], float)):
						doc[key] = str(doc[key])
				row.append(doc)
				# print(doc)
			return row[0]
		except Exception as e:
			print(e)
			return False

	def find_genotype_by_permittee(self, permittee):
		try:
			collection = self.db.genotypes
			cur = collection.find({"labaddr": permittee})
			row = []
			for doc in cur:
				# doc[""]
				for key in doc:
					if (not isinstance(doc[key], str)) or (not isinstance(doc[key], int)) or (not isinstance(doc[key], float)):
						doc[key] = str(doc[key])
				row.append(doc)
				# print(doc)
			return row
		except Exception as e:
			print(e)
			return False

	def find_genotype_by_signature(self, signature):
		try:
			collection = self.db.genotypes
			cur = collection.find({"filesigned": signature})
			_json = {}
			row = []
			for doc in cur:
				for key in doc:
					if (not isinstance(doc[key], str)) or (not isinstance(doc[key], int)) or (not isinstance(doc[key], float)):
						doc[key] = str(doc[key])
				row.append(doc)
				# print(doc)
			return row[0]
		except Exception as e:
			print(e)
			return False

	def verify_signature(self, wallet, signature):
		try:
			# genotype_db = self.find_genotype_by_signature(signature)
			genotype_db = self.find_genotype_by_owner(wallet)
			if not genotype_db:
				raise Exception("Genotype not found")
			wallet_db = genotype_db["owneraddr"]
			signature_db = genotype_db["filesigned"]
			return ((wallet == wallet_db) and (signature == signature_db)), genotype_db["filename"], genotype_db["extension"]
		except Exception as e:
			print(e)
			return False

	def real_validation(self, signed_message, msg, permittee):
		msg = encode_defunct(text=msg)
		wallet = w3.eth.account.recover_message(msg, signature=signed_message)

		print("\n\n\n\n\nWallet:", wallet,"\n\n\n")
		# delete this part only to download boto3
			# s3_client = boto3.client(service_name='s3',
			# 													aws_access_key_id='AKIAUFOG4Q6XPT3LMZHB',
			# 													aws_secret_access_key='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',
			# 													region_name='us-east-1'
			# 												)

			# s3_client.download_file(Bucket='somos-genobank', Key='GHAnDU0029.txt', Filename='GHAnDU0029.txt')
		return (wallet == permittee)

	def is_file_enable(self, filename):
		try:
			collection = self.db.genotypes
			cur = collection.find_one({"filename": filename})
			enable = cur["status"]
			return enable
			# return enable.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
		except Exception as e:
			print(e)
			return e

		

	def revoke_consents(self, owner, permittee):
		try:
			tx = self.burn_bio_token(owner, permittee)
			if not tx:
				raise Exception("Smartcontract: Error during revoke_consents")
			collection = self.db.genotypes
			collection.update_one({"owneraddr":owner}, {"$set": {"status": False}})
			return {"transactionHash":tx}
		except:
			# print(e)
			raise

	def burn_bio_token(self, owner, permittee):
		contract = self.w3.eth.contract(address=os.getenv('TEST_BIOSAMPLE_COTRACT'), abi=self.SM_JSONINTERFACE['abi'])
		tx = contract.functions.burnToken(owner, permittee).buildTransaction({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
			})
		signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
		self.w3.eth.waitForTransactionReceipt(tx_hash)    
		print("tx hash\n",tx_hash.hex())
		return tx_hash.hex()





	def create_table(self, name, fields):
		try:
			# self.db.create_collection(name)
			
			# self.db[name].insert_one(fields)

			# self.db.create_collection(name,{
			# 	"labaddr": <String>,
			# 	"owneraddr": <String>,
			# 	"filename": <String>,
			# 	"extension": <String>,
			# 	"hash": <String>,
			# 	"signature": <String>,
			# 	"created": <Date>,
			# 	"updated": <Date>
			# })


			# return self.db.list_collection_names()

			raise Exception("Failed to create new table, this methos is locked")
			# return True
		except:
			raise 

	def find_all_by_table(self, table):
		try:
			collection = self.db[table]
			cur = collection.find()
			_json = {}
			row = []
			for doc in cur:
				for key in doc:
					if (not isinstance(doc[key], str)) or (not isinstance(doc[key], int)) or (not isinstance(doc[key], float)):
						doc[key] = str(doc[key])

				# doc['_id'] = str(doc['_id'])
				# doc['createdAt'] = str(doc['createdAt'])
				# doc['updatedAt'] = str(doc['updatedAt'])

				row.append(doc)
				# print(doc)
			return row
		except Exception as e:
			print(e)
			return False

	def get_list_collection_names(self):
		try:
			return self.db.list_collection_names()
		except Exception as e:
			print(e)
			return False




	# WARNING ZONE, FOR TEST ONLY

	def delete_table(self):
		try:
			deleted = self.table.delete_many({})
			return deleted.deleted_count+" documents deleted successfully"
		except Exception as e:
			print(e)
			return False
