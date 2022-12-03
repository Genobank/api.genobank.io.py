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
		self.restore_api.delete_genotypes_table()
		print("[1] Genotype table cleaned...................................................... [OK]")

		self.restore_api.delete_genotypes_file()
		print("[2] Deleted genotypes files .................................................... [OK]")

		abi = self.restore_api.compile_sm_genotypes_and_save_json()
		print("[3] New SM_genotypes compiled an JSONInterface Saved ........................... [OK]")

		genotype_sm_address = self.restore_api.deploy_genotype_smartcontract()
		print("[4] Genoype SM Deployed at", genotype_sm_address, ".......... [OK]")

		self.restore_api.save_genotype_sm_env(genotype_sm_address)
		print("[5] Genoype SM ENVIROMENT added ................................................ [OK]")

		self.restore_api.delete_posp_table()
		print("[6] Posp table deleted ......................................................... [OK]")

		abi = self.restore_api.compile_sm_posp_and_save_json()
		print("[7] New posp factory and posp token compiled an JSONInterface Saved ............ [OK]")

		factory_sm_address = self.restore_api.deploy_factory_smartcontract()
		print("[8] POSP Factory SM Deployed at", factory_sm_address, "..... [OK]")

		self.restore_api.save_posp_factory_sm_env(factory_sm_address)
		print("[9] POSP Factory SM ENVIROMENT added ........................................... [OK]")

		self.restore_api.delete_ancestry_table()
		print("[10] Ancestry Table deleted ..................................................... [OK]")

		self.restore_api.delete_files_table()
		print("[11] Files Table deleted ........................................................ [OK]")

		
		print("\n\nALL API RESTORED SUCCESSFULLY!!!\n\n")


	 
		# os.system('clear')
		# self.genotype_service.delete_table()
		# print("Table cleaned [OK]")