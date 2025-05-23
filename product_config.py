from typing import Optional, Dict, Any
import json
from config import FileConfig


class ProductConfig:
    def __init__(self):
        self._load_config()

    def _load_config(self) -> None:
        """Load product configuration from JSON file."""
        try:
            with open(FileConfig.product_config, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"錯誤: 找不到配置文件 {FileConfig.product_config}")
            self.config = {}
        except json.JSONDecodeError:
            print(f"錯誤: 配置文件 {FileConfig.product_config} 格式不正確")
            self.config = {}

    def search_product(self, search_value: str, search_type: str = "mixx_name") -> Optional[str]:
        """
        Search for a product code based on search value and type.

        Args:
            search_value: Value to search for
            search_type: Type of search ('mixx_name' or 'c2c_code')

        Returns:
            Product code if found, None otherwise
        """
        try:
            for product_code, product_info in self.config.items():
                if search_type == "mixx_name" and search_value in product_info.get("mixx_name", ""):
                    return product_code
                elif search_type == "c2c_code" and product_info.get("c2c_code") == search_value:
                    return product_code
            return None
        except Exception as e:
            print(f"搜尋產品時發生錯誤: {e}")
            return None

    def get_product_quantity(self, product_code: str) -> int:
        """
        Get the quantity for a product.

        Args:
            product_code: Product code to look up

        Returns:
            Quantity if found, 0 otherwise
        """
        try:
            return self.config.get(product_code, {}).get("qty", 0)
        except Exception as e:
            print(f"獲取產品數量時發生錯誤: {e}")
            return 0

    def get_product_info(self, product_code: str) -> Dict[str, Any]:
        """
        Get all information for a product.

        Args:
            product_code: Product code to look up

        Returns:
            Product information dictionary
        """
        try:
            return self.config.get(product_code, {})
        except Exception as e:
            print(f"獲取產品信息時發生錯誤: {e}")
            return {}
