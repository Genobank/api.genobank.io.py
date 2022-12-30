
# from typing import Any
# import binascii
# from eth_utils import (
#     encode_hex,
#     is_bytes,
#     is_integer,
#     ValidationError,
# )







# def myfunc(signature_bytes: bytes = None):
#     validate_recoverable_signature_bytes(signature_bytes)
#     r = big_endian_to_int(signature_bytes[0:32])
#     s = big_endian_to_int(signature_bytes[32:64])
#     v = ord(signature_bytes[64:65])
#     print("v",v)
#     print("r",r)
#     print("s",s)

# def validate_recoverable_signature_bytes(value: Any) -> None:
#     validate_bytes(value)
#     validate_bytes_length(value, 65, "recoverable signature")

# def validate_bytes(value: Any) -> None:
#     if not is_bytes(value):
#         raise ValidationError("Value must be a byte string.  Got: {0}".format(type(value)))

# def validate_bytes_length(value: bytes, expected_length: int, name: str) -> None:
#     actual_length = len(value)
#     if actual_length != expected_length:
#         raise ValidationError(
#             "Unexpected {name} length: Expected {expected_length}, but got {actual_length} "
#             "bytes".format(
#                 name=name,
#                 expected_length=expected_length,
#                 actual_length=actual_length,
#             )
#         )

# def big_endian_to_int(value: bytes) -> int:
#     return int.from_bytes(value, "big")



# if __name__ == "__main__":
#     valid_signature = '6f0156091cbe912f2d5d1215cc3cd81c0963c8839b93af60e0921b61a19c54300c71006dd93f3508c432daca21db0095f4b16542782b7986f48a5d0ae3c583d401'
#     invalid_signature = 'd6d0eed0ea8079b8bc3b6c5e91e62662e5ecb7e89987f6df9cb74d3d11fd64dd32600a55560e55c972e4c23aa4450dcb6bc8e9a8aacb218992bebf6a5921bb051c'

#     print(valid_signature)
#     print(invalid_signature)


#     myfunc(binascii.unhexlify(valid_signature))
#     # myfunc(binascii.unhexlify(invalid_signature))


from eth_keys import keys
import binascii

from web3 import Web3, HTTPProvider
import web3

w3 = Web3(HTTPProvider("https://api.avax-test.network/ext/bc/C/rpc"))



valid_signature = '6f0156091cbe912f2d5d1215cc3cd81c0963c8839b93af60e0921b61a19c54300c71006dd93f3508c432daca21db0095f4b16542782b7986f48a5d0ae3c583d401'
# invalid_signature = binascii.unhexlify('d6d0eed0ea8079b8bc3b6c5e91e62662e5ecb7e89987f6df9cb74d3d11fd64dd32600a55560e55c972e4c23aa4450dcb6bc8e9a8aacb218992bebf6a5921bb051c')
invalid_signature = 'd6d0eed0ea8079b8bc3b6c5e91e62662e5ecb7e89987f6df9cb74d3d11fd64dd32600a55560e55c972e4c23aa4450dcb6bc8e9a8aacb218992bebf6a5921bb051c'


print(binascii.unhexlify(valid_signature))
sig = Web3.toBytes(hexstr=valid_signature)
print(sig)

(v, r, s) = Web3.toInt(sig[-1]), Web3.toHex(sig[:32]), Web3.toHex(sig[32:64])

print(v, r, s)
# print(valid_signature)
# print(invalid_signature)

# (v, r, s) = keys.Signature(signature_bytes=invalid_signature).vrs

# print(v, r, s)