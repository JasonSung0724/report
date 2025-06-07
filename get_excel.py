import pandas as pd
from config.name import ExcelFieldName

class GetExcelData:
    def __init__(self, input_data_path, platform):
        self.input_data_path = input_data_path
        self.platform = platform.lower()
        self.field_config = ExcelFieldName.get_config(self.platform)

    def check_excel(self):
        data = self.open_file()
        current_columns = [column for column in list(data.columns) if column.startswith("Unnamed:") == False]
        if current_columns == self.field_config["columns"]:
            receiver_name = self.field_config["receiver_name"]
            sorted_data = data.sort_values(by=receiver_name, ascending=True)
            print(f"\n處理{self.platform.upper()}訂單\n")
            print(f"原始資料數量: {len(data)}\n")
            return sorted_data
        else:
            raise ValueError(f"檔案欄位與預期不符: {list(data.columns)}")

    def open_file(self):
        order_number = self.field_config["order_id"]
        product_quantity = self.field_config["product_quantity"]
        return pd.read_excel(self.input_data_path, dtype={order_number: str, product_quantity: str})
    
    def __call__(self):
        return self.check_excel()