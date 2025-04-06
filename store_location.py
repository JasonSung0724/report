import pandas as pd
from config import *
from excel_controller import ExcelController
import requests
import xml.etree.ElementTree as ET
import json


class CheckAdress:

    def __init__(self, original_data_path):
        self.original_data = ExcelController(original_data_path, sheet_name=0)
        self.adress_file = ExcelController(FilePath.doc, sheet_name="store_location")

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
        return location_711, location_family

    def fetch_lcation(self, company, store_list):

        location_dict = {}
        missing_stores = []

        for store_711 in store_list:
            matched = self.adress_file.data_filter({"門市名稱": store_711, "商店": company})
            if matched.empty:
                print(f"{company} 「{store_711}」門市沒有對應的地址資料")
                missing_stores.append(store_711)
            else:
                location_dict[store_711] = matched["地址"].values[0]
        if missing_stores:
            script = FindLocationOnWeb()
            found_location = script.find_location(company=company, store_name_list=missing_stores)
            location_dict = location_dict | found_location
            self.update_location(company=company, new_location_data=found_location)
        return location_dict

    def update_location(self, company, new_location_data):
        store_location_data = self.adress_file
        for store, address in new_location_data.items():
            existing_row = self.adress_file.data_filter({"門市名稱": store, "商店": company})
            if len(existing_row) == 0:
                new_row = pd.DataFrame({"商店": [company], "門市名稱": [store], "地址": [address]})
                store_location_data.df = pd.concat([store_location_data.df, new_row], ignore_index=True)
                print(f"新增{company}門市:「{store}」的資料地址: {address})")

            elif pd.isna(existing_row["地址"].values[0]) or existing_row["地址"].values[0] == "":
                store_location_data.loc[(store_location_data["門市名稱"] == store) & (store_location_data["商店"] == company), "地址"] = address
                print(f"更新門市「{store}」的地址: {address}")
            else:
                print(f"門市「{store}」已存在且有地址資料")
        try:
            store_location_data.save_excel_with_multiple_sheets(sheet_name="store_location", file_path=FilePath.doc)
            print("已成功更新Store_location")
        except Exception as e:
            print(f"寫入Excel時發生錯誤: {e}")
            return new_location_data


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
