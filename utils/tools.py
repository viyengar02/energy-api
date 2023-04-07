import os
import json 

#Returns a specified config file as a dictionary
def get_config_file(file_name: str):

    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
        config_dir = os.path.join(parent_dir, 'config')

        with open(f"{config_dir}/{file_name}", 'r') as f:
            # Read the contents of the file into a string
            config_dict = json.load(f)
            return config_dict   
    except Exception as e:
        print(f"Exception occured in get_config_file: {e}")
        return 1
    
def get_config_path(file_name: str):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
        config_dir = os.path.join(parent_dir, 'config')

        return f"{config_dir}/{file_name}"
    except Exception as e:
        print(f"Exception occured in get_config_file: {e}")
        return 1
    