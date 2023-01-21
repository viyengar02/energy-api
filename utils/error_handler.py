

def mongo_db_error_handler(error):
    #Check error code with config

    #Map Mongo DB error code to REST error code
    error_object = {
        "status-code": 500,
        "message": "Internal Server Error"
    }
    return 