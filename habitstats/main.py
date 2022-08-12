import pandas as pd


def process_data(data):
    # TODO check if data has date and habit columns
    data = data.drop_duplicates().sort_values("date")
    data["month"] = data["date"].apply(lambda x: x.month)
    data["week"] = data["date"].apply(lambda x: x.isocalendar()[1])
    # differentiate between last week of last year and this year
    data.loc[((data.week == 52) & (data.month == 1)), "week"] = 0
    return data
