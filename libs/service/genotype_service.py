from re import T
from libs.dao import genotype_dao
from libs.exceptions import DomainInjectionError
from libs.domain import Encryption

import requests
import os
import uuid
import hmac



class genotype_service:
  def __init__(self, _genotype):
    if not isinstance(_genotype, genotype_dao.genotype_dao):
      raise DomainInjectionError.DomainInjectionError("genotype_service", "genotype")
    self.genotype = _genotype
    self.encryption = Encryption.Encryption()

  def create(self, data, file):
    data["filename"] = str(uuid.uuid4())
    token_hash = self.genotype.mint_nft(data)
    if not token_hash:
      raise Exception("Error minting token")
    data["token_hash"] = token_hash
    print("\n\n\n\n\n\n",data,"\n\n\n\n\n\n")
    save_db_file = self.genotype.save_db_file(data)
    if not save_db_file:
      raise Exception("Error saving file in database")
    file_name = self.genotype.save_file(file, data)
    if not file_name:
      raise Exception("Error saving file")
    return {"token": token_hash}

  def find_by_owner(self, owner):
    genotype = self.genotype.find_genotype_by_owner(owner)
    if not genotype:
      return {}
    return genotype

  def find_by_permittee(self, owner):
    genotype = self.genotype.find_genotype_by_permittee(owner)
    if not genotype:
      return {}
    return genotype

  def list_to_json(self, gen_list):
    _json = {}
    for gen in gen_list:
      for key in gen:
        _json[key] = gen[key]


  def basic_reference(self, _genotype):
    if not _genotype:
      return []
      raise Exception("Couldn't find genotype with the given name")
    _json = {}
    _json["name"] = _genotype["filename"]
    _json["ext"] = _genotype["extension"]

    return _json

  def authorize_download(self, wallet, signature):
    # signature = data["signature"]
    # wallet = data["wallet"]
    # # message = signature+wallet
    # # mark_key = hmac.new(signature.encode('utf-8'),msg=message.encode(), digestmod="sha256")
    validation, name, ext= self.genotype.verify_signature(wallet, signature)
    if not validation:
      print("\n\n\n\n\n\n THIS FILE HAS NO VALIDATION SIGNATURE\n\n\n\n\n\n\n\n")
      raise Exception("Invalid signature")
    return name, ext

  def download_file(self, file_name, file_ext):
    file = self.genotype.download_file(file_name, file_ext)
    if not file:
      raise Exception("Couldn't find file")
    return file

  def checkPermitteeSecret(self, id, address, secret):
    try:
      secret = str(secret)
      message=id+address
      hmac1 = hmac.new(os.getenv('TEST_APP_SECRET').encode('utf-8'),msg=message.encode(), digestmod="sha256")
      hmac1 = str(hmac1.hexdigest())

      return hmac1 == secret
    except Exception as e:
      raise e

  def validate_permitte(self, id):
    resp = requests.get(
      os.getenv('API_PERMITTEES')+"{0}".format(id)
    )

  def create_table(self, name, fields):
    created = self.genotype.create_table(name, fields)
    if not created:
      raise Exception("Failed to create new table, please try again later")
    return created

  def find_all_by_table(self, table):
    if table == None or table == "":
      tables = self.genotype.get_list_collection_names()
      return {"Requires table name":tables}
    else:
      search = self.genotype.find_all_by_table(table)
      if not search:
        return []
    return search

  
  # WARNIGN ZONE, FRO TEST ONLY
  def delete_table(self):
    deleted = self.genotype.delete_table()
    if not deleted:
      raise Exception("Failed to delete table, please try again later")
    return deleted