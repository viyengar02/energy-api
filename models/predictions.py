import requests
import pandas as pd
import datetime as datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from models.hueristics import get_flagged_times
from utils.tools import get_config_path

model_targets = [ # These are the good models so we will use them as a demo
    "electricity-interior_lighting",
    "electricity-fans",
    "electricity-interior_equipment"
]

def load_model(board_path: str):
    # Init regression model
    reg = xgb.XGBRegressor(base_score=0.5, booster='gbtree',    
                        n_estimators=1000, # creates 1k tress for this tree algorithm (read more on documentation to see other tweaks)
                        early_stopping_rounds=50,
                        #  objective='reg:linear',
                        #  max_depth=3,
                        learning_rate=0.01
                        )

    # Import the model
    reg = xgb.XGBRegressor()
    reg.load_model(board_path)
    # print(reg.get_booster().feature_names)
    return reg

def create_features(df):
    """
    Create time series features based on time series index.
    """
    df = df.copy() # to edit a copy of our data instead of replacing it
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['quarter'] = df.index.quarter
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear
    df['dayofmonth'] = df.index.day
    df['weekofyear'] = df.index.isocalendar().week
    df['weekofyear'] = df['weekofyear'].astype('int')
    df['TMP_F'] = df['TMP_F'].astype('float')
    # Reorder for model input
    df = df[['hour',
        'dayofweek',
        'quarter',
        'month',
        'year',
        'dayofyear',
        'dayofmonth',
        'weekofyear',
        'TMP_F'
        ]]
    return df

def get_data(days: int):
    # Get future 24 hours of data to predict on
    URL = f"https://api.open-meteo.com/v1/forecast?latitude=39.95&longitude=-75.16&past_days={days}&hourly=temperature_2m&temperature_unit=fahrenheit"
    data = requests.get(URL).json()
    # Get time period to predict
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M") # Get current datetime as string
    start_date = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M').replace(minute=0) # Turn to datetime
    end_date = start_date + timedelta(days=days)
    date_times = data.get("hourly").get("time")
    date_times = [datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M') for date in date_times]
    temps = data.get("hourly").get("temperature_2m")
    # Store into list to be loaded in pandas dataframe
    targets = []
    for date, temp in zip(date_times, temps):
        if date >= start_date and date < end_date:
            targets.append([date, format(temp, '.2f')])
    return targets

def create_df(targets):
    # Create the pandas DataFrame
    weather_df = pd.DataFrame(targets, columns = ['Datetime', 'TMP_F'])
    weather_df = weather_df.set_index('Datetime')
    weather_df = create_features(weather_df)
    return weather_df

def run_predictions(days: int):
    # Get weather forcast data from API
    targets = get_data(days)
    # Format to dataframe to pass to model
    validation_data = create_df(targets)
    # Load in the model
    model = load_model(get_config_path("LSTM_model.json"))
    # Run predictions on validation data
    predictions = model.predict(validation_data)
    return predictions, targets

def run_predictions_v2(days: int):
    """
    Base func to calculate predictions of appliances using ML models.
    """
    # Get weather forecast data from API
    try:
        temperature_data = get_data(days)
        # Format to dataframe to pass to model
        model_inputs = create_df(temperature_data)
        results={}
        for target in model_targets:
            print(f"Getting {days} days forecast for model: {target}...")
            results[target] = {}
            # Run predictions using the current model
            model = load_model(get_config_path(f"{target}_model.json"))
            predictions = model.predict(model_inputs)
            results[target]["predictions"] = predictions
            flagged_times = get_flagged_times(results, target, days)
            results[target]["flagged_times"] = flagged_times

        print(results)
        return results
    except Exception as error:
        print(f'Error occurred at run_predictions_v2: {error}')
        raise f'Error occurred at run_predictions_v2: {error}'
