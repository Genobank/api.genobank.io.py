from pymongo import MongoClient
import os, shutil
from web3 import Web3, HTTPProvider
from solcx import compile_source
from solcx import compile_files
import json


class restore_api_dao:
	def __init__(self):
		self.w3 = Web3(HTTPProvider(os.getenv('BIOSAMPLE_PROVIDER')))
		self.account = self.w3.eth.account.privateKeyToAccount(os.getenv('BIOSAMPLE_EXECUTOR'))
		self.w3.eth.default_account = self.account.address

		self.client = MongoClient(os.getenv('TEST_MONGO_DB_HOST'))
		self.db = self.client[os.getenv('TEST_DB_NAME')]
		self.genotypes_table = self.db.genotypes
		self.posp_table = self.db.posp
		
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
			# print(file_path)
			try:
				if os.path.isfile(file_path) or os.path.islink(file_path):
					os.unlink(file_path)
				# elif os.path.isdir(file_path):
				# 	shutil.rmtree(file_path)
			except Exception as e:
				print('Failed to delete %s. Reason: %s' % (file_path, e))

	def compile_sm_genotypes_and_save(self):
		solidity_sm_path = os.path.abspath("./smart_contract/genotype.sol")
		# with open(solidity_sm_path, 'rb') as enc_file:
		# 	sm_content = enc_file.read()
		# compiled_sol = compile_source(sm_content,output_values=['abi', 'bin'])
		compiled_sol = compile_files(
			[solidity_sm_path],
			output_values=['abi', 'bin'],
			solc_version="0.8.9"
		)

		contract_id, contract_interface = compiled_sol.popitem()

		abi = contract_interface['abi']

		print(abi)

		# compiled_sol = json.dumps(compiled_sol)

		with open(f"smart_contract/Biosample.json", "w") as f:
			f.write("""{"abi":"""+json.dumps(abi) +"""}""")

		# print(type(compiled_sol))

