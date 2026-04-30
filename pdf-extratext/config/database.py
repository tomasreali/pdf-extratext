from pymongo import MongoClient
from config.settings import settings

client = MongoClient(settings.mongo_url)
db = client[settings.db_name]
collection = db["documents"]