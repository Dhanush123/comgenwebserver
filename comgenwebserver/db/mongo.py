import os
from pymongo import MongoClient

COLLECTION_NAME = 'comgen'


class MongoRepository(object):
    def __init__(self):
        mongo_url = os.environ.get('MONGO_URL')
        self.db = MongoClient(mongo_url).comgen

    def find_all(self, selector):
        return self.db.comgen.find(selector)

    def find(self, selector):
        return self.db.comgen.find_one(selector)

    def create(self, comgen):
        return self.db.comgen.insert_one(comgen)

    def update(self, selector, comgen):
        return self.db.comgen.replace_one(selector, comgen, upsert=True).modified_count

    def delete(self, selector):
        return self.db.comgen.delete_one(selector).deleted_count
