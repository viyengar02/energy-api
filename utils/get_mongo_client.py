from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from utils.tools import get_config_file
import certifi

#Establish DB Connection
def get_database(database_name: str):
    
    try:
        mongo_config = get_config_file("mongodb.config.json")
        #CONNECTION_STRING = f"mongodb+srv://viyengar02:AH105242@sdcluster.dtapx.mongodb.net/SDcluster?retryWrites=true&w=majority&tls=true&tlsCAFile=certifi.where()"
        CONNECTION_STRING = f"mongodb+srv://viyengar02:AH105242@sdcluster.dtapx.mongodb.net/?retryWrites=true&tls=true&w=majority&appName=SDcluster"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        #client = MongoClient(CONNECTION_STRING)
        client = MongoClient(
    CONNECTION_STRING,
    tlsAllowInvalidCertificates=True  # INSECURE! Use only to confirm CA issue
)
        # Create the database for our example (we will use the same database throughout the tutorial
        return client[database_name]
    except:
        print("Error connecting to database")
        return 0

def get_database_2(database_name: str):
    
    try:
        mongo_config = get_config_file("mongodb.config.json")
        CONNECTION_STRING = f"mongodb+srv://viyengar02:AH105242@sdcluster.dtapx.mongodb.net/?retryWrites=true&w=majority&appName=SDcluster"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
        # Create the database for our example (we will use the same database throughout the tutorial
        return client[database_name]
    except:
        print("Error connecting to database")
        return 0