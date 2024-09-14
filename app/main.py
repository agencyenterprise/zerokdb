from fastapi import FastAPI
import json
import hashlib

from zerokdb.ipfs_storage import IPFSStorage

app = FastAPI()

# Initialize IPFSStorage
storage = IPFSStorage()

