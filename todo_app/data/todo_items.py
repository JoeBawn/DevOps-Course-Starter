import os 
import requests, datetime, json
import pymongo, ssl

class ToDoCard:
    def __init__(self, id, name, idList, due_date, description, modified):
        self.id = id
        self.name = name
        self.idList = idList
        self.due_date = due_date
        self.description = description
        self.modified = modified
    
    def get_date(self):
        return datetime.datetime.strftime(self.due_date, '%Y-%m-%d')
    
    def get_user_date(self):
        return datetime.datetime.strftime(self.due_date, '%d/%m/%Y')

    def get_modified_date(self):
        return datetime.datetime.strftime(self.modified, '%Y-%m-%d')
    
    def get_modified_user_date(self):
        return datetime.datetime.strftime(self.modified, '%d/%m/%Y')
    
    def get_card_as_dictionary(self):
        return {'name' : self.name, 'idList' : self.idList, 'due_date' : self.due_date, 'description' : self.description, 'modified' : self.modified}

class ViewModel:
    def __init__(self, items, lists):
        self._items = items
        self._lists = lists

    @property
    def items(self):
        return self._items

    @property
    def lists(self):
        return self._lists

    @property
    def items_todo(self):
        items = []
        for item in self._items:
            if item.idList == self.lists['ToDo']:
                items.append(item)
        return items

    @property
    def items_doing(self):
        items = []
        for item in self._items:
            if item.idList == self.lists['Doing']:
                items.append(item)
        return items

    @property
    def items_done(self):
        items = []
        for item in self._items:
            if item.idList == self.lists['Done']:
                items.append(item)
        return items

    @property
    def recent_done_items(self):
        items = []
        for item in self._items:
            if item.idList == self.lists['Done'] and item.modified == datetime.date.today():
                items.append(item)
        return items

    @property
    def older_done_items(self):
        items = []
        for item in self._items:
            if item.idList == self.lists['Done'] and item.modified != datetime.date.today():
                items.append(item)
        return items

def get_mongodb_connection():
    mongodb_url = os.getenv('MONGO_URL')
    return mongodb_url

def get_mongodb_database_name():
    mongodb_name = os.getenv('MONGO_DB_NAME')
    return mongodb_name

def mongo_db_connection():
    db_connection = get_mongodb_connection()
    db_name = get_mongodb_database_name()

    mongo_client = pymongo.MongoClient(db_connection, ssl_cert_reqs=ssl.CERT_NONE)
    db = mongo_client[db_name]

    return db

def get_todo_cards():
    db = mongo_db_connection()
    collections = db.list_collection_names()

    card_list = []
    for col in collections:
        collection = db[col]

        for card in collection.find({}):
            card_list.append(ToDoCard(card['_id'], card['name'], card['idList'], card['due_date'], card['description'], card['modified']))

    return card_list

def move_todo_card(card_id, new_list_id):
    db = mongo_db_connection()
    collections = db.list_collection_names()

    for col in collections:
        collection = db[col]
        for card in collection.find({}): 
            if str(card['_id']) == str(card_id):
                new_card = ToDoCard(0, card['name'], new_list_id, card['due_date'], card['description'], datetime.datetime.today())
                new_collection = db[new_list_id]
                new_collection.insert_one(new_card.get_card_as_dictionary())
                result = collection.delete_one({'_id' : card['_id']})
                print(result)
                break

def delete_todo_card(card_id):
    db = mongo_db_connection()
    collections = db.list_collection_names()

    for col in collections:
        collection = db[col]
        for card in collection.find({}): 
            if str(card['_id']) == str(card_id):
                result = collection.delete_one({'_id' : card_id})

def create_todo_card(new_card):
    db = mongo_db_connection()
    card = new_card.get_card_as_dictionary()
    db['todo'].insert_one(card)

def create_test_db(db_name):
    db_connection = get_mongodb_connection()
    mongo_client = pymongo.MongoClient(db_connection, ssl_cert_reqs=ssl.CERT_NONE)
    db = mongo_client[db_name]

    return db_name

def delete_test_db(db_name):
    db_connection = get_mongodb_connection()
    mongo_client = pymongo.MongoClient(db_connection, ssl_cert_reqs=ssl.CERT_NONE)
    mongo_client.drop_database(db_name)
    