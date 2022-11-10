from libs.dao import restore_api_dao

from libs.exceptions import DomainInjectionError
from libs.domain import Encryption

class restore_api_serivice:
	def __init__(self, _restore_api):
			if not isinstance(_restore_api, restore_api_dao.restore_api_dao):
				raise DomainInjectionError.DomainInjectionError("genotype_service", "genotype")
			self.restore_api = _restore_api
			self.encryption = Encryption.Encryption()


	def restore_api_service(self):
		# self.restore_api.delete_genotypes_table()
		# print("Genotype table cleaned [OK]")
		# self.restore_api.delete_genotypes_file()
		# print("Deleted genotypes files [OK]")
		abi = self.restore_api.compile_sm_genotypes_and_save()
		print("New SM_genotypes compiled [OK]")
		sm_address = self.deploy_genotype_smartcontract(abi)
		# self.save_sm_env(sm_address)

		# abi = self.coompile_sm_posp()
		# self.

	 
		# os.system('clear')
		# self.genotype_service.delete_table()
		# print("Table cleaned [OK]")