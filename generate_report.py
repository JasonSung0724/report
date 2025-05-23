import pandas as pd
from store_location import CheckAdress
from config import config, FileConfig
from openpyxl import load_workbook
from openpyxl.styles import Font
from typing import List, Dict, Any
from order_processors import C2COrderProcessor, MixxOrderProcessor, ShoplineOrderProcessor


class ReportGenerator:
    def __init__(self):
        self.c2c_processor = C2COrderProcessor()
        self.mixx_processor = MixxOrderProcessor()
        self.shopline_processor = ShoplineOrderProcessor()

    def save_to_excel(self, new_rows: List[Dict[str, Any]], output_path: str) -> None:
        """Save processed orders to Excel file."""
        wb = load_workbook(FileConfig.report_template)
        sheet = wb.active
        template_columns = [cell.value for cell in sheet[1]]
        processed_rows = [{col: row.get(col, "") for col in template_columns} for row in new_rows]
        new_data = pd.DataFrame(processed_rows)

        for i, row in enumerate(new_data.values, start=2):
            for j, value in enumerate(row, start=1):
                cell = sheet.cell(row=i, column=j, value=value)
                if isinstance(value, str) and "ERROR" in value:
                    cell.font = Font(color="FF0000")

        wb.save(output_path)

    def _determine_order_type(self, data: pd.DataFrame) -> tuple[str, pd.DataFrame]:
        """Determine order type and return sorted data."""
        if "收件人" in data.columns:
            sorted_data = data.sort_values(by="收件人", ascending=True)
            if len(data.columns) >= 17:
                return "shopline", sorted_data
            elif len(data.columns) >= 10:
                return "mixx", sorted_data
        elif "收件者姓名" in data.columns:
            return "c2c", data.sort_values(by="收件者姓名", ascending=True)
        return "unknown", data

    def _print_order_statistics(self, order_type: str, data: pd.DataFrame, new_rows: List[Dict[str, Any]]) -> None:
        """Print order processing statistics."""
        print(f"\n原始資料筆數: {len(data)}")

        if order_type == "c2c":
            main_product_count = len(data[data["商品編號"] != config.order.SPECIAL_PRODUCT])
            freebies_count = len(data[data["商品編號"] == config.order.SPECIAL_PRODUCT])
            print(f"\n主商品數量: {main_product_count}")
            print(f"\n贈品數量: {freebies_count}")

        print(f"\n最終筆數: {len(new_rows)}")

        order_number_column = {"shopline": "訂單號碼", "c2c": "平台訂單編號", "mixx": "*銷售單號"}.get(order_type)

        if order_number_column and order_number_column in data:
            print(f"\n總訂單數: {len(data[order_number_column].unique())}")

    def generate_report(self, input_data_path: str, output_path: str) -> None:
        """Generate report from input data."""
        if "." not in output_path:
            output_path += ".xlsx"

        # Read and process input data
        original_data = pd.read_excel(input_data_path)
        order_type, sorted_data = self._determine_order_type(original_data)

        # Process orders based on type
        if order_type == "shopline":
            print("Shopline 訂單處理")
            address_checker = CheckAdress(original_data_path=input_data_path)
            location_info = address_checker.check_adress()
            new_rows = self.shopline_processor.process_orders(sorted_data, location_info)
        elif order_type == "mixx":
            print("Mixx 訂單處理")
            new_rows = self.mixx_processor.process_orders(sorted_data)
        elif order_type == "c2c":
            print("C2C 訂單處理")
            new_rows = self.c2c_processor.process_orders(sorted_data)
        else:
            print("未知的訂單格式")
            return

        # Print statistics and save results
        self._print_order_statistics(order_type, sorted_data, new_rows)
        self.save_to_excel(new_rows, output_path)


if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate_report(
        input_data_path=r"C:\Users\07711.Jason.Sung\OneDrive - Global ICT\文件\快電商XCHECK2CHECK-拋單追蹤-減醣市集-貝果 (13).xlsx",
        output_path="output_report",
    )
