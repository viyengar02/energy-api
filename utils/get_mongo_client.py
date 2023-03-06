from pymongo import MongoClient
from utils.tools import get_config_file

#Establish DB Connection
def get_database(database_name: str):
    
    try:
        mongo_config = get_config_file("mongodb.config.json")
        CONNECTION_STRING = f"mongodb+srv://{mongo_config['username']}:{mongo_config['password']}@{mongo_config['url']}"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        client = MongoClient(CONNECTION_STRING)
        # Create the database for our example (we will use the same database throughout the tutorial
        return client[database_name]
    except:
        print("Error connecting to database")
        return 0