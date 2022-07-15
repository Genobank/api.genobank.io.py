from libs.exceptions import UserDomainError
from settings import settings
from cryptography.fernet import Fernet

class Encryption:


    def secure_key(self,data):
        try:
            cipher_suite = Fernet(settings.KEY)
            bytes_from_data = bytes(data, 'utf-8')
            encrypted_data = (cipher_suite.encrypt(bytes_from_data)).decode("utf-8")
            return encrypted_data
        except:
            raise Exception("\n\n [ !!! ] Error encrypting data\n")


    def decrypt_key(self,secured_data):
        try:
            cipher_suite = Fernet(settings.KEY)
            decrypted_data = cipher_suite.decrypt(bytes(secured_data, 'utf-8'))
            data_from_bytes = decrypted_data.decode("utf-8")
            return data_from_bytes
        except:
            raise Exception("\n\n [ !!! ] Error decrypting secure data\n")


#Avocado Blockchain Services at Merida Yucatan