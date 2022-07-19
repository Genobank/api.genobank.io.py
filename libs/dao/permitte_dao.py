
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
      if not self.checkPermitteeSecret(id, my_address, secret):
        raise Exception("Invalid secret")
      minted, tokenId = self.mint_permittee(id, my_address)
      if not minted:
        raise Exception("Could not mint permittee")

      return self.insert_in_database(int(id), my_address, tokenId, minted)
    except Exception as e:
      raise e

  def insert_in_database(self, id, address, token_id, tx_hash):
    try:
      # int_id = int(id)
      # left_id = str(int_id).zfill(12)
      # token_id = '0x000000000000' + left_id + self.account.address[2:]

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
      # hmac1 = hmac.new(secret.encode('utf-8'), digestmod=hashlib.sha256)
      secret = str(secret)
      message=id+address
      hmac1 = hmac.new(os.getenv('APP_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
      hmac1 = str(hmac1.hexdigest())

      return hmac1 == secret
    except Exception as e:
      raise e


  async def mint_permittee(self, id, address):
    try:
      wallet = self.w3.eth.account.privateKeyToAccount(os.getenv('ROOT_KEY_EXECUTOR')).address
      int_id = int(id)
      contract_address = os.getenv('SMART_CONTRACT')
      token = self.w3.eth.contract(address=contract_address, abi=self.SM_JSONINTERFACE['abi'])
      left_id = str(int_id).zfill(12)
      createTokenId = '0x000000000000' + left_id + self.account.address[2:]

      id_token = int(createTokenId, 16)
      #  createTokenId = int(self.account.address, 16)

      tx = token.functions.mint(id_token, address, 'ACTIVE').buildTransaction({
            'from': self.account.address,
            'nonce': self.w3.eth.getTransactionCount(self.account.address),
      })

      signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('ROOT_KEY_EXECUTOR'))
      tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
      print("tx hash\n",tx_hash.hex())
      return tx_hash.hex(), createTokenId
    except:
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
      collection = self.db.permittees
      cur = collection.find()
      row = []
      for doc in cur:
        row.append(doc)
        print(doc)
    except Exception as e:
      print(e)
      return False