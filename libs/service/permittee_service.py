from re import S
from urllib import response
from libs.domain import Encryption
from libs.dao import permitte_dao as dao
from libs.exceptions import DomainInjectionError
from dotenv import load_dotenv

import requests
import os



class permittee_service:
  def __init__(self, _permittee):
    if not isinstance(_permittee, dao.permittee_dao):
      raise DomainInjectionError.DomainInjectionError("genotype_service", "genotype")
    self.permittee = _permittee
    self.encryption = Encryption.Encryption()
  
  load_dotenv()

  def create_permittee(self, id, address, secret):
    try:
      resp = requests.get(
        os.getenv('API_PERMITTEES')+"{0}".format(id)
        )
      print(resp.status_code)
      if resp.status_code != 200 and resp.status_code != 400:
        raise Exception("Failed to create new permittee, please try again later")
      elif resp.status_code == 200:
        return False, "Permittee ID #" + id + " was already registered."
      elif resp.status_code == 400:
        created = self.permittee.create_permittee(id, address, secret)
        if not created:
          raise Exception("Failed to create new permittee, please try again later")
        return created
    except:
      raise
  
  
  def delete_permittee(self, id):
    return self.permittee.delete_permittee(id)


  def testing_mongo_db(self):
    return self.permittee.testing_mogo_db()

  def find_all_by_table(self, table):
    if table == None or table == "":
      tables = self.permittee.get_list_collection_names()
      return {"Requires table name":tables}
    else:
      search = self.permittee.find_all_by_table(table)
      if not search:
        return []
    return search

    

  