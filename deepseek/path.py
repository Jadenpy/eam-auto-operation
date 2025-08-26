from datetime import datetime
TODAY = datetime.now().strftime("%Y-%m-%d")

ERIC = "https://myeric.textron.com/"

EDGE = r"C:\Users\jhu00\OneDrive - Textron\Documents\code\eam-auto-operation\drive files\msedgedriver.exe"

# Selenium 4.3 模糊匹配 XPath 映射
locators = {
    # ======页面获取=========
    'page_eam': '//*[@id="MyTools"]/div/ul/li[7]/a',    #别名：EAM  HTML标签：a-tag     动作：点击ERIC主页上的该链接    切换新的标签页    
    'page_wo_tag': '//*[@id="tab-1052"]',               #别名：WO_TAG  HTML标签     动作：点击   切换FRAME
    'page_frame': "uxtabiframe-1040-iframeEl",           # BY.ID
    # =====工单列表获取======
    'list_date_filter_drop_button':'//*[@id="uxfilteroperator-1251"]',
    'list_date_condition':'#menuitem-1256',                                    # By.CSS_SELECTOR,
    'list_date_input': '#uxdate-1261-inputEl',                                 # By.CSS_SELECTOR,
    'list_wo': '//*[@id="tableview-1103"]/div[3]//table[starts-with(@id, "tableview-1103-record-")]',                                 
    # ===== WO 信息读取 =====       r: read
    "wo_r_start_date": '//*[@id="uxdate-1412-inputEl"]',  
    "wo_r_end_date": '//*[@id="uxdate-1413-inputEl"]',
    "wo_r_assigned_to": '//*[@id="lovfield-1414-inputEl"]',
    "wo_r_status": '//*[@id="uxcombobox-1415-inputEl"]',
    "wo_r_estimated_hours": '//*[@id="uxnumber-1425-inputEl"]', 

    # ===== 标签页 & 按钮类 =====    c: control
    "wo_c_record_view": '//*[@id="tab-1163-btnInnerEl"]',
    "wo_c_book_labor": '//*[@id="tab-1166-btnInnerEl"]',
    "wo_c_record_save": '//*[@id="button-1033-btnIconEl"]', 
    "wo_c_slide_bar": '//*[@id="panel-1093-splitter"]',
    "wo_c_submit": "(//*[starts-with(@id, 'button-') and substring(@id, string-length(@id) - string-length('-btnIconEl') +1) = '-btnIconEl'])[38]", # 索引从1开始
    
    # ===== WO 输入 =====           w: write
    "wo_r_panel": "(//*[starts-with(@id, 'panel-') and substring(@id, string-length(@id) - string-length('-bodyWrap') +1) = '-bodyWrap'])[19]",   # 索引从1开始
    "wo_w_employee": './/input[contains(@id, "lovmultiselectfield")]',
    "wo_w_hours_worked": './/input[contains(@id, "uxnumber")]',
    "wo_w_date_worked": './/input[contains(@id, "uxdate")]',
    "wo_c_dropdown": "(//*[starts-with(@id, 'uxcombobox-') and substring(@id, string-length(@id) - string-length('-trigger-picker') +1) = '-trigger-picker'])[5]",
    "wo_r_activity": "(//input[starts-with(@id, 'uxcombobox-') and substring(@id, string-length(@id)-6)='inputEl'])[9]",    
}
