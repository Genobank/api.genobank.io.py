from math import perm
from re import S
from urllib import response
from libs.domain import Encryption
from libs.dao import test_permitte_dao as dao
from libs.exceptions import DomainInjectionError
from dotenv import load_dotenv

import requests
import os



class test_permittee_service:
  def __init__(self, _test_permittee):
    if not isinstance(_test_permittee, dao.test_permittee_dao):
      raise DomainInjectionError.DomainInjectionError("test_genotype_service", "genotype")
    self.test_permittee = _test_permittee
    self.encryption = Encryption.Encryption()

  def create_permittee(self, id, address, secret):
    try:
      resp = requests.get(
        os.getenv('TEST_API_PERMITTEES')+"{0}".format(id)
        )
      print(resp.status_code)
      if resp.status_code != 200 and resp.status_code != 400:
        raise Exception("Failed to create new permittee, please try again later")
      elif resp.status_code == 200:
        return False, "Permittee ID #" + id + " was already registered."
      elif resp.status_code == 400:
        created = self.test_permittee.create_permittee(id, address, secret)
        if not created:
          raise Exception("Failed to create new permittee, please try again later")
        return created
    except:
      raise


  def get_serial_from_address(self, address):
    serial = self.test_permittee.get_serial_from_address(address)
    if not serial:
      return[]
    return serial


  def validate_permittee(self, permittee):
    validated = self.test_permittee.validate_permittee(permittee)
    if not validated:
      return False
    # return validated
    return validated

  def basic_reference(self, _permittee):
    if not _permittee:
      return False
    _json = {}
    _json["public_address"] = _permittee["owner"]
    _json["id_number"] = _permittee["serial"]
    _json["status"] = _permittee["status"]
    return _json
  
  def is_permittee(self, permittee):
    permittee = self.test_permittee.validate_permittee(permittee)
    if not permittee:
      raise Exception("Address is no permittee")
    return permittee
    # if not permittee:
    #   return False
    # return True

# WARNING ZONE
  
  
  def delete_permittee(self, id):
    return self.test_permittee.delete_permittee(id)


  def testing_mongo_db(self):
    return self.test_permittee.testing_mogo_db()

  def find_all_by_table(self, table):
    if table == None or table == "":
      tables = self.test_permittee.get_list_collection_names()
      return {"Requires table name":tables}
    else:
      search = self.test_permittee.find_all_by_table(table)
      if not search:
        return []
    return search

    

  