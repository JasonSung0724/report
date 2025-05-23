import pandas as pd
from typing import Dict, Any, List
from config import config
import requests
import xml.etree.ElementTree as ET
import json


class CheckAdress:
    def __init__(self, original_data_path: str):
        self.original_data_path = original_data_path

    def check_adress(self) -> Dict[str, Dict[str, str]]:
        """
        Check and process store addresses from the original data.

        Returns:
            Dictionary containing store information for different companies
        """
        try:
            df = pd.read_excel(self.original_data_path)
            store_info = {config.company.FAMILY: {}, config.company.SEVEN: {}}

            filtered_seven = df[df["送貨方式"].str.startswith(config.shipping.SEVEN, na=False)]
            filtered_family = df[df["送貨方式"].str.startswith(config.shipping.FAMILY, na=False)]

            # Get unique store names
            seven_stores = filtered_seven["門市名稱"].unique()
            family_stores = filtered_family["門市名稱"].unique()

            # Find locations
            location_finder = FindLocationOnWeb()
            seven_locations = location_finder.find_locations(company_type="SEVEN", store_names=seven_stores)
            family_locations = location_finder.find_locations(company_type="FAMILY", store_names=family_stores)

            # Print statistics
            print(f"\n7-11筆數: {len(filtered_seven['收件人'].unique())}\n{filtered_seven['收件人'].unique()}")
            print(f"\n全家筆數: {len(filtered_family['收件人'].unique())}\n{filtered_family['收件人'].unique()}")

            return {config.company.SEVEN: seven_locations, config.company.FAMILY: family_locations}

        except Exception as e:
            print(f"處理門市地址時發生錯誤: {e}")
            return {config.company.FAMILY: {}, config.company.SEVEN: {}}


class FindLocationOnWeb:
    def __init__(self):
        self.headers = {
            "Referer": "https://www.family.com.tw/",
        }

    def find_locations(self, company_type: str, store_names: List[str]) -> Dict[str, str]:
        """
        Find store locations for a list of store names.

        Args:
            company_type: Type of company ("SEVEN" or "FAMILY")
            store_names: List of store names to look up

        Returns:
            Dictionary mapping store names to their addresses
        """
        store_locations = {}
        for store in store_names:
            if not store or str(store) == "nan":
                continue

            if company_type == "SEVEN":
                location = self._get_seven_location(store)
            elif company_type == "FAMILY":
                location = self._get_family_location(store)
            else:
                continue

            store_locations.update(location)
        return store_locations

    def _get_seven_location(self, store: str) -> Dict[str, str]:
        """Get location for a 7-11 store."""
        store_location = {}
        input_name = store if "門市" not in store else store.split("門市")[0]

        try:
            url = "https://emap.pcsc.com.tw/EMapSDK.aspx"
            data = {
                "commandid": "SearchStore",
                "city": "",
                "town": "",
                "roadname": "",
                "ID": "",
                "StoreName": input_name,
                "SpecialStore_Kind": "",
                "leftMenuChecked": "",
                "address": "",
            }

            response = requests.post(url, data=data)
            xml_data = response.text
            root = ET.fromstring(xml_data)

            for geo_position in root.findall("GeoPosition"):
                address = geo_position.find("Address").text
                name = geo_position.find("POIName").text
                if name == input_name:
                    store_location[store] = address
                    break

            if not store_location:
                store_location[store] = f"ERROR : 無法確認{store}正確地址"

        except Exception as e:
            print(f"獲取7-11門市地址時發生錯誤 ({store}): {e}")
            store_location[store] = f"ERROR : 系統錯誤"

        return store_location

    def _get_family_location(self, store: str) -> Dict[str, str]:
        """Get location for a Family Mart store."""
        store_location = {}

        try:
            url = "https://api.map.com.tw/net/familyShop.aspx"
            params = {"searchType": "ShopName", "type": "", "kw": store, "fun": "getByName", "key": "6F30E8BF706D653965BDE302661D1241F8BE9EBC"}

            response = requests.get(url, params=params, headers=self.headers)
            start_index = response.text.find("[")
            end_index = response.text.rfind("]") + 1
            json_text = response.text[start_index:end_index]
            data = json.loads(json_text)

            for store_info in data:
                if store == store_info["NAME"]:
                    store_location[store] = store_info["addr"]
                    break

            if not store_location:
                store_location[store] = f"ERROR : 無法確認{store}正確地址"

        except Exception as e:
            print(f"獲取全家門市地址時發生錯誤 ({store}): {e}")
            store_location[store] = f"ERROR : 系統錯誤"

        return store_location
