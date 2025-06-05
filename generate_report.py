import pandas as pd
from store_location import CheckAdress
from config import FilePath, TargetShipping, CompanyName
from openpyxl import load_workbook
from datetime import datetime
import os
from openpyxl.styles import Font
import json


class ProductConfig:
    def __init__(self):
        with open("product_config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def search_product(self, search_value, search_type="mixx_name"):
        for product_code, product_info in self.config.items():
            if search_type == "mixx_name" and search_value in product_info.get("mixx_name", ""):
                return product_code
            elif search_type == "c2c_code" and product_info.get("c2c_code") == search_value:
                return product_code
        return None, None


class OrderProcessor:
    def __init__(self):
        self.product_config = ProductConfig()

    def format_date(self, order_time):
        try:
            if isinstance(order_time, datetime):
                date_time_format = order_time
            else:
                date_time_format = datetime.strptime(order_time, "%Y-%m-%d %H:%M:%S")
            return date_time_format.strftime("%Y%m%d")
        except (ValueError, TypeError):
            return "INVALID_DATE"

    def calculate_box_type(self, personal_order):
        grand_total = 0
        for order in personal_order:
            try:
                if str(order["商品編號"]) and str(order["商品編號"]) != "nan":
                    with open("product_config.json", "r", encoding="utf-8") as f:
                        product_config = json.load(f)
                    qty = product_config[order["商品編號"]]["qty"]
                    order_quantity = int(float(order["訂購數量"]))
                    grand_total += qty * order_quantity
            except ValueError as e:
                print(f"處理商品編號 {order['商品編號']} 時發生錯誤: {e}")
                raise

        if grand_total <= 14:
            return "box60-EA", "60公分紙箱"
        elif grand_total <= 47:
            return "box90-EA", "90公分紙箱"
        return "ERROR-需拆單", "ERROR-需拆單"

    def get_delivery_info(self, row, store_adress):
        if row["送貨方式"].split("（", 1)[0] == TargetShipping.tacat:
            return "Tcat", row["完整地址"]
        elif row["送貨方式"].split("（", 1)[0] == TargetShipping.family:
            adress = (
                "ERROR"
                if row["門市名稱"] not in store_adress[CompanyName.family]
                else f"{row['門市名稱']} ({store_adress[CompanyName.family][row['門市名稱']]})"
            )
            return "全家", adress
        elif row["送貨方式"].split("（", 1)[0] == TargetShipping.seven:
            adress = "ERROR" if row["門市名稱"] not in store_adress[CompanyName.seven] else "(宅轉店)" + store_adress[CompanyName.seven][row["門市名稱"]]
            return "7-11", adress
        return "UNKNOWN", "ERROR"

    def create_order_row(self, base_data, product_code, order_mark, formatted_date, order_type="c2c"):
        if order_type == "c2c":
            order_number = str(base_data["平台訂單編號"]) if not pd.isna(base_data["平台訂單編號"]) else ""
            return {
                "貨主編號": "A442",
                "貨主單號\n(不同客戶端、不同溫層要分單)": order_number,
                "客戶端代號(店號)": str(base_data["收件者姓名"]),
                "訂購日期": formatted_date,
                "商品編號": product_code,
                "商品名稱": str(base_data["商品樣式"]).replace("-F", ""),
                "訂購數量": str(base_data["小計數量"]),
                "配送方式\nFT : 逢泰配送\nTcat : 黑貓宅配\n全家到府取貨": "Tcat",
                "收貨人姓名": str(base_data["收件者姓名"]),
                "收貨人地址": str(base_data["收件者地址"]),
                "收貨人聯絡電話": str(base_data["收件者手機"]),
                "訂單 / 宅配單備註": "減醣市集 X 快電商 C2C BUY" + order_mark,
                "品項備註": "",
                "指定配送溫層\n001：常溫\n002：冷藏\n003：冷凍": "003",
            }
        elif order_type == "mixx":
            return {
                "貨主編號": "A442",
                "貨主單號\n(不同客戶端、不同溫層要分單)": str(base_data["*銷售單號"]),
                "客戶端代號(店號)": str(base_data["收件人"]),
                "訂購日期": formatted_date,
                "商品編號": product_code,
                "商品名稱": str(base_data["品名/規格"]),
                "訂購數量": str(base_data["採購數量"]),
                "配送方式\nFT : 逢泰配送\nTcat : 黑貓宅配\n全家到府取貨": "Tcat",
                "收貨人姓名": str(base_data["收件人"]),
                "收貨人地址": str(base_data["收件地址"]),
                "收貨人聯絡電話": str(base_data["收件人手機"]),
                "訂單 / 宅配單備註": "減醣市集" + order_mark,
                "品項備註": "",
                "指定配送溫層\n001：常溫\n002：冷藏\n003：冷凍": "003",
            }
        elif order_type == "shopline":
            return {
                "貨主編號": "A442",
                "貨主單號\n(不同客戶端、不同溫層要分單)": str(base_data["訂單號碼"]),
                "客戶端代號(店號)": str(base_data["收件人"]),
                "訂購日期": formatted_date,
                "預計到貨日": "",
                "商品編號": str(base_data["商品貨號"]),
                "商品名稱": f"{base_data['商品名稱']}",
                "訂購數量": str(base_data["數量"]),
                "配送方式\nFT : 逢泰配送\nTcat : 黑貓宅配\n全家到府取貨": base_data["delivery_method"],
                "收貨人姓名": str(base_data["收件人"]),
                "收貨人地址": base_data["address"],
                "收貨人聯絡電話": str(base_data["收件人電話號碼"]),
                "訂單 / 宅配單備註": "減醣市集" + order_mark,
                "品項備註": "",
                "指定配送溫層\n001：常溫\n002：冷藏\n003：冷凍": "003",
            }

    def process_mixx_orders(self, sorted_data):
        new_rows = []
        personal_order = []

        for _, row in sorted_data.iterrows():
            product_code = self.product_config.search_product(search_type="mixx_name", search_value=str(row["品名/規格"]).split("｜")[1])
            order_mark = "" if str(row["備註"]) == "nan" else f"/{row['備註']}"
            formatted_date = self.format_date(datetime.now())

            if personal_order and personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] != str(row["*銷售單號"]):
                box_type, box_name = self.calculate_box_type(personal_order)
                refer_order = personal_order[0].copy()
                refer_order.update(
                    {
                        "商品編號": box_type,
                        "商品名稱": box_name,
                        "訂購數量": "1",
                        "品項備註": "箱子",
                    }
                )
                new_rows.append(refer_order)
                personal_order.clear()

            new_row = self.create_order_row(row, product_code, order_mark, formatted_date, "mixx")
            if str(row["*銷售單號"]) != "nan":
                if not personal_order or personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] == str(row["*銷售單號"]):
                    personal_order.append(new_row)
                else:
                    personal_order = [new_row]
                new_rows.append(new_row)

        if personal_order:
            box_type, box_name = self.calculate_box_type(personal_order)
            refer_order = personal_order[0].copy()
            refer_order.update(
                {
                    "商品編號": box_type,
                    "商品名稱": box_name,
                    "訂購數量": "1",
                    "品項備註": "箱子",
                }
            )
            new_rows.append(refer_order)

        return new_rows

    def process_c2c_orders(self, sorted_data):
        new_rows = []
        personal_order = []

        for _, row in sorted_data.iterrows():
            if str(row["商品編號"]) == "F2500000044":
                for i in range(2):
                    product_code = self.product_config.search_product(search_type="c2c_code", search_value=f"F2500000044-{i}")
                    order_mark = "" if str(row["出貨備註"]) == "nan" else f" | {row['出貨備註']}"
                    formatted_date = self.format_date(row["建立時間"])

                    if personal_order and personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] != str(row["平台訂單編號"]):
                        box_type, box_name = self.calculate_box_type(personal_order)
                        refer_order = personal_order[0].copy()
                        refer_order.update(
                            {
                                "商品編號": box_type,
                                "商品名稱": box_name,
                                "訂購數量": "1",
                                "品項備註": "箱子",
                            }
                        )
                        new_rows.append(refer_order)
                        personal_order.clear()

                    new_row = self.create_order_row(row, product_code, order_mark, formatted_date, "c2c")
                    new_row["商品名稱"] = str(row["商品樣式"]).replace("(贈品)-F", "").split("+")[i]

                    if str(row["平台訂單編號"]) != "nan":
                        if not personal_order or personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] == str(row["平台訂單編號"]):
                            personal_order.append(new_row)
                        else:
                            personal_order = [new_row]
                        new_rows.append(new_row)
            else:
                product_code = self.product_config.search_product(search_type="c2c_code", search_value=str(row["商品編號"]))
                order_mark = "" if str(row["出貨備註"]) == "nan" else f" | {row['出貨備註']}"
                formatted_date = self.format_date(row["建立時間"])

                if personal_order and personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] != str(row["平台訂單編號"]):
                    box_type, box_name = self.calculate_box_type(personal_order)
                    refer_order = personal_order[0].copy()
                    refer_order.update(
                        {
                            "商品編號": box_type,
                            "商品名稱": box_name,
                            "訂購數量": "1",
                            "品項備註": "箱子",
                        }
                    )
                    new_rows.append(refer_order)
                    personal_order.clear()

                new_row = self.create_order_row(row, product_code, order_mark, formatted_date, "c2c")

                if str(row["平台訂單編號"]) != "nan":
                    if not personal_order or personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] == str(row["平台訂單編號"]):
                        personal_order.append(new_row)
                    else:
                        personal_order = [new_row]
                    new_rows.append(new_row)

        if personal_order:
            box_type, box_name = self.calculate_box_type(personal_order)
            refer_order = personal_order[0].copy()
            refer_order.update(
                {
                    "商品編號": box_type,
                    "商品名稱": box_name,
                    "訂購數量": "1",
                    "品項備註": "箱子",
                }
            )
            new_rows.append(refer_order)

        return new_rows

    def process_shopline_orders(self, sorted_data, address_info):
        new_rows = []
        personal_order = []
        skip_order = 0

        for _, row in sorted_data.iterrows():
            delivery_method, address = self.get_delivery_info(row, address_info)
            product_mark = "" if len(str(row["商品貨號"]).split("-")) < 3 else "-" + str(row["商品貨號"]).split("-")[2]
            order_mark = "" if str(row["出貨備註"]) == "nan" else f"/{row['出貨備註']}"
            formatted_date = self.format_date(str(row["訂單日期"]))

            if personal_order and personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] != str(row["訂單號碼"]):
                box_type, box_name = self.calculate_box_type(personal_order)
                refer_order = personal_order[0].copy()
                refer_order.update(
                    {
                        "商品編號": box_type,
                        "商品名稱": box_name,
                        "訂購數量": "1",
                        "品項備註": "箱子",
                    }
                )
                new_rows.append(refer_order)
                personal_order.clear()

            row_data = row.to_dict()
            row_data.update({"delivery_method": delivery_method, "address": address, "product_mark": product_mark})
            new_row = self.create_order_row(row_data, None, order_mark, formatted_date, "shopline")
            new_row["商品名稱"] = f"{row['商品名稱']}{product_mark}"

            if str(row["商品貨號"]) != "nan":
                if not personal_order or personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] == str(row["訂單號碼"]):
                    personal_order.append(new_row)
                else:
                    personal_order = [new_row]
                if len(row) > 17 and pd.notna(row.iloc[17]) and row.iloc[17] in ["下午到貨", "上午到貨"]:
                    new_row["到貨時段\n1: 13點前\n2: 14~18\n3: 不限時"] = 1 if str(row.iloc[17]) == "上午到貨" else 2
                new_rows.append(new_row)
            else:
                skip_order += 1

        if personal_order:
            box_type, box_name = self.calculate_box_type(personal_order)
            refer_order = personal_order[0].copy()
            refer_order.update(
                {
                    "商品編號": box_type,
                    "商品名稱": box_name,
                    "訂購數量": "1",
                    "品項備註": "箱子",
                }
            )
            new_rows.append(refer_order)

        print(f"\n商品貨號空白故扣除筆數：{skip_order}")
        return new_rows


class ReportGenerator:
    def __init__(self):
        self.order_processor = OrderProcessor()

    def save_to_excel(self, new_rows, output_path):
        wb = load_workbook(FilePath.report)
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

    def generate_report(self, input_data_path, output_path):
        if "." not in output_path:
            output_path += ".xlsx"

        original_data = pd.read_excel(input_data_path, dtype={"平台訂單編號": str, "小計數量": str})
        original_column_count = len(original_data.columns)

        if "收件人" in original_data.columns:
            sorted_data = original_data.sort_values(by="收件人", ascending=True)
            if original_column_count >= 17:
                print("Shopline 訂單處理")
                adress = CheckAdress(original_data_path=input_data_path)
                loaction_info = adress.check_adress()
                print(f"\n原始資料筆數: {len(original_data)}")
                new_rows = self.order_processor.process_shopline_orders(sorted_data, loaction_info)
            elif original_column_count >= 10:
                print("Mixx 訂單處理")
                print(f"\n原始資料筆數: {len(original_data)}")
                new_rows = self.order_processor.process_mixx_orders(sorted_data)
        elif "收件者姓名" in original_data.columns:
            sorted_data = original_data.sort_values(by="收件者姓名", ascending=True)
            print("C2C 訂單處理")
            print(f"\n原始資料筆數: {len(original_data)}")
            main_product_count = len(sorted_data[sorted_data["商品編號"] != "F2500000044"])
            freebies_count = len(sorted_data[sorted_data["商品編號"] == "F2500000044"])
            print(f"\n主商品數量: {main_product_count}")
            print(f"\n贈品數量: {freebies_count}")
            new_rows = self.order_processor.process_c2c_orders(sorted_data)

        else:
            print("未知的訂單格式")
            return

        print(f"\n最終筆數: {len(new_rows)}")

        if "訂單號碼" in sorted_data:
            order_number = sorted_data["訂單號碼"]
        elif "平台訂單編號" in sorted_data:
            order_number = sorted_data["平台訂單編號"]
        elif "*銷售單號" in sorted_data:
            order_number = sorted_data["*銷售單號"]

        print(f"\n總訂單數: {len(order_number.unique())}")
        self.save_to_excel(new_rows, output_path)


if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate_report(
        input_data_path=r"C:\Users\07711.Jason.Sung\OneDrive - Global ICT\文件\快電商XCHECK2CHECK-拋單追蹤-減醣市集-貝果 (20).xlsx",
        output_path="123",
    )
