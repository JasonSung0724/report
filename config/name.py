import os
import json

class ExcelFieldName:

    @staticmethod
    def get_config(platform):
        with open("config/field.json", "r") as f:
            field_config = json.load(f)
        return field_config[platform]

class TargetShipping:
    seven = "7-11低溫取貨"
    family = "全家低溫取貨"
    tacat = "低溫宅配"


class CompanyName:
    seven = "SEVEN"
    family = "FAMILY"
    tacat = "TACAT"


class FilePath:
    report = os.path.join(os.getcwd(), "config/report_template.xlsx")
