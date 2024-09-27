import base64
import os

from services.hub_service import call_hub_post
from services.signature_service import sign_message

def register(public_key: bytes, private_key: bytes):
  try:
    message_data = {
      'public_key': base64.urlsafe_b64encode(public_key).decode()
    }
    message_response = call_hub_post("/auth/signature-messages", message_data)

    signature = sign_message(message_response['message'], private_key)

    worker_data = {
      'wallets': [{
        'wallet': os.getenv("WORKER_WALLET"),
        'chain': 'aptos_testnet'
      }],
      'ai_models': ['zerokdb']
    }
    worker_headers = {
      'signature-message-id': message_response['id'],
      'signature': signature,
    }
    worker_response = call_hub_post("/workers/", worker_data, worker_headers)

    return message_response['id'], worker_response['id'], signature

  except Exception as e:
    raise Exception('Error registering worker: {}'.format(e))