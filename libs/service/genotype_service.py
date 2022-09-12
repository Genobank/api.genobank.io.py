# from re import T
from time import sleep
from cryptography.fernet import Fernet
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

  # obsolete method
  def create(self, data, file):
    data["filename"] = str(uuid.uuid4())
    data["key"] = Fernet.generate_key()
    token_hash = self.genotype.mint_nft(data)
    if not token_hash:
      raise Exception("Error minting token")
    data["token_hash"] = token_hash
    save_db_file = self.genotype.save_db_file(data)
    if not save_db_file:
      raise Exception("Error saving file in database")
    file_name = self.genotype.save_file(file, data)
    if not file_name:
      raise Exception("Error saving file")
    # add boto to upload to the bucket
    # bucket_send = self.genotype.upload_file_to_bucket(data["filename"]+"."+data["extension"], "somos-genobank")
    # if not bucket_send:
    #   raise Exception("Error uploading file to bucket")
    return {"token": token_hash}


  # Partitionated methos
  def mint_nft(self, data):
    data["filename"] = str(uuid.uuid4())
    data["key"] = str(Fernet.generate_key())
    token_hash = self.genotype.mint_nft(data)
    if not token_hash:
      raise Exception("Error minting token")
    data["token_hash"] = token_hash
    return data

  def save_db_file(self, data):
    save_db_file = self.genotype.save_db_file(data)
    if not save_db_file:
      raise Exception("Error saving file in database")
    return data

  def storage_file(self, data, file):
    file_name = self.genotype.save_file(file, data)
    if not file_name:
      raise Exception("Error saving file")
    return {"token":data["token_hash"]}



  def validate_consents_metadata(self, data):
    if "agreements" not in data:
      raise Exception("Invalid consent metadata")
    agreements = data['agreements']
    if "questions" not in agreements:
      raise Exception("question is required for consent metadata")
    if "document" not in agreements:
      raise Exception("document is required for consent metadata")
    if "read" not in agreements:
      raise Exception("read is required for consent metadata")
    if "permission" not in agreements:
      raise Exception("permission is required for consent metadata")
    if "providing" not in agreements:
      raise Exception("providing is required for consent metadata")
    if "analysis" not in agreements:
      raise Exception("analysis is required for consent metadata")
    if "results" not in agreements:
      raise Exception("results is required for consent metadata")


# ONLY TEST PURPOSES
  def test_process_1(self):
    sleep(1)
    return "1 second waited"
  
  def test_process_2(self):
    sleep(5)
    return "1 second waited"

  def test_process_3(self):
    sleep(3)
    return "1 second waited"
    

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

  def find_by_permittee_only_basic_data(self, _permittee):
    genotype = self.genotype.find_genotype_by_permittee(_permittee)
    if not genotype:
      return {}
    for index in genotype:
      if "_id" in index: del index["_id"]
      if "filesigned" in index: del index["filesigned"]
      if "hash" in index: del index["hash"]
      if "signature" in index: del index["signature"]
      if "key" in index: del index["key"]
      if "updated" in index: del index["updated"]
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
    _json["lab"] = _genotype["labaddr"]
    _json["status"] = _genotype["status"]
    _json["filesize"] = _genotype["filesize"]
    _json["consents"] = _genotype["consents"]

    return _json

  def authorize_download(self, wallet, signature):
    # signature = data["signature"]
    # wallet = data["wallet"]
    # # message = signature+wallet
    # # mark_key = hmac.new(signature.encode('utf-8'),msg=message.encode(), digestmod="sha256")

    validation, name, ext= self.genotype.verify_signature(wallet, signature)
    if not validation:
      raise Exception("Invalid signature")
    return name, ext

  def real_validation(self, signature, msg, permittee):
    valid = self.genotype.real_validation(signature, msg, permittee)
    if not valid:
      raise Exception("You permittee is not valid")
    return valid

  def is_file_enable(self, file_name):
    is_enable = self.genotype.is_file_enable(file_name)
    if not is_enable:
      raise Exception("This file has consents revoked")
    return is_enable

  def download_file(self, file_name, file_ext):
    file = self.genotype.download_file(file_name, file_ext)
    # if not file:
    #   raise Exception("Couldn't find file")
    return file

  def revoke_consents(self, owner, signature, permittee):
    authorized, name, ext= self.genotype.verify_signature(owner, signature)
    if not authorized:
      raise Exception("Invalid signature")
    revoked = self.genotype.revoke_consents(owner, permittee)
    # if not revoked:
    #   raise Exception("Couldn't revoke consent")
    return revoked


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