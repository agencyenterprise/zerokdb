import httpx
import os

def call_hub_post(endpoint, data, headers={}):
  response = httpx.post(os.environ['HUB_URL'] + endpoint, json=data, headers=headers, timeout=600)

  if response.status_code == 200:
    return response.json()
  else:
    raise Exception('Error executing "{}": {}'.format(endpoint, response))

def call_hub_get(endpoint, headers={}):
  response = httpx.get(os.environ['HUB_URL'] + endpoint, headers=headers, timeout=600)

  if response.status_code == 200:
    return response.json()
  else:
    raise Exception('Error executing "{}": {}'.format(endpoint, response))
