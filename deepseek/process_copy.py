# 验证extJSSeleniumHelper的功能是否可行
from extJSSeleniumHelper_copy import ExtJSSeleniumHelper
from path_copy import ERIC, EDGE, locators,TODAY,page_title
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import Optional,Union
from selenium.webdriver.remote.webelement import WebElement

def open_eam()->Optional[Union[ExtJSSeleniumHelper]]:
    # 1. 配置selenium
    try:
        mySite = ExtJSSeleniumHelper(executable_path=EDGE)

        # 2.打开eric的首页
        mySite.openURL(ERIC)

        # 3. EAM link, click on it
        mySite.element_click(locators['page_eam'])
        
        # 4. change to the new tag
        # mySite.switch_to_new_tab(page_title['eam'])
        if mySite.tab_change(page_title['eam']):
            return mySite
    except:
        print(f'网页开启失败')
        raise

    finally:
        pass
        

def get_wo_list(mySite:ExtJSSeleniumHelper)->list:
    # 4. WO Tab
    try:
        mySite.element_click(locators['page_wo_tag'])
        # 5. iframe
        
        mySite.switch_to_iframe((By.ID,locators['page_iframe']))

        # 6. 筛选工单
        # 6.1 日期筛选下拉按钮
        
        mySite.element_click(locators['list_date_filter_drop_button'])
        # 6.2 日期比较条件  <=
        
        mySite.element_click(locators['list_date_condition'],pos_by=By.CSS_SELECTOR)   
        # 6.3 日期输入
        
        mySite.element_write(locators['list_date_input'],TODAY,By.CSS_SELECTOR,True)
        # 等待运算完成
        time.sleep(3)

        # # 7. 工单列表
        work_order_list = mySite.elements_get(locators['list_wo'])
        
        if work_order_list:
            print(f'获取工单列表成功：工单数量：{len(work_order_list)}')
            return work_order_list
    except:
        print(f'工单列表获取失败')
        raise

    finally:
        pass
    
def read_work_order_information(mySite:ExtJSSeleniumHelper,wo:WebElement) ->tuple:
    
    try:   
        # double click
        mySite.element_double_click(wo)
        # click record view tag
        mySite.element_click(locators["wo_c_record_view"])
        # 开始日期
        start_date = mySite.element_read(locators["wo_r_start_date"])
        # 结束日期
        end_date = mySite.element_read(locators["wo_r_end_date"])
        # 所属人员
        person = mySite.element_read(locators["wo_r_assigned_to"])
        # 所需工时
        estimated_hours = mySite.element_read(locators["wo_r_estimated_hours"])
        # click book labor  
        mySite.element_click(locators["wo_c_book_labor"])

        return  start_date, end_date, person, estimated_hours 
    except:
        raise
    finally:
        pass


def fill_out_work_order(mySite:ExtJSSeleniumHelper, wo:WebElement):
    try:
        information = read_work_order_information(mySite, wo)
        start_date, end_date, person, estimated_hours = information
        # panel
        panel = mySite.element_get(locators["wo_r_panel"])
        # 是否activity 有值
        activity = panel.find_element(By.XPATH,locators["wo_r_activity"])
        activity_value = activity.get_attribute('value').strip()
        
        if not activity_value:
            activity.clear()
            activity.send_keys('10 - DEFAULT / ALL TRADES')   

        # fill in
        # 所属人员
        mySite.element_child_send_keys(panel,person,locators["wo_w_employee"])
    
        work_hour = "{:.1f}".format(float(estimated_hours) / 2)
        # 实际工时
        
        mySite.element_child_send_keys(panel,work_hour,locators["wo_w_hours_worked"])
        # 实际日期
        
        mySite.element_child_send_keys(panel,start_date,locators["wo_w_date_worked"])

        # form save
        mySite.element_click(locators["wo_c_submit"])

        # record save
        mySite.element_click(locators["wo_c_record_save"])

        # go back record view tab
        
        mySite.element_click(locators["wo_c_record_view"])

        # update status
        mySite.element_write(locators["wo_r_status"],'Completed')

        # final save
        mySite.element_click(locators["wo_c_record_save"])

        # double click side bar
        side_bar = mySite.element_get(locators["wo_c_slide_bar"])
        mySite.element_double_click(side_bar)
        
    except:    
        raise

    finally:
        pass

        

            

        
                             

if __name__ == '__main__':

    w = open_eam()
    orders = get_wo_list(mySite=w)

    for index, work_order in  enumerate(orders,start=1):
        fill_out_work_order(w,work_order)
    

    
    

