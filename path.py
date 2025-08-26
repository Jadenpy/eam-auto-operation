

ERIC = "https://myeric.textron.com/"

# Selenium 4.3 模糊匹配 XPath 映射
locators = {
    'EAM': '//*[@id="MyTools"]/div/ul/li[7]/a',    # EAM a tag
    # ===== WO 信息读取 =====
    "start_date": '//*[@id="uxdate-1412-inputEl"]',
    "end_date": '//*[@id="uxdate-1413-inputEl"]',
    "assigned_to": '//*[@id="lovfield-1414-inputEl"]',
    "status": '//*[@id="uxcombobox-1415-inputEl"]',
    "estimated_hours": '//*[@id="uxnumber-1425-inputEl"]', 

    # ===== 标签页 & 按钮类 =====
    "record_view": '//*[@id="tab-1163-btnInnerEl"]',
    "book_labor": '//*[@id="tab-1166-btnInnerEl"]',
    "record_save": '//*[@id="button-1033-btnIconEl"]', 
    "slide_bar": '//*[@id="panel-1093-splitter"]',
    "submit": "(//*[starts-with(@id, 'button-') and substring(@id, string-length(@id) - string-length('-btnIconEl') +1) = '-btnIconEl'])[38]", # 索引从1开始
    
    # ===== WO 输入 =====
    "panel": "(//*[starts-with(@id, 'panel-') and substring(@id, string-length(@id) - string-length('-bodyWrap') +1) = '-bodyWrap'])[19]",   # 索引从1开始
    "employee": './/input[contains(@id, "lovmultiselectfield")]',
    "hours_worked": './/input[contains(@id, "uxnumber")]',
    "date_worked": './/input[contains(@id, "uxdate")]',
    "dropdown": "(//*[starts-with(@id, 'uxcombobox-') and substring(@id, string-length(@id) - string-length('-trigger-picker') +1) = '-trigger-picker'])[5]",
    "activity": "(//input[starts-with(@id, 'uxcombobox-') and substring(@id, string-length(@id)-6)='inputEl'])[9]",    
}
