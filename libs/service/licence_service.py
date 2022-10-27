from libs.dao import licences_dao
from libs.exceptions import DomainInjectionError
from libs.domain import Encryption

class licence_service:
	def __init__(self, _licence):
		if not isinstance(_licence, licences_dao.licence_dao):
			raise DomainInjectionError.DomainInjectionError("licence_service", "licence")
		self.licence = _licence
		self.encryption = Encryption.Encryption()

	def create_licence(self, metadata):
		licence_created = self.licence.create_licence(metadata)
		if not licence_created:
			raise Exception("Error during creation of licence")
		return licence_created



	
