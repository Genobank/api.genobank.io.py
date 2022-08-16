from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

import os
import json
import uuid



class genotype_dao:
	def __init__(self):
		self.w3 = Web3(HTTPProvider(os.getenv('PROVIDER')))
		self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
		self.account = self.w3.eth.account.privateKeyToAccount(os.getenv('BIOSAMPLE_EXECUTOR'))
		self.w3.eth.default_account = self.account.address
		self.SM_JSONINTERFACE = self.load_smart_contract(os.getenv('ABI_BIOSAMPLE_PATH'))

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

		# ADDING it will need set all data on the metadata object
		


		contract = self.w3.eth.contract(address=os.getenv('TEST_BIOSAMPLE_COTRACT'), abi=self.SM_JSONINTERFACE['abi'])
		
		# id_address = int(wallet, 16)

    # tx = contract.functions.mint(id_address, wallet, 'ACTIVE').buildTransaction({
    #     'nonce': self.w3.eth.getTransactionCount(self.account.address)
    # })
		tx = contract.functions.addGenotype(file_name, owner, permittee).buildTransaction({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
			})
		signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
		self.w3.eth.waitForTransactionReceipt(tx_hash)    
		print("tx hash\n",tx_hash.hex())
		return tx_hash.hex()

	def generate_token_id (self, token):
		try:
			return int(token, 16)
		except Exception as e:
			raise Exception(str(e))

	def save_file(self, file, ext):
		content_file = file.file.read()
		file_name = str(uuid.uuid4())
		with open(f"storage/genotypes/{file_name}."+ext, "wb") as f:
			f.write(content_file)
		return file_name