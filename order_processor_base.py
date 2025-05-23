from datetime import datetime
from typing import Dict, Any, List, Tuple
import pandas as pd
from config import config


class BaseOrderProcessor:
    def format_date(self, order_time: Any) -> str:
        """Format the order date to YYYYMMDD format."""
        try:
            if isinstance(order_time, datetime):
                date_time_format = order_time
            else:
                date_time_format = datetime.strptime(str(order_time), "%Y-%m-%d %H:%M:%S")
            return date_time_format.strftime("%Y%m%d")
        except (ValueError, TypeError):
            return "INVALID_DATE"

    def calculate_box_type(self, personal_order: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Calculate box type based on order quantity."""
        grand_total = 0
        product_config = config.load_product_config()

        for order in personal_order:
            try:
                product_id = str(order["商品編號"])
                if product_id and product_id != "nan":
                    qty = product_config[product_id]["qty"]
                    grand_total += qty * int(float(order["訂購數量"]))
            except (KeyError, ValueError) as e:
                print(f"處理商品編號 {order['商品編號']} 時發生錯誤: {e}")
                raise

        if grand_total <= 14:
            return "box60-EA", "60公分紙箱"
        elif grand_total <= 47:
            return "box90-EA", "90公分紙箱"
        return "ERROR-需拆單", "ERROR-需拆單"

    def create_base_order_row(self) -> Dict[str, str]:
        """Create base order row with common fields."""
        return {
            "貨主編號": config.order.OWNER_ID,
            "指定配送溫層\n001：常溫\n002：冷藏\n003：冷凍": config.order.TEMPERATURE,
            "品項備註": "",
        }

    def add_box_to_order(self, personal_order: List[Dict[str, Any]], new_rows: List[Dict[str, Any]]) -> None:
        """Add box information to the order."""
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

    def process_orders(self, sorted_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Template method for processing orders. Should be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement process_orders method")
