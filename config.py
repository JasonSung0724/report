import os


class TargetShipping:
    seven = "7-11低溫取貨"
    family = "全家低溫取貨"
    tacat = "低溫宅配"


class CompanyName:
    seven = "SEVEN"
    family = "FAMILY"
    tacat = "TACAT"


class FilePath:
    doc = os.path.join(os.getcwd(), "doc.xlsx")
    report = os.path.join(os.getcwd(), "report_template.xlsx")
