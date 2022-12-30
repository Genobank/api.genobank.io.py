from web3.auto import w3
from eth_account.messages import encode_defunct
import datetime




private_key = "<privated key>"
msg = "Hola"
message = encode_defunct(text=msg)
signed_message = w3.eth.account.sign_message(message, private_key=private_key)
now = datetime.datetime.now()
time_stamp = datetime.datetime.timestamp(now)



print(signed_message.messageHash.hex())
print(signed_message.signature.hex())

print(time_stamp)