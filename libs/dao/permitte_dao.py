
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
    # self.w3 = Web3(HTTPProvider(settings.PROVIDER))
    self.w3 = Web3(HTTPProvider(os.getenv('PROVIDER')))
    self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    self.account = self.w3.eth.account.privateKeyToAccount(os.getenv('ROOT_KEY_EXECUTOR'))

    self.SM_JSONINTERFACE = self.load_smart_contract(os.getenv('ABI_SM_PATH'))


    # self.con = con
    return None
  load_dotenv()
  

  def create_permittee(self, id, address, secret):
    my_address = web3.Web3.toChecksumAddress(address)
    if not self.checkPermitteeSecret(id, my_address, secret):
      raise Exception("Invalid secret")
    self.mint_permittee(id, my_address)






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


  def mint_permittee(self, id, address):
    wallet = self.w3.eth.account.privateKeyToAccount(os.getenv('ROOT_KEY_EXECUTOR')).address
    print("Executor wallet", wallet)
    int_id = int(id)
    contract_address = os.getenv('SMART_CONTRACT')

    token = self.w3.eth.contract(address=os.getenv('SMART_CONTRACT'), abi=self.SM_JSONINTERFACE['abi'])
    print("token", token)
    # createTokenId = int(wallet, 16)
    # add twelve zeros to the left of the id
    left_id = str(int_id).zfill(12)
    createTokenId = '0x000000000000' + left_id + wallet[2:]


    # tx = token.functions.mint(createTokenId, wallet, 'ACTIVE').buildTransaction({
    #     'nonce': self.w3.eth.getTransactionCount(self.account.address)
    # })
    
    # signed_tx = self.w3.eth.account.signTransaction(tx, private_key=os.getenv('ROOT_KEY_EXECUTOR'))
    # tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    # self.w3.eth.waitForTransactionReceipt(tx_hash)    
    # print("tx hash\n",tx_hash.hex())
    # return tx_hash.hex()