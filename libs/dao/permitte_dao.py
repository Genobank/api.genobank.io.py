
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



    # self.con = con
    return None
  load_dotenv()
  

  def create_permittee(self, id, address, secret):
    try:
      my_address = web3.Web3.toChecksumAddress(address)
      print("my_address",my_address)
      if not self.checkPermitteeSecret(id, my_address, secret):
        raise Exception("Invalid secret")
      token_hash = self.mint_permittee(id, my_address)
      if not token_hash:
        raise Exception("Could not mint permittee")
      created = self.insert_in_database(int(id), my_address, token_hash)
      if created:
        return created
      else:
        return False
    except Exception as e:
      raise e

  def insert_in_database(self, id, address, tx_hash):
    try:
      int_id = int(id)
      left_id = str(int_id).zfill(12)
      token_id = '0x000000000000' + left_id + self.account.address[2:]

      _fields = {
			'serial': id,
			'actor': self.account.address,
			'owner': address,
			'status': 'ACTIVE',
			'tokenId': token_id,
      'createdAt': datetime.datetime.now(),
      'updatedAt': datetime.datetime.now(),
			'txHash': '0x' + tx_hash,
			'sequenceIndicator': 2
			}

      x = self.db.permittees.insert_one(_fields)
      return x.inserted_id
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
      left_id = str(int_id).zfill(12)
      createTokenId = '0x000000000000' + left_id + self.account.address[2:]

      id_token = int(createTokenId, 16)

      tx = token.functions.mint(id_token, address, 'ACTIVE').buildTransaction({
            'from': self.account.address,
            'nonce': self.w3.eth.getTransactionCount(self.account.address)
      })

      signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('ROOT_KEY_EXECUTOR'))
      tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
      tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)    
      return tx_hash.hex()
    except:#Exception as e:
      raise
      # if e.args[0]['code'] < 0:
      #   time.sleep(5)
      #   return self.mint_permittee(id, address)
      # else:
      #   msg = ""
      #   if 'message' in e.args[0]:
      #     msg = str(e.args[0]['message'])
      #   else:
      #     msg = str(e)
      #   raise Exception(msg)



  def delete_permittee(self, id):
    try:
      id = int(id)
      self.db.permittees.delete_one({"serial": id})
      return True
    except Exception as e:
      raise e
    
  def testing_mogo_db(self):
    try:
      collection = self.db.permittees
      cur = collection.find()
      row = []
      for doc in cur:
        row.append(doc)
        print(doc)
    except Exception as e:
      print(e)
      return False