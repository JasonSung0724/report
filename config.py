from dataclasses import dataclass
from typing import Dict, Any
import json
import os


@dataclass
class FileConfig:
    report_template: str = "report_template.xlsx"
    product_config: str = "product_config.json"


@dataclass
class ShippingConfig:
    TACAT: str = "黑貓宅配"
    FAMILY: str = "全家取貨"
    SEVEN: str = "7-11取貨"


@dataclass
class CompanyConfig:
    FAMILY: str = "全家便利商店"
    SEVEN: str = "7-11"


@dataclass
class OrderConfig:
    OWNER_ID: str = "A442"
    TEMPERATURE: str = "003"  # 冷凍
    DEFAULT_REMARK: str = "減醣市集"
    C2C_REMARK: str = "減醣市集 X 快電商 C2C BUY"
    SPECIAL_PRODUCT: str = "F2500000044"


class Config:
    def __init__(self):
        self.file = FileConfig()
        self.shipping = ShippingConfig()
        self.company = CompanyConfig()
        self.order = OrderConfig()

    @staticmethod
    def load_product_config() -> Dict[str, Any]:
        with open(FileConfig.product_config, "r", encoding="utf-8") as f:
            return json.load(f)


config = Config()
