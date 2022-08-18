from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from pymongo import MongoClient

import os
import json
import datetime


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
				"extension": data["extension"],
				"hash": data["token_hash"],
				"signature": data["signature"],
				"created": datetime.datetime.now(),
				"updated": datetime.datetime.now()
			}
			self.table.insert_one(_fields)
			return True
		except:
			raise

	def save_file(self, file, data):
		ext = data["extension"]
		file_name = data["filename"]
		content_file = file.file.read()
		with open(f"storage/genotypes/{file_name}."+ext, "wb") as f:
			f.write(content_file)
		return file_name

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

				# doc['_id'] = str(doc['_id'])
				# doc['createdAt'] = str(doc['createdAt'])
				# doc['updatedAt'] = str(doc['updatedAt'])

				row.append(doc)
				# print(doc)
			return row
		except Exception as e:
			print(e)
			return False

	

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