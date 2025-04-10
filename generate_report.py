import pandas as pd
from store_location import CheckAdress
from config import FilePath, TargetShipping, CompanyName
from excel_controller import ExcelController
from openpyxl import load_workbook
from datetime import datetime
import os
from openpyxl.styles import Font


def get_delivery_info(row, store_adress):
    if row["送貨方式"].split("（", 1)[0] == TargetShipping.tacat:
        return "Tcat", row["完整地址"]
    elif row["送貨方式"].split("（", 1)[0] == TargetShipping.family:
        adress = (
            "ERROR" if row["門市名稱"] not in store_adress[CompanyName.family] else f"{row['門市名稱']} ({store_adress[CompanyName.family][row['門市名稱']]})"
        )
        return "全家", adress
    elif row["送貨方式"].split("（", 1)[0] == TargetShipping.seven:
        adress = "ERROR" if row["門市名稱"] not in store_adress[CompanyName.seven] else "(宅轉店)" + store_adress[CompanyName.seven][row["門市名稱"]]
        return "7-11", adress
    return "UNKNOWN", "ERROR"


def calculate_box_type(personal_order, product_info):
    grand_total = 0
    for order in personal_order:
        try:
            if str(order["商品編號"]) and str(order["商品編號"]) != "nan":
                filtered_data = product_info.data_filter({"商品編號": order["商品編號"]})
                if filtered_data.empty:
                    raise ValueError(f"商品編號 {order['商品編號']} 在資料中不存在")
                quantity = filtered_data.get("數量")
                if quantity is None or quantity.empty:
                    raise ValueError(f"商品編號 {order['商品編號']} 的數量資料缺失")
                grand_total += quantity.iloc[0] * int(order["訂購數量"])
            else:
                pass
        except ValueError as e:
            print(f"處理商品編號 {order['商品編號']} 時發生錯誤: {e}")
            raise

    if grand_total <= 14:
        return "box60-EA", "60公分紙箱"
    elif grand_total <= 47:
        return "box90-EA", "90公分紙箱"
    else:
        return "ERROR-需拆單", "ERROR-需拆單"


def format_date(order_time):
    try:
        if isinstance(order_time, datetime):
            date_time_format = order_time
        else:
            date_time_format = datetime.strptime(order_time, "%Y-%m-%d %H:%M:%S")
        return date_time_format.strftime("%Y%m%d")
    except (ValueError, TypeError):
        return "INVALID_DATE"


def process_mixx_orders(sorted_data):
    product_info = ExcelController(data_path=FilePath.doc, sheet_name="product")
    new_rows = []
    personal_order = []

    for _, row in sorted_data.iterrows():
        product_code = product_info.data_filter({"商品品名(Mixx)": str(row["品名/規格"]).split("｜")[1]})

        product_code = product_code.iloc[0].get("商品編號")
        order_mark = "" if str(row["備註"]) == "nan" else f"/{row['備註']}"
        formatted_date = format_date(datetime.now())

        if personal_order and personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] != str(row["*銷售單號"]):
            box_type, box_name = calculate_box_type(personal_order, product_info)
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

        new_row = {
            "貨主編號": "A442",
            "貨主單號\n(不同客戶端、不同溫層要分單)": str(row["*銷售單號"]),
            "客戶端代號(店號)": str(row["收件人"]),
            "訂購日期": formatted_date,
            "商品編號": product_code,
            "商品名稱": str(row["品名/規格"]),
            "訂購數量": str(row["採購數量"]),
            "配送方式\nFT : 逢泰配送\nTcat : 黑貓宅配\n全家到府取貨": "Tcat",
            "收貨人姓名": str(row["收件人"]),
            "收貨人地址": str(row["收件地址"]),
            "收貨人聯絡電話": str(row["收件人手機"]),
            "訂單 / 宅配單備註": "減醣市集" + order_mark,
            "品項備註": "",
            "指定配送溫層\n001：常溫\n002：冷藏\n003：冷凍": "003",
        }
        if str(row["*銷售單號"]) != "nan":
            if not personal_order or personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] == str(row["*銷售單號"]):
                personal_order.append(new_row)
            else:
                personal_order = [new_row]
            new_rows.append(new_row)

    if personal_order:
        box_type, box_name = calculate_box_type(personal_order, product_info)
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


def process_shopline_orders(sorted_data, address_info):
    product_info = ExcelController(data_path=FilePath.doc, sheet_name="product")
    new_rows = []
    personal_order = []
    skip_order = 0
    for _, row in sorted_data.iterrows():
        delivery_method, adress = get_delivery_info(row, address_info)
        product_mark = "" if len(str(row["商品貨號"]).split("-")) < 3 else "-" + str(row["商品貨號"]).split("-")[2]
        order_mark = "" if str(row["出貨備註"]) == "nan" else f"/{row['出貨備註']}"
        formatted_date = format_date(str(row["訂單日期"]))

        if personal_order and personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] != str(row["訂單號碼"]):
            box_type, box_name = calculate_box_type(personal_order, product_info)
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

        new_row = {
            "貨主編號": "A442",
            "貨主單號\n(不同客戶端、不同溫層要分單)": str(row["訂單號碼"]),
            "客戶端代號(店號)": str(row["收件人"]),
            "訂購日期": formatted_date,
            "預計到貨日": "",
            "商品編號": str(row["商品貨號"]),
            "商品名稱": f"{row['商品名稱'] + product_mark}",
            "訂購數量": str(row["數量"]),
            "配送方式\nFT : 逢泰配送\nTcat : 黑貓宅配\n全家到府取貨": delivery_method,
            "收貨人姓名": str(row["收件人"]),
            "收貨人地址": adress,
            "收貨人聯絡電話": str(row["收件人電話號碼"]),
            "訂單 / 宅配單備註": "減醣市集" + order_mark,
            "品項備註": "",
            "指定配送溫層\n001：常溫\n002：冷藏\n003：冷凍": "003",
        }
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
            pass

    if personal_order:
        box_type, box_name = calculate_box_type(personal_order, product_info)
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


def save_to_excel(new_rows, output_path):
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


def generate_report(input_data_path, output_path):
    if "." not in output_path:
        output_path += ".xlsx"
    original_data = ExcelController(input_data_path, sheet_name=0)
    original_data_count = len(original_data.df.columns)
    sorted_data = original_data.df.sort_values(by="收件人", ascending=True)
    if original_data_count >= 17:
        print("Shopline 訂單處理")
        adress = CheckAdress(original_data_path=input_data_path)
        loaction_info = adress.check_adress()
        print(f"\n原始資料筆數: {len(original_data.df)}")
        new_rows = process_shopline_orders(sorted_data, loaction_info)
    elif original_data_count >= 10:
        print("Mixx 訂單處理")
        print(f"\n原始資料筆數: {len(original_data.df)}")
        new_rows = process_mixx_orders(sorted_data)
    print(f"\n最終筆數: {len(new_rows)}")
    order_number = sorted_data["訂單號碼"] if "訂單號碼" in sorted_data else sorted_data["*銷售單號"]
    print(f"\n總訂單數: {len(order_number.unique())}")

    save_to_excel(new_rows, output_path)


if __name__ == "__main__":
    generate_report(
        input_data_path=r"/Users/jasonsung/Downloads/carbs_orders_20250402202303783001.xls",
        output_path="123",
    )
