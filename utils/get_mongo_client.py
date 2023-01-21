from pymongo import MongoClient

#Establish DB Connection
def get_database(database_name: str):

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING =  "mongodb+srv://ava54:jvLsXWTf70tIkSij@cluster0.lsback5.mongodb.net/?retryWrites=true&w=majority" #"mongodb+srv://ava54:2Qxaj3GoMmUSENR7@cluster0.lsback5.mongodb.net/test"
    
    try:
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        client = MongoClient(CONNECTION_STRING)
        # Create the database for our example (we will use the same database throughout the tutorial
        return client[database_name]
    except:
        print("Error connecting to database")
        return 0