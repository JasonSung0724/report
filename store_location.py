import pandas as pd
from config import *
from excel_controller import ExcelController
import requests
import xml.etree.ElementTree as ET
import json


class CheckAdress:

    def __init__(self, original_data_path):
        self.original_data = ExcelController(original_data_path, sheet_name=0)

    def check_adress(self):
        filtered_711 = self.original_data.data_filter({"送貨方式": lambda x: x.startswith(TargetShipping.seven)})
        all_store_711 = filtered_711["門市名稱"].unique()
        location_711 = self.fetch_lcation(company=CompanyName.seven, store_list=all_store_711)
        filtered_family = self.original_data.data_filter({"送貨方式": lambda x: x.startswith(TargetShipping.family)})
        all_store_family = filtered_family["門市名稱"].unique()
        location_family = self.fetch_lcation(company=CompanyName.family, store_list=all_store_family)
        # print(f"\n7-11地址\n{location_711}")
        # print(f"\n全家地址\n{location_family}")
        print(f"\n7-11筆數: {len(filtered_711['收件人'].unique())}\n{filtered_711['收件人'].unique()}")
        print(f"\n全家筆數: {len(filtered_family['收件人'].unique())}\n{filtered_family['收件人'].unique()}")
        location_info = {CompanyName.seven: location_711, CompanyName.family: location_family}
        return location_info

    def fetch_lcation(self, company, store_list):

        find_stores = []
        for store_711 in store_list:
            find_stores.append(store_711)
        if find_stores:
            script = FindLocationOnWeb()
            found_location = script.find_location(company=company, store_name_list=find_stores)

        return found_location


class FindLocationOnWeb:

    def __init__(self):
        pass

    def seven_location_script(self, store):
        store_location_dict = {}
        input_name = store if "門市" not in store else store.split("門市")[0]
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
                store_location_dict[store] = address
        if not store_location_dict:
            store_location_dict[store] = f"ERROR : 無法確認{store}正確地址"
        return store_location_dict

    def family_location_script(self, store):
        store_location_dict = {}
        url = "https://api.map.com.tw/net/familyShop.aspx"
        params = {"searchType": "ShopName", "type": "", "kw": store, "fun": "getByName", "key": "6F30E8BF706D653965BDE302661D1241F8BE9EBC"}
        headers = {
            "Referer": "https://www.family.com.tw/",
        }
        response = requests.get(url, params=params, headers=headers)
        start_index = response.text.find("[")
        end_index = response.text.rfind("]") + 1
        json_text = response.text[start_index:end_index]
        data = json.loads(json_text)
        for store_info in data:
            if store == store_info["NAME"]:
                store_location_dict[store] = store_info["addr"]

        if not store_location_dict:
            store_location_dict[store] = f"ERROR : 無法確認{store}正確地址"
        return store_location_dict

    def find_location(self, company, store_name_list):
        store_location_dict = {}
        for store in store_name_list:
            if company == CompanyName.seven:
                found_location = self.seven_location_script(store=store)
            elif company == CompanyName.family:
                found_location = self.family_location_script(store=store)
            store_location_dict.update(found_location)
        return store_location_dict
