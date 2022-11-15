from dotenv import load_dotenv
from pymongo import MongoClient
import json
import os, os.path
# from datetime import datetime
import datetime
import requests
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.auto import w3
import web3
import re

class posp_dao:
	def __init__(self):
		self.w3 = Web3(HTTPProvider(os.getenv('BIOSAMPLE_PROVIDER')))
		self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
		self.account = self.w3.eth.account.privateKeyToAccount(os.getenv('BIOSAMPLE_EXECUTOR'))
		self.w3.eth.default_account = self.account.address
		self.SM_JSONINTERFACE_POSP = self.load_smart_contract(os.getenv('ABI_POSP_PATH'))
		self.SM_JSONINTERFACE_POSP_FACTORY = self.load_smart_contract(os.getenv('ABI_POSP_FACTORY_PATH'))
		self.client = MongoClient(os.getenv('TEST_MONGO_DB_HOST'))
		self.db = self.client[os.getenv('TEST_DB_NAME')]
		self.table = self.db.posp
		self.biosamples_table = self.db.biosamples
		self.genotypes_table = self.db.genotypes
	
	def load_smart_contract(self,path):
				solcOutput = {}
				try:
						with open(path) as inFile:
								solcOutput = json.load(inFile)
				except Exception as e:
						print(f"ERROR: Could not load file {path}: {e}")
				return solcOutput
	
	def create_sm_token(self, _metadata):
		print(_metadata)
		name = str(_metadata["name"])
		symbol = _metadata["symbol"]
		laboratory = _metadata["laboratory"]
		print("self.account.address",self.account.address)

		# # checar en la base de datos si el laboratorio cuienta con su respectiva licencia
		manager_sm = self.w3.eth.contract(address=os.getenv('TEST_POSP_FACTORY_CONTRACT'), abi=self.SM_JSONINTERFACE_POSP_FACTORY['abi'])
		create_token_tx = manager_sm.functions.createToken(name, symbol, laboratory).buildTransaction({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
		})

		print(create_token_tx)
		
		signed_tx = self.w3.eth.account.signTransaction(create_token_tx, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
		self.w3.eth.waitForTransactionReceipt(tx_hash)    
		print("tx hash\n",tx_hash.hex())
		return tx_hash.hex()

	def mint_posp(self, metadata):
		metadata["lab_address"] = web3.Web3.toChecksumAddress(metadata["lab_address"])
		metadata["user_address"] = web3.Web3.toChecksumAddress(metadata["user_address"])
		PospToken = []
		PospToken.append(0)
		PospToken.append(metadata["user_address"])
		PospToken.append(metadata["lab_address"])
		PospToken.append(metadata["title"])
		PospToken.append(metadata["msg"])
		PospToken.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		PospToken.append("")
		PospToken.append("")
		PospToken.append("0x0000000000000000000000000000000000000000")
		posp_contract = self.w3.eth.contract(address=os.getenv('TEST_POSP_FACTORY_CONTRACT'), abi=self.SM_JSONINTERFACE_POSP_FACTORY['abi'])
		tx = posp_contract.functions.mintInstancePOSP(metadata["token_sm"], PospToken).buildTransaction({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
		})
		signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
		self.w3.eth.waitForTransactionReceipt(tx_hash)    
		print("tx hash\n",tx_hash.hex())
		return tx_hash.hex()

	# # old version save posp hash
	# def save_posp_hash (self, metadata, token_hash):
	# 	cur = self.genotypes_table.find_one({"owneraddr": metadata["user_address"]})
	# 	# cur2 = self.biosamples_table.find_one({"owneraddr": metadata["
	# 	if not cur:
	# 		raise Exception("Could not find this user")
	# 	if "stake_nfts" not in cur:
	# 		cur["stake_nfts"] = {}
	# 	_json = cur["stake_nfts"]
	# 	_json[metadata["lab_address"]] = token_hash
	# 	self.genotypes_table.update_one({"owneraddr":metadata["user_address"]}, {"$set": {"stake_nfts": _json}})
	# 	return {"transactionHash":token_hash}

	def save_posp_hash (self, metadata):
		print(metadata)
		cur = self.table.find_one({"owner": metadata["user_address"], "laboratory":metadata["lab_address"]})
		if cur:
			raise Exception("You already have this token in the database")
		_fields = {
				"owner": str(metadata["user_address"]).upper(),
				"laboratory": str(metadata["lab_address"]).upper(),
				"hash": metadata["hash"],
				"created": datetime.datetime.now(),
				"updated": datetime.datetime.now()
			}
		self.table.insert_one(_fields)
		return True

	def find_by_owner_and_permittee(self, owner, permittee):
		row = []
		cur = self.table.find_one({"owner": re.compile(owner, re.IGNORECASE), "laboratory":re.compile(permittee, re.IGNORECASE)})
		if not cur:
			return {}
		return {permittee:cur["hash"]}


	def reset_posp_db (self):
		self.genotypes_table.update_many({},{"$set": {"stake_nfts": {}}})
		return True

	def get_token_sm(self, lab_address):
		lab_address = web3.Web3.toChecksumAddress(lab_address)
		posp_factory_contract = self.w3.eth.contract(address=os.getenv('TEST_POSP_FACTORY_CONTRACT'), abi=self.SM_JSONINTERFACE_POSP_FACTORY['abi'])
		posp_sm_address = posp_factory_contract.functions.getTokenSmartContractAddress(lab_address).call({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
		})
		return posp_sm_address[3]


	def get_posp_token(self,  token_sm_address, lab_address, user_address):
		token_sm_address = token_sm_address
		lab_address = web3.Web3.toChecksumAddress(lab_address)
		user_address = web3.Web3.toChecksumAddress(user_address)
		posp_contract = self.w3.eth.contract(address=token_sm_address, abi=self.SM_JSONINTERFACE_POSP['abi'])
		POSP = posp_contract.functions.getPoSP(lab_address, user_address).call({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
		})
		return POSP

	def get_current_id(self, token_sm_address):
		posp_contract = self.w3.eth.contract(address=token_sm_address, abi=self.SM_JSONINTERFACE_POSP['abi'])
		current_id = posp_contract.functions.getCurrentId().call({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
		})
		return current_id

	def find_token_by_permittee(self, permittee):
		permittee = web3.Web3.toChecksumAddress(permittee)

		posp_factory_contract = self.w3.eth.contract(address=os.getenv('TEST_POSP_FACTORY_CONTRACT'), abi=self.SM_JSONINTERFACE_POSP_FACTORY['abi'])
		token_sm = posp_factory_contract.functions.getTokenSmartContractAddress(permittee).call({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
		})
		print("\n\n",token_sm,"\n\n")
		return token_sm[3]


	def get_all_users(self):
		row = []
		cur = self.biosamples_table.find().sort("createdAt",-1)
		for doc in cur:
			# row.append({"serial":doc["serial"],"owner":doc["owner"]})
			row.append(doc["owner"])
			
		return row

