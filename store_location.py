import pandas as pd
from config import *
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from excel_controller import ExcelController


class CheckAdress:

    def __init__(self, original_data_path):
        self.original_data = ExcelController(original_data_path, sheet_name=0)
        self.adress_file = ExcelController(FilePath.doc, sheet_name="store_location")

    def check_adress(self):
        filtered_711 = self.original_data.data_filter({"送貨方式": TargetShipping.seven})
        all_store_711 = filtered_711["門市名稱"].unique()
        location_711 = self.fetch_lcation(company=CompanyName.seven, store_list=all_store_711)
        filtered_family = self.original_data.data_filter({"送貨方式": TargetShipping.family})
        all_store_family = filtered_family["門市名稱"].unique()
        location_family = self.fetch_lcation(company=CompanyName.family, store_list=all_store_family)
        print(f"\n7-11地址\n{location_711}")
        print(f"\n全家地址\n{location_family}")
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
                print(f"新增7-11門市:「{store}」的資料地址: {address})")

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
        self.driver = self.open_chrome()
        self.wait = WebDriverWait(self.driver, 5)

    def open_chrome(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def web_wait(self):
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def seven_location_script(self, store):
        store_location_dict = {}
        try:
            self.driver.get("https://emap.pcsc.com.tw/")
            self.web_wait()
            store_name_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "shop_na")))
            store_name_input.clear()
            store_name_input.send_keys(store if "門市" not in store else store.split("門市")[0])
            self.wait.until(EC.element_to_be_clickable((By.ID, "Image_store_name"))).click()
            self.web_wait()
            self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='mytb']/tbody/tr")))
            store_info_element = self.driver.find_elements(By.XPATH, "//*[@id='mytb']/tbody/tr")
            if len(store_info_element) == 2:
                location_table = store_info_element[1].find_element(By.XPATH, ".//table/tbody/tr[2]/td").text
                location_text = location_table.split("\n")[0].split("：")[1].replace(" ", "")
                store_location_dict[store] = location_text
                self.driver.refresh()
            else:
                correct_store = False
                warning = f"ERROR : 可能出現多間類似{store}的店名，無法確認地址"
                for i in range(1, len(store_info_element)):
                    store_name = location_table = store_info_element[i].find_element(By.XPATH, "./td").text
                    if store_name == store.split("門市")[0]:
                        location_table = store_info_element[i].find_element(By.XPATH, ".//table/tbody/tr[2]/td").text
                        location_text = location_table.split("\n")[0].split("：")[1].replace(" ", "")
                        correct_store = True
                        break
                store_location_dict[store] = warning if not correct_store else location_text
                self.driver.refresh()
        except Exception as e:
            print(f"處理{store}門市時發生錯誤，{e}")
            warning = f"ERROR : 無法確認{store}正確地址"
            store_location_dict[store] = warning
            self.driver.refresh()
        return store_location_dict

    def family_location_script(self, store):
        store_location_dict = {}
        try:
            self.driver.get("https://www.family.com.tw/Marketing/zh/Map")
            self.web_wait()
            iframe = self.wait.until(EC.presence_of_element_located((By.ID, "map-iframe")))
            self.driver.switch_to.frame(iframe)
            store_name_input = self.wait.until(EC.visibility_of_element_located((By.ID, "shopName")))
            store_name_input.clear()
            store_name_input.send_keys(store)
            self.wait.until(EC.element_to_be_clickable((By.ID, "shopNameSearch"))).click()
            self.web_wait()
            self.wait.until(EC.visibility_of_element_located((By.XPATH, "(//*[@id='showShopList']//tbody)[2]/tr")))
            store_info_element = self.driver.find_elements(By.XPATH, "(//*[@id='showShopList']//tbody)[2]/tr")
            if len(store_info_element) == 1:
                location_table = store_info_element[0].text
                find_adress = [info for info in location_table.split("\n") if "地址" in info]
                location_text = find_adress[0].split("：")[1].replace(" ", "")
                store_location_dict[store] = location_text
                self.driver.refresh()
            else:
                correct_store = False
                for i in range(len(store_info_element)):
                    if store == store_info_element[i].find_element(By.XPATH, "./td").text:
                        correct_store = True
                        location_table = store_info_element[i].text
                        find_adress = [info for info in location_table.split("\n") if "地址" in info]
                        location_text = find_adress[0].split("：")[1].replace(" ", "")
                        pass
                warning = f"ERROR : 可能出現多間類似{store}的店名，無法確認地址"
                store_location_dict[store] = warning if not correct_store else location_text
                self.driver.refresh()
        except Exception as e:
            print(f"處理{store}門市時發生錯誤，{e}")
            warning = f"ERROR : 無法確認{store}正確地址"
            store_location_dict[store] = warning
            self.driver.refresh()
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
