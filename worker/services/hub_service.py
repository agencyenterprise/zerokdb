import httpx
import os

hub_url = os.getenv("HUB_URL") or "https://g1cqd9cf69e1b0tj8fd7o85mdg.ingress.akashprovid.com"

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
