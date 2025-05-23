from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from order_processor_base import BaseOrderProcessor
from config import config
from product_config import ProductConfig


class C2COrderProcessor(BaseOrderProcessor):
    def __init__(self):
        self.product_config = ProductConfig()

    def create_order_row(self, base_data: Dict[str, Any], product_code: str, order_mark: str, formatted_date: str) -> Dict[str, str]:
        base_row = self.create_base_order_row()
        base_row.update(
            {
                "貨主單號\n(不同客戶端、不同溫層要分單)": str(base_data["平台訂單編號"]),
                "客戶端代號(店號)": str(base_data["收件者姓名"]),
                "訂購日期": formatted_date,
                "商品編號": product_code,
                "商品名稱": str(base_data["商品樣式"]).replace("-F", ""),
                "訂購數量": str(base_data["小計數量"]),
                "配送方式\nFT : 逢泰配送\nTcat : 黑貓宅配\n全家到府取貨": "Tcat",
                "收貨人姓名": str(base_data["收件者姓名"]),
                "收貨人地址": str(base_data["收件者地址"]),
                "收貨人聯絡電話": str(base_data["收件者手機"]),
                "訂單 / 宅配單備註": config.order.C2C_REMARK + order_mark,
            }
        )
        return base_row

    def process_orders(self, sorted_data: pd.DataFrame) -> List[Dict[str, Any]]:
        new_rows = []
        personal_order = []

        for _, row in sorted_data.iterrows():
            if str(row["商品編號"]) == config.order.SPECIAL_PRODUCT:
                self._process_special_product(row, personal_order, new_rows)
            else:
                self._process_regular_product(row, personal_order, new_rows)

        self.add_box_to_order(personal_order, new_rows)
        return new_rows

    def _process_special_product(self, row: pd.Series, personal_order: List[Dict[str, Any]], new_rows: List[Dict[str, Any]]) -> None:
        for i in range(2):
            product_code = self.product_config.search_product(search_type="c2c_code", search_value=f"{config.order.SPECIAL_PRODUCT}-{i}")
            self._process_order_item(row, product_code, personal_order, new_rows, split_index=i)

    def _process_regular_product(self, row: pd.Series, personal_order: List[Dict[str, Any]], new_rows: List[Dict[str, Any]]) -> None:
        product_code = self.product_config.search_product(search_type="c2c_code", search_value=str(row["商品編號"]))
        self._process_order_item(row, product_code, personal_order, new_rows)

    def _process_order_item(
        self, row: pd.Series, product_code: str, personal_order: List[Dict[str, Any]], new_rows: List[Dict[str, Any]], split_index: int = None
    ) -> None:
        order_mark = "" if str(row["出貨備註"]) == "nan" else f" | {row['出貨備註']}"
        formatted_date = self.format_date(row["建立時間"])
        new_row = self.create_order_row(row, product_code, order_mark, formatted_date)

        if split_index is not None:
            new_row["商品名稱"] = str(row["商品樣式"]).replace("(贈品)-F", "").split("+")[split_index]

        if str(row["平台訂單編號"]) != "nan":
            if not personal_order or personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] == str(row["平台訂單編號"]):
                personal_order.append(new_row)
            else:
                self.add_box_to_order(personal_order, new_rows)
                personal_order = [new_row]
            new_rows.append(new_row)


class MixxOrderProcessor(BaseOrderProcessor):
    def __init__(self):
        self.product_config = ProductConfig()

    def create_order_row(self, base_data: Dict[str, Any], product_code: str, order_mark: str, formatted_date: str) -> Dict[str, str]:
        base_row = self.create_base_order_row()
        base_row.update(
            {
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
                "訂單 / 宅配單備註": config.order.DEFAULT_REMARK + order_mark,
            }
        )
        return base_row

    def process_orders(self, sorted_data: pd.DataFrame) -> List[Dict[str, Any]]:
        new_rows = []
        personal_order = []

        for _, row in sorted_data.iterrows():
            product_code = self.product_config.search_product(search_type="mixx_name", search_value=str(row["品名/規格"]).split("｜")[1])
            order_mark = "" if str(row["備註"]) == "nan" else f"/{row['備註']}"
            formatted_date = self.format_date(datetime.now())

            if personal_order and personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] != str(row["*銷售單號"]):
                self.add_box_to_order(personal_order, new_rows)
                personal_order.clear()

            new_row = self.create_order_row(row, product_code, order_mark, formatted_date)

            if str(row["*銷售單號"]) != "nan":
                if not personal_order or personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] == str(row["*銷售單號"]):
                    personal_order.append(new_row)
                else:
                    personal_order = [new_row]
                new_rows.append(new_row)

        self.add_box_to_order(personal_order, new_rows)
        return new_rows


class ShoplineOrderProcessor(BaseOrderProcessor):
    def create_order_row(self, base_data: Dict[str, Any], order_mark: str, formatted_date: str) -> Dict[str, str]:
        base_row = self.create_base_order_row()
        base_row.update(
            {
                "貨主單號\n(不同客戶端、不同溫層要分單)": str(base_data["訂單號碼"]),
                "客戶端代號(店號)": str(base_data["收件人"]),
                "訂購日期": formatted_date,
                "預計到貨日": "",
                "商品編號": str(base_data["商品貨號"]),
                "商品名稱": f"{base_data['商品名稱']}{base_data.get('product_mark', '')}",
                "訂購數量": str(base_data["數量"]),
                "配送方式\nFT : 逢泰配送\nTcat : 黑貓宅配\n全家到府取貨": base_data["delivery_method"],
                "收貨人姓名": str(base_data["收件人"]),
                "收貨人地址": base_data["address"],
                "收貨人聯絡電話": str(base_data["收件人電話號碼"]),
                "訂單 / 宅配單備註": config.order.DEFAULT_REMARK + order_mark,
            }
        )
        return base_row

    def get_delivery_info(self, row: pd.Series, store_address: Dict[str, Dict[str, str]]) -> tuple[str, str]:
        shipping_method = row["送貨方式"].split("（", 1)[0]

        if shipping_method == config.shipping.TACAT:
            return "Tcat", row["完整地址"]
        elif shipping_method == config.shipping.FAMILY:
            store_name = row["門市名稱"]
            if store_name not in store_address[config.company.FAMILY]:
                return "全家", "ERROR"
            return "全家", f"{store_name} ({store_address[config.company.FAMILY][store_name]})"
        elif shipping_method == config.shipping.SEVEN:
            store_name = row["門市名稱"]
            if store_name not in store_address[config.company.SEVEN]:
                return "7-11", "ERROR"
            return "7-11", "(宅轉店)" + store_address[config.company.SEVEN][store_name]
        return "UNKNOWN", "ERROR"

    def process_orders(self, sorted_data: pd.DataFrame, address_info: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
        new_rows = []
        personal_order = []
        skip_order = 0

        for _, row in sorted_data.iterrows():
            delivery_method, address = self.get_delivery_info(row, address_info)
            product_mark = "" if len(str(row["商品貨號"]).split("-")) < 3 else "-" + str(row["商品貨號"]).split("-")[2]
            order_mark = "" if str(row["出貨備註"]) == "nan" else f"/{row['出貨備註']}"
            formatted_date = self.format_date(str(row["訂單日期"]))

            if personal_order and personal_order[0]["貨主單號\n(不同客戶端、不同溫層要分單)"] != str(row["訂單號碼"]):
                self.add_box_to_order(personal_order, new_rows)
                personal_order.clear()

            row_data = row.to_dict()
            row_data.update({"delivery_method": delivery_method, "address": address, "product_mark": product_mark})

            new_row = self.create_order_row(row_data, order_mark, formatted_date)

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

        self.add_box_to_order(personal_order, new_rows)
        print(f"\n商品貨號空白故扣除筆數：{skip_order}")
        return new_rows
