
from hmac import digest
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from pymongo import MongoClient


import os
import web3
import hmac
import json
import datetime
import time



class permittee_dao:
  def __init__(self):
    # self.w3 = Web3(HTTPProvider(settings.PROVIDER))

    self.client = MongoClient(os.getenv('MONGO_DB_HOST'))
    self.db = self.client[os.getenv('DB_NAME')]
    self.w3 = Web3(HTTPProvider(os.getenv('PROVIDER')))
    self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    self.account = self.w3.eth.account.privateKeyToAccount(os.getenv('ROOT_KEY_EXECUTOR'))

    self.SM_JSONINTERFACE = self.load_smart_contract(os.getenv('ABI_SM_PATH'))
    
    return None
  # load_dotenv()

    
  

  def create_permittee(self, id, address, secret):
    try:
      my_address = web3.Web3.toChecksumAddress(address)
      if not self.checkPermitteeSecret(id, my_address, secret):
        raise Exception("Invalid secret")
      token_hash = self.mint_permittee(id, my_address)
      if not token_hash:
        raise Exception("Could not mint permittee")
      created = self.save_and_insert_in_DB(int(id), my_address, token_hash)

      # token_hash = "0xsoikgfjsodjfosdfjosñdjfsidjfsidjfMIO"
      # created = True

      if created:
        return {"data":[{"transactionHash": token_hash}]}
      else:
        return {"data":[{"transactionHash": token_hash}], "warning": "lo saved"}
    except Exception as e:
      raise e

  
  # open file, add new line, write to file
  def add_new_line(self, new_line):
    try:
      for key in new_line:
        print(key, new_line[key])
        if (not isinstance(new_line[key], str)) or (not isinstance(new_line[key], int)) or (not isinstance(new_line[key], float)):
          new_line[key] = str(new_line[key])
      with open(os.getenv('PERMITEE_INSERTS'), 'a') as f:
        f.write(json.dumps(new_line)+',\n')
      return True
    except Exception as e:
      print(e)
      return False
      

  def save_and_insert_in_DB(self, id, address, tx_hash):
    try:
      int_id = int(id)
      hex_id = hex(int_id)[2:]
      left_id = str(hex_id).zfill(12)
      token_id = '0x000000000000' + left_id + self.account.address[2:]

      _fields = {
			'serial': id,
			'actor': self.account.address,
			'owner': address,
			'status': 'ACTIVE',
			'tokenId': token_id,
      'createdAt': datetime.datetime.now(),
      'updatedAt': datetime.datetime.now(),
			'txHash': tx_hash,
			'sequenceIndicator': 1
			}

      # Save file locally
      return self.add_new_line(_fields)
      


      # # Insert in DB
      # x = self.db.permittees.insert_one(_fields)
      # return x.inserted_id
    except:
      raise

  def load_smart_contract(self,path):
        solc_output = {}
        try:
            with open(path) as inFile:
                solc_output = json.load(inFile)
        except Exception as e:
            print(f"ERROR: Could not load file {path}: {e}")
        return solc_output

  def checkPermitteeSecret(self, id, address, secret):
    try:
      secret = str(secret)
      message=id+address
      hmac1 = hmac.new(os.getenv('APP_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
      hmac1 = str(hmac1.hexdigest())

      return hmac1 == secret
    except Exception as e:
      raise e


  def mint_permittee(self, id, address):
    try:
      wallet = self.w3.eth.account.privateKeyToAccount(os.getenv('ROOT_KEY_EXECUTOR')).address
      int_id = int(id)
      contract_address = os.getenv('SMART_CONTRACT')
      token = self.w3.eth.contract(address=contract_address, abi=self.SM_JSONINTERFACE['abi'])
      hex_id = hex(int_id)[2:]
      left_id = str(hex_id).zfill(12)
      createTokenId = '0x000000000000' + left_id + self.account.address[2:]

      id_token = int(createTokenId, 16)

      tx = token.functions.mint(id_token, address, 'ACTIVE').buildTransaction({
            'from': self.account.address,
            'nonce': self.w3.eth.getTransactionCount(self.account.address)
      })
      print("tx: ", tx)
      signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('ROOT_KEY_EXECUTOR'))
      tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
      tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
      print("tx_receipt: ", tx_receipt)
      print("tx_hash: ", tx_hash)
      return tx_hash.hex()
    except:#Exception as e:
      raise



  def delete_permittee(self, id):
    try:
      id = int(id)
      self.db.permittees.delete_one({"serial": id})
      return True
    except Exception as e:
      raise e
    
  def testing_mogo_db(self):
    try:
      print(self.client.list_database_names())
      print(self.db.list_collection_names())
      collection = self.db.permittees
      cur = collection.find()
      _json = {}
      row = []
      for doc in cur:
        row.append(doc)
        print(doc)
      # return row
    except Exception as e:
      print(e)
      return False

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