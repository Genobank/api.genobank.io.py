
from hmac import digest
from dotenv import load_dotenv

import os
import hashlib
import web3
import hmac



class permittee_dao:
  def __init__(self, con):
    self.con = con
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

  def checkPermitteeSecret(self, id, address, secret):
    try:
      # hmac1 = hmac.new(secret.encode('utf-8'), digestmod=hashlib.sha256)
      message=id+address
      hmac1 = hmac.new(os.getenv('APP_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
      return hmac1.hexdigest()
    except Exception as e:
      raise e


  def mint_permittee():
    return None