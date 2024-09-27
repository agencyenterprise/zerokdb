from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

def sign_message(message: str, private_key: bytes):
  key = RSA.import_key(private_key)

  digest = SHA256.new()
  digest.update(message.encode('utf-8'))

  signer = PKCS1_v1_5.new(key)
  sig = signer.sign(digest)

  return sig.hex()
