# 验证extJSSeleniumHelper的功能是否可行
from extJSSeleniumHelper import ExtJSSeleniumHelper
from path import ERIC, EDGE, locators,TODAY,page_title
from selenium.webdriver.common.by import By
import time

def eam_auto():
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

    mySite.switch_to_new_tab(page_title['eam'])
    
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
    mySite.ensure_element_visible(locators['list_date_condition'],By.CSS_SELECTOR)
    mySite.safe_click(locators['list_date_condition'],By.CSS_SELECTOR)   
    # 6.3 日期输入
    mySite.ensure_element_visible(locators['list_date_input'],By.CSS_SELECTOR)
    mySite.safe_input(locators['list_date_input'],TODAY,By.CSS_SELECTOR,enter=True)

    # 等待运算完成
    time.sleep(2)

    # 7. 工单列表
    # tables = mySite.find_elements(By.XPATH, locators['list_wo'])
    
    if mySite.wait_for_element_clickable(locators['list_wo']):
        wos = mySite.get_elements(locators['list_wo'])
    # 8. 遍历工单并进行处理   
    if wos:
       for index, wo in enumerate(wos, start=1):
            # double click
            if mySite.wait_for_element_clickable(locators['list_wo']):
                mySite.double_click(wo)
            # click 
            mySite.safe_click(locators["wo_c_record_view"])
            # get value
            start_date = mySite.find_clickable_element(locators["wo_r_start_date"]).get_attribute('value')
            # get value
            end_date = mySite.find_clickable_element(locators["wo_r_end_date"]).get_attribute('value')
            # get value
            person = mySite.find_clickable_element(locators["wo_r_assigned_to"]).get_attribute('value')
            # get value
            status = mySite.find_clickable_element(locators["wo_r_status"]).get_attribute('value')
            # get value
            estimated_hours = mySite.find_clickable_element(locators["wo_r_estimated_hours"]).get_attribute('value')

            # double click side bar
            side_bar = mySite.find_clickable_element(locators["wo_c_slide_bar"])
            mySite.double_click(side_bar)

            # 供测试遍历工单 print(f'工单{index}: 开始日期：{start_date}，截止日期：{end_date}，所属人员：{person}，状态：{status}，计划工时：{estimated_hours}')

            

            

def wo_operation(wo):
    #1. 双击工单
    pass
                             

if __name__ == '__main__':

    eam_auto()
    
    

