import pandas as pd


def get_dataframe(data_thing):
    """
    Takes an arbitrary object and converts it into a standardized object
    all methods can use.
    """
    # dataframe passthrough
    if type(data_thing) == pd.core.frame.DataFrame:
        result = data_thing
    # csv file path
    elif data_thing.strip().endswith(".csv"):
        print("loading file...")
        data = pd.read_csv(data_thing)
        result = data

    # === post-loading cleanup
    # drop any worthless columns
    result.dropna(axis='columns', how='all', inplace=True)

    # === defensive programming checks
    if len(result) < 1:
        raise AssertionError("loaded dataframe has length of 0")

    return result
