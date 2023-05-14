import pandas as pd
from datetime import datetime
from utils.tools import get_config_path



def generate_order(start_index=datetime.now().hour):
    """
    Generates a list starting from a specified index, counting up to 23, then wrapping back to 0 and counting up to
    the specified index again.

    :param start_index: The starting index for the list. Must be between 0 and 23 (inclusive).
    :return: The generated list.
    """
    if not (0 <= start_index <= 23):
        raise ValueError("start_index must be between 0 and 23 (inclusive).")
    
    generated_list = []
    for i in range(start_index, 24):
        generated_list.append(i)
    for i in range(0, start_index):
        generated_list.append(i)
    
    return generated_list

def merge_preds(preds, data, days):
    group_by_month = data.groupby(['month', 'hour']).mean()
    month = datetime.now().month
    df = group_by_month.loc[(month,)]
    df = df.iloc[generate_order()]
    df = df.reset_index(drop=True)
    df = pd.concat([df] * days, ignore_index=True)
    df["prediction"] = preds
    return df

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
    pe = abs((df["prediction"] - df[target]) / df["prediction"] * 100)
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
    df = merge_preds(model_results[target]["predictions"].tolist(), data, days)
    # Percent Error rule
    pe = percent_err(df, target)
    return pe

