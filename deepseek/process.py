# 验证extJSSeleniumHelper的功能是否可行
from extJSSeleniumHelper import ExtJSSeleniumHelper
from path import ERIC, EDGE, locators,TODAY
from selenium.webdriver.common.by import By
import time



if __name__ == '__main__':
    # 1. 配置selenium
    mySite = ExtJSSeleniumHelper(executable_path=EDGE)

    # 2.打开eric的首页
    success = mySite.load_extjs_page(ERIC)
    if success:
        print('eric的首页加载成功')

    else:
        print('eric的首页加载失败')

    # 3. EAM link
    mySite.ensure_element_visible(locators['page_eam'])
    mySite.safe_click(locators['page_eam'])
    mySite.switch_to_new_tab()
    
    # 4. WO Tab
    mySite.ensure_element_visible(locators['page_wo_tag'])
    mySite.safe_click(locators['page_wo_tag'])

    # 5. iframe
    mySite.switch_to_iframe((By.ID,locators['page_iframe']))

    # 6. 筛选工单
    # 6.1 日期筛选下拉按钮
    mySite.ensure_element_visible(locators['list_date_filter_drop_button'])
    mySite.safe_click(locators['list_date_filter_drop_button'])
    # 6.2 日期比较条件  <=
    mySite.ensure_element_visible(locators['list_date_condition'])
    mySite.safe_click(locators['list_date_condition'])   
    # 6.3 日期输入
    mySite.ensure_element_visible(locators['list_date_input'])
    mySite.safe_input(locators['list_date_input'],TODAY,enter=True)

    # 等待运算完成
    time.sleep(2)

    # 7. 工单列表
    # mySite.
    

