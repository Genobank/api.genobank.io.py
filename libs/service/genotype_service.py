from libs.dao import genotype_dao
from libs.exceptions import DomainInjectionError
from libs.domain import Encryption



class genotype_service:
  def __init__(self, _genotype):
    if not isinstance(_genotype, genotype_dao.genotype_dao):
      raise DomainInjectionError.DomainInjectionError("genotype_service", "genotype")
    self.genotype = _genotype
    self.encryption = Encryption.Encryption()


  def create(self, data, file):
    file_name = self.genotype.save_file(file)
    if not file_name:
      raise Exception("Error saving file")
    data["filename"] = file_name
    self.genotype.mint_nft(data)
    return file_name