import hmac
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
import zipfile
import gzip
import io
import binascii
import re
import web3
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
		self.buckets_table = self.db.buckets
		self.ancestry_table = self.db.ancestry

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
				"labaddr": str(data["labAddress"]).upper(),
				"owneraddr": str(data["userAddress"]).upper(),
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
				"stake_nfts":{},
				"created": datetime.datetime.now(),
				"updated": datetime.datetime.now()
			}
			self.table.insert_one(_fields)
			return True
		except:
			raise

	def find_ancestry_db(self, filename, owner, laboratory):
		cur = self.table.find_one({"filename":filename, "owner": re.compile(owner, re.IGNORECASE), "laboratory": re.compile(laboratory, re.IGNORECASE)})
		if not cur:
			return False
		return cur["results"]

	
	def save_ancestry_db(self, genotype_info, data):
		print("\n",genotype_info, data)





	def save_file(self, file, data):
		try:
			file.file.seek(0)
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

	def upload_file_to_bucket(self, dataset_file, file_name, permittee):
		cur = self.buckets_table.find_one({"permittee": re.compile(permittee, re.IGNORECASE)})
		if not cur:
			raise Exception("No permittee found for bucket")

		BUCKET_NAME = cur['bucket_name']
		ACCESS_KEY = cur['access_key_id']
		SECRET_KEY = cur['secret_access_key']

		dataset_file.file.seek(0)
		upload_file = dataset_file.file.read()

		s3_client = boto3.client(service_name='s3',
								aws_access_key_id=ACCESS_KEY,
								aws_secret_access_key=SECRET_KEY)
		try:
			print("Uploading...")
			file_name = str(file_name)
			response = s3_client.upload_fileobj(io.BytesIO(upload_file), BUCKET_NAME, file_name)
			print("Bucket response",response)
			# response = s3_client.upload_file("storage/genotypes/"+file_name, bucket, object_name)
			# return response
		except ClientError as e:
			print(e)
			logging.error(e)
			return False
		return True

	def download_file_from_bucket(self, permittee, file_name):
		cur = self.buckets_table.find_one({"permittee": re.compile(permittee, re.IGNORECASE)})
		if not cur:
			raise Exception("No permittee found for bucket")


		BUCKET_NAME = cur['bucket_name']
		ACCESS_KEY = cur['access_key_id']
		SECRET_KEY = cur['secret_access_key']

		s3 = boto3.resource(service_name='s3',
								aws_access_key_id=ACCESS_KEY,
								aws_secret_access_key=SECRET_KEY)

		s3_client = boto3.client(service_name='s3',
								aws_access_key_id=ACCESS_KEY,
								aws_secret_access_key=SECRET_KEY)

		my_bucket = s3.Bucket(BUCKET_NAME)
		file_key = 'results-test/json/'+file_name+'.json'
		print(file_name)


		response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
		data = response['Body'].read()
		print(response)
		print(data)



		# with open('filename', 'wb') as test_result:
		# 	s3_client.download_fileobj(BUCKET_NAME, "results-test/json/"+file_name+".json", test_result)
		# 	print(test_result)
		# 	return test_result

		# print(file_bucket_path)

		# # to download fileobj
		# with open(file_name, 'wb') as data:
		# 	s3_client.download_fileobj(BUCKET_NAME, file_bucket_path, data)
		# 	print("DATA\n",data)

		# s3_client.download_file(BUCKET_NAME, file_bucket_path, 'suarchivo.txt')
		# print("\n",open('my_localfile.txt').read(),"\n")

		



	def list_bucket_files(self, permittee, file_name):
		cur = self.buckets_table.find_one({"permittee": re.compile(permittee, re.IGNORECASE)})
		if not cur:
			raise Exception("No permittee found for bucket")

		BUCKET_NAME = cur['bucket_name']
		ACCESS_KEY = cur['access_key_id']
		SECRET_KEY = cur['secret_access_key']

		s3 = boto3.resource(service_name='s3',
								aws_access_key_id=ACCESS_KEY,
								aws_secret_access_key=SECRET_KEY)
		
		s3_client = boto3.client(service_name='s3',
								aws_access_key_id=ACCESS_KEY,
								aws_secret_access_key=SECRET_KEY)

		my_bucket = s3.Bucket(BUCKET_NAME)
		if not file_name:
			# to see all
			for my_bucket_object in my_bucket.objects.all():
				print(my_bucket_object.key)
		else:
			# to download file
			s3_client.download_file(BUCKET_NAME, file_name, 'suarchivo.txt')
			print("\n",open('my_localfile.txt').read(),"\n")
		# # to see in a specific folder
		# for my_bucket_object in my_bucket.objects.filter(Prefix="logs/"):
		# 	print(my_bucket_object.key)
		

		

		# to download fileobj
		# with open('filename', 'wb')as data:
		# 	s3_client.download_fileobj('somos-genobank', 'genotypes/1b826255-e0b8-4aa9-bbf5-a2826aa634b6.txt', data)
		# 	print("DATA\n",data)


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
			cur = collection.find({"owneraddr": re.compile(owner, re.IGNORECASE)})
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
			cur = collection.find({"labaddr": str(permittee).upper()})
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
			wallet_db = web3.Web3.toChecksumAddress(str(genotype_db["owneraddr"]))
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
			collection.update_one({"owneraddr":str(owner).upper()}, {"$set": {"status": False}})
			return {"transactionHash":tx}
		except:
			# print(e)
			raise

	def burn_bio_token(self, owner, permittee):
		owner = web3.Web3.toChecksumAddress(owner)
		permittee = web3.Web3.toChecksumAddress(permittee)
		contract = self.w3.eth.contract(address=os.getenv('TEST_BIOSAMPLE_COTRACT'), abi=self.SM_JSONINTERFACE['abi'])
		tx = contract.functions.burnToken(owner, permittee).buildTransaction({
			'nonce': self.w3.eth.getTransactionCount(self.account.address)
			})
		signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('BIOSAMPLE_EXECUTOR'))
		tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
		self.w3.eth.waitForTransactionReceipt(tx_hash)    
		print("tx hash\n",tx_hash.hex())
		return tx_hash.hex()

	# dtc validation section
	def Source(self, line):
		if "23andMe" in line:
			source = 0
		elif "Ancestry" in line:
			source = 1
		elif line.startswith("RSID"):
			source = 2
		elif "MyHeritage" in line:
			source = 3
		elif "Living DNA" in line:
			source = 4
		elif re.match("^#*[ \t]*rsid[, \t]*chr", line):
			source = 5
		elif "Genes for Good" in line:
			source = 6
		elif "PLINK" in line:
			source = 7
		else:
			source = -1
		return source

	def Is_zip(self, bytes_data):
		return zipfile.is_zipfile(bytes_data) 
		
	def Is_gzip(self, bytes_data):
		return binascii.hexlify(bytes_data[:2]) == b"1f8b"
		
	def Extract_source(self, a, decode=False):
		first_line = self.Read_line(a, decode)
		return self.Source(first_line)
			
	def Read_line(self, file, decode):
		if decode:
			return file.readline().decode("utf8")
		else:
			return file.readline()

	def Manejador(self, dtc):
		try:
			if self.Is_gzip(dtc):
				with gzip.open(io.BytesIO(dtc), "rb") as f1:
					source = self.Extract_source(f1,decode=True)
			elif self.Is_zip(dtc):
				with zipfile.ZipFile(io.BytesIO(dtc)) as z:
					namelist = z.namelist()[0]
					with z.open(namelist, "r") as f:
						source = self.Extract_source(f1,decode=True)
			else:
				file = io.BytesIO(dtc)
				source = self.Extract_source(file,decode=True)
			return source
		except:
			raise Exception("No valid File, upload a TXT dtc file, change your file and try again")

	def create_table(self, name):
		try:
			self.db.create_collection(name)
			return True
			# self.db[name].insert_one(fields)

			# # self.db.create_collection(name,{
			# #	 "labaddr": <String>,
			# #	 "owneraddr": <String>,
			# #	 "filename": <String>,
			# #	 "extension": <String>,
			# #	 "hash": <String>,
			# #	 "signature": <String>,
			# #	 "created": <Date>,
			# #	 "updated": <Date>
			# # })


			# return self.db.list_collection_names()

			# raise Exception("Failed to create new table, this methos is locked")
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

	def reset_wallet(self, file_name, user_addr, permittee_addr, secret):
		if not self.checkSecret(file_name, user_addr, permittee_addr, secret):
			raise Exception("You do not have permission to call this method.")
		# resetear los tokens en el smartcontract
		return "Validated"

	def checkSecret(self, f_name, usr_addr, pmtee_addr,  secret):
		try:
			secret = str(secret)
			message=f_name+usr_addr+pmtee_addr
			hmac1 = hmac.new(os.getenv('TEST_APP_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
			hmac1 = str(hmac1.hexdigest())
			print("mysecret", secret)
			return hmac1 == secret
		except Exception as e:
			raise e

	def check_generic_secret(self, message, secret):
		try:
			secret = str(secret)
			hmac1 = hmac.new(os.getenv('TEST_APP_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
			hmac1 = str(hmac1.hexdigest())
			return hmac1 == secret
		except Exception as e:
			raise e




	# WARNING ZONE, FOR TEST ONLY



	def insert_many(self, table_name, list_string):
		# list_json = list_json
		new_string = str(list_string)
		new_string = new_string[new_string.find('['):]
		list_json = json.loads(new_string)
		print(list_json)

		print(type(list_json))
		collection = self.db[table_name]
		x = collection.insert_many(list_json)
		# x = True
		return x
		
