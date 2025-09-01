# 验证extJSSeleniumHelper的功能是否可行
from extJSSeleniumHelper import ExtJSSeleniumHelper
from path import ERIC, EDGE, locators,TODAY,page_title
from selenium.webdriver.common.by import By
import time



def open_eam():
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

    return mySite

def get_wo_list(mySite:ExtJSSeleniumHelper):
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
        return wos
    



def handle_work_order(mySite:ExtJSSeleniumHelper, wo):   
    # double click
    if mySite.wait_for_element_clickable(locators['list_wo']):
        mySite.double_click(wo)
    # click 
    mySite.safe_click(locators["wo_c_record_view"])
    # get value
    el = mySite.find_clickable_element(locators["wo_r_start_date"])
    if el:
        start_date = el.get_attribute('value')
    # get value
    el = mySite.find_clickable_element(locators["wo_r_end_date"])
    end_date = el.get_attribute('value')
    # get value
    el = mySite.find_clickable_element(locators["wo_r_assigned_to"])
    if el:
        person = el.get_attribute('value')
    # get value
    el = mySite.find_clickable_element(locators["wo_r_status"])
    if el:
        status = el.get_attribute('value')
    # get value
    el = mySite.find_clickable_element(locators["wo_r_estimated_hours"])
    if el:
        estimated_hours = el.get_attribute('value')

    # book labor  
    mySite.safe_click(locators["wo_c_book_labor"])


    # panel
    if mySite.wait_for_element_clickable(locators["wo_r_panel"]):

        panel = mySite.find_clickable_element(locators["wo_r_panel"])
        # 是否activity 有值
        activity = panel.find_element(By.XPATH,locators["wo_r_activity"])
        activity_value = activity.get_attribute('value').strip()
        if not activity_value:
            activity.clear()
            activity.send_keys('10 - DEFAULT / ALL TRADES')   

        # fill in

        if mySite.wait_for_element_clickable(locators["wo_w_employee"]):
            mySite.safe_input(locators["wo_w_employee"],person)
        print(f'计划工时为：{estimated_hours}')
        if estimated_hours == '':
            estimated_hours = '0.5'
        work_hour = str(int((float(estimated_hours) / 2)))

        if mySite.wait_for_element_clickable(locators["wo_w_hours_worked"]):
            mySite.safe_input(locators["wo_w_hours_worked"],work_hour)

        if mySite.wait_for_element_clickable(locators["wo_w_date_worked"]):
            mySite.safe_input(locators["wo_w_date_worked"],start_date)


        # form save
        if mySite.wait_for_element_clickable(locators["wo_c_submit"]):
            mySite.safe_click(locators["wo_c_submit"])

        # record save
        if mySite.wait_for_element_clickable(locators["wo_c_record_save"]):
            mySite.safe_click(locators["wo_c_record_save"])

        # go back record view tab
        if mySite.wait_for_element_clickable(locators["wo_c_record_view"]):
            mySite.safe_click(locators["wo_c_record_view"])

        # update status

        if mySite.wait_for_element_clickable(locators["wo_r_status"]):
            mySite.safe_input(locators["wo_r_status"],'Completed')

        # final save
        if mySite.wait_for_element_clickable(locators["wo_c_record_save"]):
            mySite.safe_click(locators["wo_c_record_save"])
        
    else:
        print('没有找到panel')


    # double click side bar
    side_bar = mySite.find_clickable_element(locators["wo_c_slide_bar"])
    mySite.double_click(side_bar)

        

            

        
                             

if __name__ == '__main__':

    pass

    
    

