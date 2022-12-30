from pymongo import MongoClient
import os
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
import hmac
from pprint import pprint
import eth_keys, eth_utils, binascii, os
import json
import datetime
from eth_account.messages import encode_defunct

class biosample_dao:
	def __init__(self):
		self.w3 = Web3(HTTPProvider(os.getenv('BIOSAMPLE_PROVIDER')))
		self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
		self.account = self.w3.eth.account.privateKeyToAccount(os.getenv('BIOSAMPLE_EXECUTOR'))
		self.w3.eth.default_account = self.account.address
		self.SM_BPT_JSONINTERFACE = self.load_smart_contract(os.getenv('ABI_BPT_PATH'))


		self.client = MongoClient(os.getenv('TEST_MONGO_DB_HOST'))
		self.db = self.client[os.getenv('TEST_DB_NAME')]
		self.biosample_activations_table = self.db["biosample-activations"]
		self.biosamples_table = self.db["biosamples"]
		self.permissions_table = self.db["permissions"]


	def load_smart_contract(self,path):
		solcOutput = {}
		try:
				with open(path) as inFile:
						solcOutput = json.load(inFile)
		except Exception as e:
				print(f"ERROR: Could not load file {path}: {e}")
		return solcOutput

	def claim(self, token_id, data):
		biosample_id = int(token_id[0:12], 16)
		address = f"""0x{token_id[24:]}"""
		receiverAddress  = Web3.toChecksumAddress(address)
		activation = self.find_by_serial(biosample_id)
		signature = data["signature"]
		seed = data["seed"]
		signature_kind = int(data["signatureKind"])
		if activation["isPersistent"]:
			if not self.check_biosample_activation_secret(data, biosample_id):
				raise Exception("Error: Invalid Signature")
		else:
			if not self.check_biosample_secret(data, biosample_id):
				raise Exception("Error: Invalid Signature")
		
		createTokenId, create_token_mint_hash, create_token_permission_hash = self.claim_sm_tokens(token_id, receiverAddress, signature, seed, signature_kind)
		

		now = datetime.datetime.now()
		iso_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4]+"Z"
		time_stamp = datetime.datetime.timestamp(now)
		data_to_sign = f"{os.getenv('NAMESPACE')}.login-third-party|{biosample_id}|{activation['permitteeSerial']}|${iso_time}"
		message = encode_defunct(text=data_to_sign)
		data_signed = self.w3.eth.account.sign_message(message, os.getenv('BIOSAMPLE_EXECUTOR') )
		data_signature = data_signed.signature.hex()
		data_hash = data_signed.messageHash.hex()

		biosample_object = {
			"txStatus":1,
			"txHash":str(create_token_mint_hash).lower(),
			"serial": biosample_id,
			"status": "ACTIVE",
			"owner":str(receiverAddress),
			"actor":str(self.account.address),
			"tokenId": createTokenId
		}

		self.create_biosample_object(biosample_object)

		permission_object = {
			"txStatus":1,
			"txHash":str(create_token_permission_hash),
			"biosampleSerial":str(biosample_id),
			"permitteeSerial":activation["permitteeSerial"],
			"tokenId":f"0x{token_id}",
			"status":"ACTIVE",
			"owner":str(receiverAddress),
            "actor":str(receiverAddress),
		}

		self.create_permission_object(permission_object)


		return {
			"data":{
				"biosampleSerial": biosample_id,
                "hash": data_hash,
				"permitteeSerial":activation["permitteeSerial"],
				"signature": data_signature,
				"timestamp": time_stamp,
				"transactions":[
					{"transactionHash":create_token_mint_hash},
					{"transactionHash":create_token_permission_hash}
				]
			}
		} 
	
	def create_biosample_object(self, biosample_obj):
		cur = self.biosamples_table
		return True

	def create_permission_object(self, permission_obj):
		cur = self.permissions_table
		return True



	def check_biosample_activation_secret(self, data, biosample_id):
		try:
			message = str(biosample_id)
			s_hash = data['biosampleSecret']
			hmac1 = hmac.new(os.getenv('BIOSAMPLE_ACTIVATION_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
			digest = str(hmac1.hexdigest())
			return s_hash == digest
		except Exception as e:
			raise e

	def check_biosample_secret(self, data, biosample_id):
		try:
			message = str(biosample_id)
			s_hash = data['biosampleSecret']
			hmac1 = hmac.new(os.getenv('TEST_APP_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
			digest = str(hmac1.hexdigest())
			return s_hash == digest
		except Exception as e:
			raise e

	def claim_sm_tokens(self, _tokenId, receiver_address, sign, seed, signature_kind):
		createTokenId = f"0x{_tokenId[0:12]}000000000000{self.account.address[2:]}"
		createTokenId = int(createTokenId,16)
		contract = self.w3.eth.contract(address=os.getenv('TEST_BPT_CONTRACT'), abi=self.SM_BPT_JSONINTERFACE['abi'])
		create_token_tx = contract.functions.mint(
			createTokenId,
			receiver_address,
			'ACTIVE'
		).buildTransaction({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
		})
		create_token_tx_signed_tx = self.w3.eth.account.signTransaction(create_token_tx, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		create_token_tx_hash = self.w3.eth.sendRawTransaction(create_token_tx_signed_tx.rawTransaction)
		self.w3.eth.waitForTransactionReceipt(create_token_tx_hash)
		mint_token_hash = create_token_tx_hash.hex()
		print("create_token_tx_hash\n",create_token_tx_hash.hex())

		# check the nex steps HERE
		sig = Web3.toBytes(hexstr=sign[2:])
		(v, r, s) = Web3.toInt(sig[-1]), Web3.toHex(sig[:32]), Web3.toHex(sig[32:64])

		
		tx_send = contract.functions.createWithSignature(
			int(_tokenId,16),
			"ACTIVE",
			int(seed,16),
			r,
			s,
			v,
			signature_kind
		).buildTransaction({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
		})

		tx_send_signed_tx = self.w3.eth.account.signTransaction(tx_send, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		tx_send_tx_hash = self.w3.eth.sendRawTransaction(tx_send_signed_tx.rawTransaction)
		self.w3.eth.waitForTransactionReceipt(tx_send_tx_hash)
		signed_token_hash = tx_send_tx_hash.hex()
		print("tx_send_tx_hash\n",tx_send_tx_hash.hex())

		return createTokenId, mint_token_hash, signed_token_hash





		




		# file_name = metadata["filename"]
		# owner = metadata["userAddress"]
		# permittee = metadata["labAddress"]
		# tx = contract.functions.addGenotype(file_name, owner, permittee).buildTransaction({
		# 	'nonce': self.w3.eth.getTransactionCount(self.account.address)
		# 	})
		# signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))


	def parse_address_to_int(self, address):
		try:
			valid_toke_address = Web3.toChecksumAddress(address)
			print(valid_toke_address)
		except:
			raise Exception("No valid address")

	def find_by_serial(self, serial):
		cur = self.biosample_activations_table.find_one({"serial":serial})
		cur["isPersistent"] = self.is_persistent(cur)
		return cur
	
	def is_persistent(self, mongo_object):
		_id  = mongo_object["_id"]
		return bool(_id)

		


