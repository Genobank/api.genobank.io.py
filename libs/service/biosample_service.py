from libs.dao import biosample_dao
from libs.exceptions import DomainInjectionError
import hmac
import os



class biosample_service:
	def __init__(self, _biosample,):
		if not isinstance(_biosample, biosample_dao.biosample_dao):
			raise DomainInjectionError.DomainInjectionError("genotype_service", "genotype")		
		self.biosample = _biosample
			
	def claim(self, token_id, data):
		if not token_id:
			raise Exception("Invalid token_id")
		return self.biosample.claim(token_id, data)
