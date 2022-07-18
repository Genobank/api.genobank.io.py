
from hmac import digest
from dotenv import load_dotenv

import os
import web3
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
import hmac
import json




class permittee_dao:
  def __init__(self):
    self.w3 = Web3(HTTPProvider(settings.PROVIDER))
    self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    self.account = self.w3.eth.account.privateKeyToAccount(os.getenv('ROOT_KEY'))

    self.SM_JSONINTERFACE = self.load_smart_contract(os.getenv('ABI_SM_PATH'))


    # self.con = con
    return None
  load_dotenv()
  

  def create_permittee(self, id, address, secret):

    # create a web3 address object
    my_address = web3.Web3.toChecksumAddress(address)
    
    # print(type()my_address)


    # # we need to insert in a mongo db
    # receiver_address = "0x" + address
    # permitte_id = id
    if not self.checkPermitteeSecret(id, my_address, secret):
      raise Exception("Invalid secret")


    # try:
    #   self.con.insert_one({
    #     'id': id,
    #     'address': address,
    #     'secret': secret
    #   })
    #   return True
    # except Exception as e:
    #   print(e)
    #   return False


  def load_smart_contract(self,path):
        solcOutput = {}
        try:
            with open(path) as inFile:
                solcOutput = json.load(inFile)
        except Exception as e:
            print(f"ERROR: Could not load file {path}: {e}")
        return solcOutput


  def checkPermitteeSecret(self, id, address, secret):
    try:
      # hmac1 = hmac.new(secret.encode('utf-8'), digestmod=hashlib.sha256)
      message=id+address
      hmac1 = hmac.new(os.getenv('APP_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
      return hmac1.hexdigest()
    except Exception as e:
      raise e


  def mint_permittee(self, metadata):
    wallet = metadata["wallet"]
    contract = self.w3.eth.contract(address=os.getenv('SMART_CONTRACT'), abi=self.SM_JSONINTERFACE['abi'])
    id_address = int(wallet, 16)
    # tx = contract.functions.mint(id_address, wallet, 'ACTIVE').buildTransaction({
    #     'nonce': self.w3.eth.getTransactionCount(self.account.address)
    # })

    tx = contract.functions.paid_mint(id_address, wallet, 'ACTIVE').buildTransaction({
        'nonce': self.w3.eth.getTransactionCount(self.account.address)
    })
    signed_tx = self.w3.eth.account.signTransaction(tx, private_key=settings.ROOT_KEY)
    tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    self.w3.eth.waitForTransactionReceipt(tx_hash)    
    print("tx hash\n",tx_hash.hex())
    return tx_hash.hex()