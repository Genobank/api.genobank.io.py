from re import T
from libs.dao import genotype_dao
from libs.exceptions import DomainInjectionError
from libs.domain import Encryption

import requests
import os
import uuid


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