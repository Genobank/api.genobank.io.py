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
    file_name = self.genotype.save_file(file, data)
    if not file_name:
      raise Exception("Error saving file")
    return {"token": token_hash}

  def validate_permitte(self, id):
    resp = requests.get(
      os.getenv('API_PERMITTEES')+"{0}".format(id)
    )