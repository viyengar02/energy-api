'''
optimizations.py
Responsible for scheduling and generating optimization commands to the corresponding board
'''
from services import mongo_interface
from fastapi import HTTPException

#Takes in a voltage thershold and checks if the user's board_id send voltage higher than the thershold
def enable_th_optimization(user_id: str, optimization_options: object):
    try:
        config = optimization_options.dict()
        user_info = mongo_interface.get_user(user_id);
        update_board = mongo_interface.update_board_config(user_info["board_id"], config);
        return update_board;
    except Exception as error:
        print(f'Error occurred at enable_th_optimization: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")