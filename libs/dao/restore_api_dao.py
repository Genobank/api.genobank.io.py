from pymongo import MongoClient
import os, shutil
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from solcx import compile_files
import json
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
class restore_api_dao:
	def __init__(self):
		self.w3 = Web3(HTTPProvider(os.getenv('BIOSAMPLE_PROVIDER')))
		self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
		self.account = self.w3.eth.account.privateKeyToAccount(os.getenv('BIOSAMPLE_EXECUTOR'))
		self.w3.eth.default_account = self.account.address
		self.BIOSAMPLE_JSONINTERFACE = self.load_smart_contract(os.getenv('ABI_BIOSAMPLE_PATH'))
		self.FACTORY_JSONINTERFACE = self.load_smart_contract(os.getenv('ABI_POSP_FACTORY_PATH'))
		# self.POSP_JSONINTERFACE = self.load_smart_contract(os.getenv('ABI_POSP_PATH'))
		self.client = MongoClient(os.getenv('TEST_MONGO_DB_HOST'))
		self.db = self.client[os.getenv('TEST_DB_NAME')]
		self.genotypes_table = self.db.genotypes
		self.posp_table = self.db.posp
		self.ancestry_table = self.db.ancestry
		
	def delete_genotypes_table(self):
		try:
			deleted = self.genotypes_table.delete_many({})
			return deleted.deleted_count+" documents deleted successfully"
		except Exception as e:
			print(e)
			return False

	def delete_genotypes_file(self):
		folder = os.path.abspath(os.getenv('BIOSAMPLE_ADDS'))
		for filename in os.listdir(folder):
			file_path = os.path.join(folder, filename)
			try:
				if os.path.isfile(file_path) or os.path.islink(file_path):
					os.unlink(file_path)
				# elif os.path.isdir(file_path):
				# 	shutil.rmtree(file_path)
			except Exception as e:
				print('Failed to delete %s. Reason: %s' % (file_path, e))

	def compile_sm_genotypes_and_save_json(self):
		solidity_sm_path = os.path.abspath("./smart_contract/genotype.sol")
		compiled_sol = compile_files(
			[solidity_sm_path],
			output_values=['abi', 'bin'],
			solc_version="0.8.9"
		)
		contract_id, contract_interface = compiled_sol.popitem()
		with open(f"smart_contract/Biosample.json", "w") as f:
			f.write(json.dumps(contract_interface, indent=2))
		return True

	def deploy_genotype_smartcontract(self):
		abi = self.BIOSAMPLE_JSONINTERFACE["abi"]
		bytecode = self.BIOSAMPLE_JSONINTERFACE["bin"]
		genotype_sm = self.w3.eth.contract(abi=abi, bytecode = bytecode)
		tx_hash = genotype_sm.constructor("Genobank.io").buildTransaction({
			'from':self.account.address,
			'nonce': self.w3.eth.getTransactionCount(self.account.address),
		})
		signed = self.w3.eth.account.signTransaction(tx_hash, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		sm_deployed = self.w3.eth.sendRawTransaction(signed.rawTransaction)
		sm_address = self.w3.eth.waitForTransactionReceipt(sm_deployed)
		return sm_address.contractAddress

	def save_genotype_sm_env (self, sm_address):
		file_path = os.path.abspath("./.env")
		fh, abs_path = mkstemp()
		with fdopen(fh,'w') as new_file:
			with open(file_path, "r") as old_file:
				for line in old_file:
					if line.startswith("TEST_BIOSAMPLE_COTRACT"):
						new_file.write('TEST_BIOSAMPLE_COTRACT = "'+sm_address+'"\n')
					else:
						new_file.write(line)
		copymode(file_path, abs_path)
    #Remove original file
		remove(file_path)
		#Move new file
		move(abs_path, file_path)

	def delete_posp_table(self):
		try:
			deleted = self.posp_table.delete_many({})
			return deleted.deleted_count+" documents deleted successfully"
		except Exception as e:
			print(e)
			return False
		
	def compile_sm_posp_and_save_json(self):
		factory_sm_path = os.path.abspath("./smart_contract/posp_factory.sol")
		posp_sm_path = os.path.abspath("./smart_contract/posp.sol")

		cfactory_sol = compile_files(
			[factory_sm_path],
			output_values=['abi', 'bin'],
			solc_version="0.8.7"
		)

		cposp_sol = compile_files(
			[posp_sm_path],
			output_values=['abi', 'bin'],
			solc_version="0.8.7"
		)

		factory_id, factory_interface = cfactory_sol.popitem()
		posp_id, posp_interface = cfactory_sol.popitem()


		with open(f"smart_contract/posp_factory.json", "w") as f:
			f.write(json.dumps(factory_interface, indent=2))
	
		_posp_abi = {"abi":posp_interface["abi"]}
		with open(f"smart_contract/posp.json", "w") as f:
			f.write(json.dumps(_posp_abi, indent=2))

		return True


	def deploy_factory_smartcontract(self):
		factory_abi = self.FACTORY_JSONINTERFACE["abi"]
		factory_bytecode = self.FACTORY_JSONINTERFACE["bin"]
		factory_sm = self.w3.eth.contract(abi=factory_abi, bytecode = factory_bytecode)
		tx_hash = factory_sm.constructor().buildTransaction({
			'from':self.account.address,
			'nonce': self.w3.eth.getTransactionCount(self.account.address),
		})
		signed = self.w3.eth.account.signTransaction(tx_hash, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		sm_deployed = self.w3.eth.sendRawTransaction(signed.rawTransaction)
		sm_address = self.w3.eth.waitForTransactionReceipt(sm_deployed)
		return sm_address.contractAddress

	def save_posp_factory_sm_env(self, sm_address):
		file_path = os.path.abspath("./.env")
		fh, abs_path = mkstemp()
		with fdopen(fh,'w') as new_file:
			with open(file_path, "r") as old_file:
				for line in old_file:
					if line.startswith("TEST_POSP_FACTORY_CONTRACT"):
						new_file.write('TEST_POSP_FACTORY_CONTRACT = "'+sm_address+'"\n')
					else:
						new_file.write(line)
		copymode(file_path, abs_path)
    #Remove original file
		remove(file_path)
		#Move new file
		move(abs_path, file_path)


	def delete_ancestry_table(self):
		try:
			deleted = self.ancestry_table.delete_many({})
			return deleted.deleted_count+" documents deleted successfully"
		except Exception as e:
			print(e)
			return False

		





	def load_smart_contract(self,path):
					solcOutput = {}
					try:
							with open(path) as inFile:
									solcOutput = json.load(inFile)
					except Exception as e:
							print(f"ERROR: Could not load file {path}: {e}")
					return solcOutput