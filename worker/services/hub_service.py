import httpx
import os

hub_url = os.getenv("HUB_URL") or "http://localhost:8000"

def call_hub_post(endpoint, data, headers={}):
  response = httpx.post(hub_url + endpoint, json=data, headers=headers, timeout=600)

  if response.status_code == 200:
    return response.json()
  else:
    raise Exception('Error executing "{}": {}'.format(endpoint, response))

def call_hub_get(endpoint, headers={}):
  response = httpx.get(hub_url + endpoint, headers=headers, timeout=600)

  if response.status_code == 200:
    return response.json()
  else:
    raise Exception('Error executing "{}": {}'.format(endpoint, response))
