import pandas as pd
from config.name import *
import os


class ExcelController:

    def __init__(self, data_path, sheet_name=None):
        self.data_path = data_path
        self.df = pd.read_excel(data_path, sheet_name=sheet_name)

    def data_filter(self, conditions, index=None):
        filter_condition = None
        for column, value in conditions.items():
            if callable(value):
                condition = self.df[column].apply(value)
            else:
                condition = self.df[column] == value
            if filter_condition is None:
                filter_condition = condition
            else:
                filter_condition = filter_condition & condition
        filtered_data = self.df[filter_condition]
        if not filtered_data.empty and index is not None:
            return filtered_data.iloc[index]
        else:
            return filtered_data

    def save_excel(self, engine):
        # engine='xlwt' or "openpyxl"
        self.df.to_excel(self.data_path, index=False, engine=engine)

    def save_excel_with_multiple_sheets(self, file_path, sheet_name):
        try:
            with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                self.df.to_excel(writer, sheet_name=sheet_name, index=False)
        except FileNotFoundError:
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                self.df.to_excel(writer, sheet_name=sheet_name, index=False)
