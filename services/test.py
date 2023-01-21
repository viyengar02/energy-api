from pymongo import MongoClient

#MORE INFO - https://www.mongodb.com/languages/python

#Establish DB Connection
def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://ava54:2Qxaj3GoMmUSENR7@cluster0.lsback5.mongodb.net/test"
    
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)
    
    # Create the database for our example (we will use the same database throughout the tutorial
    return client['myFirstDatabase']

#Insert some item
def insert_random_item(collection_name):
    test_insert = {
        "_id" : "U1IT00001",
        "item_name" : "Aleks is very cool",
    }
    collection_name.insert_many([test_insert])
    #collection_name.insert_one(test_insert)

#Get Data From Connection
def get_collection_items(collection_name):
    item_details = collection_name.find()
    for item in item_details:
        print(item)
   
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
    # Get the database
    dbname = get_database()
    collection_name = dbname["myCollection"]
    #insert_random_item(collection_name)
    get_collection_items(collection_name)