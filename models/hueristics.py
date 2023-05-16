import pandas as pd
from datetime import datetime
from utils.tools import get_config_path


def create_time_stamps(preds):
    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
    date_range = pd.date_range(start=current_hour, periods=len(preds), freq='H')
    preds_w_time = pd.DataFrame({'prediction': preds}, index=date_range)
    return preds_w_time

def merge_preds(preds, data, days, target):
    group_by_month = data.groupby(['month', 'hour']).mean()
    month = datetime.now().month
    df = group_by_month.loc[(month,)]
    list_hourly_means = df[target].tolist()
    preds = create_time_stamps(preds)
    hourly_map = dict(zip(range(24), list_hourly_means))
    preds["avgs"] = preds.index.hour.map(hourly_map)
    return preds

def load_formated_data(TARGET):
    data = pd.read_csv(get_config_path("ML_data.csv"))[["Datetime", TARGET, "TMP_F"]]
    data = data.set_index("Datetime")
    data.index = pd.to_datetime(data.index)
    return data

def percent_err(df, target):
    """
    Returns hours to turn off system for given appliance based on threshold.
    """
    outlier_threshold = 20 # anything higer than this is probably just a bad prediction
    flag_threshold = 15 # anything higher than this should be flagged
    pe = abs((df["prediction"] - df["avgs"]) / df["prediction"] * 100)
    ind = pe[(pe < outlier_threshold) & (pe > flag_threshold)].index
    return ind

def get_flagged_times(model_results, target, days):
    # Load in our testing data (train only)
    data = load_formated_data(target)
    train_size = round(data.shape[0] *2/3)
    data = data[:train_size]
    data["hour"] = data.index.hour
    data["month"] = data.index.month
    # Merge with predictions
    df = merge_preds(model_results[target]["predictions"].tolist(), data, days, target)
    # Percent Error rule
    pe = percent_err(df, target)
    return pe
