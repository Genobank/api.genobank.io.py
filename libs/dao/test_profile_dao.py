from pymongo import MongoClient
import os

class test_permittee_dao:
  def __init__(self):
    # self.w3 = Web3(HTTPProvider(settings.PROVIDER))

    self.client = MongoClient(os.getenv('TEST_MONGO_DB_HOST'))
    self.db = self.client[os.getenv('TEST_DB_NAME')]
    return None

  def get_profile_by_serial(self, serial):
    pass