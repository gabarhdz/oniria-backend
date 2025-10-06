import chromadb
import os
from dotenv import load_dotenv
load_dotenv()

client = chromadb.CloudClient(
  api_key=os.getenv("CHROMADB_API_KEY"),
  tenant=os.getenv("CHROMADB_TENANT"),
  database=os.getenv("CHROMADB_DATABASE")
)