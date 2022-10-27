from dotenv import load_dotenv
from pymongo import MongoClient
import json
import os, os.path
# from datetime import datetime
import datetime


class licence_dao:
	def __init__(self):
		self.client = MongoClient(os.getenv('TEST_MONGO_DB_HOST'))
		self.db = self.client[os.getenv('TEST_DB_NAME')]
		self.table = self.db.licenses
		
	def create_licence (self, licence_metadata):
		try:
			licence_metadata = json.loads(licence_metadata)
			licence_details = self.get_licence_details(int(licence_metadata["type"]))

			_fields = {
				"owner": str(licence_metadata["owner"]).upper(),
				"type": licence_metadata["type"],
				"name": licence_details["name"],
				"code": licence_details["code"],
				"created": str(datetime.datetime.now()),
				"updated": str(datetime.datetime.now()),
				"expiration": str(datetime.datetime.fromtimestamp(licence_metadata["expiration"]))
			}

			self.table.insert_one(_fields)
			# self.table.drop()


			return _fields
		except:
			raise

	def get_licence_details(self, type):
		_licences = [
			{},
			{"name": "ANCESTRY", "code": "ACTRY"},
			{"name": "PROOF OF STAKE PROTOCOL", "code": "POSP"},
		]
		return _licences[type]

	# def find_license
