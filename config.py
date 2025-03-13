import os


class TargetShipping:
    seven = "7-11低溫取貨（下單後  1~5 個工作天內出貨｜離島不配送）填寫完整門市名稱"
    family = "全家低溫取貨（下單後  1~5 個工作天內出貨｜離島不配送）填寫完整門市名稱"
    tacat = "低溫宅配（台灣本島）（下單後 1~5 個工作天內出貨）"


class CompanyName:
    seven = "SEVEN"
    family = "FAMILY"
    tacat = "TACAT"


class FilePath:
    doc = os.path.join(os.getcwd(), "doc.xlsx")
    report = os.path.join(os.getcwd(), "report_template.xlsx")
