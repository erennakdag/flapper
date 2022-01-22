from pymongo import MongoClient
import certifi
from random import randrange

client = MongoClient("XXX", tlsCAFile=certifi.where())
db = client.flapper
users = db.users

def generate_random_id():
    return randrange(100, 100000)
