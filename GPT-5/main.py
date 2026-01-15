from ast import Return
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from datetime import datetime, timedelta
from selenium.webdriver.remote.webelement import WebElement
import time


URL = 'https://eu1.eam.hxgnsmartcloud.com/web/base/logindisp?tenant=KAUTEX_PRD'

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option('detach',True)  #不自动关闭浏览器
service = Service(executable_path=r'C:\baiduDownload\msedgedriver.exe')

driver = webdriver.Edge(service=service, options=options)
wait = WebDriverWait(driver, 600)  # 国外服务器，时间一定要长


def wait_ext_ready():
    wait.until(lambda d: d.execute_script(
        "return window.Ext && Ext.isReady === true"
    ))


def wait_ajax_done():
    wait.until(lambda d: d.execute_script(
        "return Ext.Ajax.isLoading() === false"
    ))


def wait_processing_done():
    wait.until(lambda d: d.execute_script("""
        return Ext.dom.Query.select('.x-mask-msg').length === 0;
    """))


def open_page():
    driver.get(URL)
    wait.until(lambda d: "Start Center" in d.title)
    wait_ext_ready()
    wait_ajax_done()
    print("✔ Start Center 页面加载完成")


def click_tag(
    driver:webdriver.Remote = driver,
    wait_time:int = 60, 
    locator:str = '',
    tag_title_compare :str = '',       
):
   
    wait = WebDriverWait(driver,wait_time)
    el = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                locator
            )
        )
    )
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", el
    )
    el.click()

    wait.until(lambda d: tag_title_compare in d.title)
    print(f"✔ 进入 {tag_title_compare} 页面")


def switch_to_iframe_and_check_grid():
    iframe = wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.switch_to.frame(iframe)

    wait_ext_ready()
    wait_ajax_done()
    print('已经进入IFRAME')


    grid_count = driver.execute_script(
        "return Ext.ComponentQuery.query('gridpanel').length"
    )
    print("grid count =", grid_count)

    if grid_count == 0:
        raise RuntimeError("❌ 未检测到 ExtJS Grid（iframe 不正确）")

    print("✔ 已进入包含工单列表的 iframe")



WO_NUMBER = "//div[not(div) and contains(., 'Records:')]"
def get_wo_total_number():
    import re

    # 获取el
    el = wait.until(
        EC._element_if_visible((By.XPATH, WO_NUMBER))
    )
    text = el.text  # Selenium
    
    # 使用正则提取 "of" 后的数字
    match = re.search(r'of\s+(\d+)', text)
    if match:
        total_count = int(match.group(1))
        print("Total records:", total_count)  # 输出: 130


def click_end_date_filter_condition(
    driver: webdriver.Remote = driver,
    n: int = 6,
    tag_name: str = "a",  
    timeout: int = 10
) -> bool:
    """
    点击 Ext JS Grid 中第 n 个列筛选按钮（通常为下拉箭头）

    :param driver: WebDriver 实例（如 Chrome(), Firefox()）
    :param n: 第几个筛选按钮（从 1 开始计数）
    :param tag_name: 元素标签名，默认 'div'（Ext JS 6/7 常用 div 模拟按钮）
    :param timeout: 显式等待超时时间（秒）
    :return: 是否成功点击
    """
    
    if n < 1:
        raise ValueError("参数 n 必须为正整数（>=1）")

    xpath = f"(//{tag_name}[contains(@class, 'x-btn-gridfilter')])[{n}]"

    try:
        # step 1 . 点击 弹出筛选按钮   done
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        print(f"✅ 成功定位并点击第 {n} 个筛选按钮")
        element.click()
        
        # Step 2: 等待菜单项出现（最多等 timeout 秒）
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".x-menu-item"))
        )

        # Step 3: 查找并点击 "Less Than or Equals"
        menu_items = driver.find_elements(By.CSS_SELECTOR, ".x-menu-item")
        target_item = None
        for item in menu_items:
            text = item.text.strip()
            if text == "Less Than or Equals":
                target_item = item
                break

        if target_item:
            # 确保可点击（有时需要短暂等待渲染）
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable(target_item))
            target_item.click()
            print("✅ 成功选择 'Less Than or Equals' (≤)")
            return True
        else:
            available = [item.text.strip() for item in menu_items]
            print(f"❌ 未找到 'Less Than or Equals'，可用选项: {available}")
            return False

        return True
    except TimeoutException:
        print(f"❌ 超时：未找到第 {n} 个筛选按钮（XPath: {xpath}）")
        return False
    except Exception as e:
        print(f"⚠️ 点击失败: {type(e).__name__}: {e}")
        return False

# 不好使
def trigger_date_picker_and_select_date(
    driver: webdriver.Remote = driver,
    n: int = 2,
    timeout: int = 10
):
    """
    点击 Ext JS Grid 中第 n 个日期选择器（通常为日历图标）

    :param driver: WebDriver 实例（如 Chrome(), Firefox()）
    :param n: 第几个筛选按钮（从 1 开始计数）
    :param timeout: 显式等待超时时间（秒）
    :return: 是否成功点击
    """
    if n < 1:
        raise ValueError("参数 n 必须为正整数（>=1）")

    
    xpath = f"(//div[contains(@class, 'x-form-date-trigger-gridfilter')])[{n}]"

    try:
        # step 1 . 点击日历图标   done
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        print(f"✅ 成功定位并点击第 {n} 个日历按钮")
        element.click()
        # Step 2: 等待日历弹出并点击“今天”（最多等 timeout 秒）
        WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, "x-datepicker"))
        )
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
        print("✅ 已通过 Enter 键设置日期为今天")
        # 可选：等待日历关闭
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "x-date-picker"))
        )
        print("🎉 日期已成功设置为今天！")
        return True
        
    except TimeoutException:
        print("❌ 超时：未找到相关元素")
        return False
    except Exception as e:
        print(f"⚠️ 点击失败: {type(e).__name__}: {e}")
        return False

def input_end_date(
        driver: webdriver.Remote = driver,
):
    # 直接通过 name 属性定位（唯一且稳定）
    el_name = "ff_schedenddate"
    input_el = driver.find_element(By.NAME, el_name)

    # 设置今天
    today = datetime.now().strftime("%Y-%m-%d")
    input_el.clear()
    input_el.send_keys(today)

    # 触发 change 事件（必须！）
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", input_el)

    print(f"✅ 日期已设为: {today}")

def input_assigned_person_name(
    driver: webdriver.Remote = driver,
    name: str = '', 
    timeout: int = 10
):
    # 如果name == '',直接返回
    if name == '':
        print("✅ 分配人员不做筛选")
        return
    el_name = 'ff_assignedto'
    try:
        # Step 1: 等待输入框存在并可见
        input_el = WebDriverWait(driver, timeout).until(
            # EC.visibility_of_element_located((By.NAME, el_name))
            # EC.presence_of_element_located
            EC.presence_of_element_located((By.NAME, el_name))
        )
        print(f"👁️  已定位到分配人员输入框 ({el_name})")

        # Step 2: 滚动到元素位置（确保在视口内，避免被 header 遮挡）
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_el)

        # Step 3: （可选）聚焦元素，模拟用户行为
        ActionChains(driver).move_to_element(input_el).click().perform()

        # Step 4: 清空并输入
        input_el.clear()
        input_el.send_keys(name)

        # Step 5: 触发 change 事件（Ext JS 必需）
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", input_el)

        print(f"✅ 分配人员已设为: {name}")

    except Exception as e:
        print(f"❌ 设置分配人员失败: {e}")


def click_run_button(
    driver: webdriver.Remote = driver,        
):
    run_button = WebDriverWait(driver, 10).until(
    # EC.element_to_be_clickable((By.XPATH, "//button[.//text()='Run'] | //a[.//text()='Run']"))
    EC.element_to_be_clickable((By.XPATH, "//span[text()='Run' and contains(@class, 'x-btn-inner')]"))
    )
    run_button.click()
    wait_ext_ready()
    wait_ajax_done()
    print("✅ 已经点击RUN按钮")


def get_work_orders(
    driver: webdriver.Remote = driver,
) -> list[WebElement]: 

    # 定位 Grid 的主容器（通过 class 而非 ID）
    grid_view = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.x-grid-view"))
    )

    # 在其内部查找所有数据行 table（不依赖具体 ID 数字）
    work_order_tables = grid_view.find_elements(
        By.XPATH,
        ".//table[starts-with(@id, 'tableview-') and contains(@id, '-record-')]"
    )
    return work_order_tables


def double_click_target_WO(
    driver: webdriver.Remote = driver,
    target_table:WebElement = None,   
):
    # 假设 target_table 是你选中的那个 <table> 元素
    if target_table is not None:
        # print(target_table)
        ActionChains(driver).double_click(target_table).perform()
        wait_ext_ready()
        wait_ajax_done()
        print('双击工单执行')

def get_work_order_item_information(
    driver:webdriver.Remote = driver,
    locator:str = ''    
) -> str | None:
    
    # 定位输入框（不依赖 ID 中的数字）
    el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, locator))
    )

    # 获取当前显示的文本（即 value）
    current_value = el.get_attribute("value")
    print("元素的值为:", current_value)  # 输出: 2026-01-15
    return current_value

def input_work_order_detail(
    driver:webdriver.Remote = driver,
    by:By = By.XPATH,
    locator: str = '',
    text:str = ''
):

    # 通过 locator 定位
    el = driver.find_element(by=by,value=locator)

    # 设置今天
    
    el.clear()
    el.send_keys(text)

    # 触发 change 事件（必须！）
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", el)

    print("✅已经录入信息 ")

WORK_ORDER_TAG = "//span[normalize-space(.)='Work Orders' and not (./span)]"
grid_filter = "//a[contains(@class, 'x-btn-gridfilter')]"              # 筛选按钮列表
grid_filter_end_date = "(//a[contains(@class, 'x-btn-gridfilter')])[6]"     # 筛选按钮列表的第6个为结束日期的筛选
date_triggers = 'div.x-form-date-trigger-gridfilter'                   # 日期图标，包含Schd.Start Date & Schd.End Date 2个                  
DATE_TRIGGER_END_DATE = "(//div[contains(@class, 'x-form-date-trigger-gridfilter')])[2]"
VALUE_LOCATOR_LIST = [
    "//input[@name='schedstartdate' and @type='text']",
    "//input[@name='schedenddate' and @type='text']",
    "//input[@name='assignedto' and @type='text']",
    ]
BOOK_LABOR_TAG = "//span[contains(@class, 'x-tab-inner') and text()='Book Labor']"

EMPLOYEE = "//input[@name='employee' and @type='text' and @role='textbox']"
HOURS_WORKED = "//input[@name='hrswork' and @type='text']"
DATE_WORKED = "//input[@name='datework' and @role='combobox']"
if __name__ == "__main__":
    open_page()  # 打开页面
    click_tag(locator=WORK_ORDER_TAG,tag_title_compare='Work Order') # work orders 点击
    switch_to_iframe_and_check_grid()  #工单列表呈现
    # get_wo_total_number()            #显示工单总数
    print("🎉 环境 + iframe + 工单列表全部确认成功")
    click_end_date_filter_condition()  #日期筛选
    # trigger_date_picker_and_select_date() #日期选为今天
    input_end_date() # 日期输入为今天
    # time.sleep(0.5)
    input_assigned_person_name(name='YXL') #人员筛选
    # time.sleep(0.5)
    click_run_button() # 开始筛选

    # section 2
    work_order_list = get_work_orders()
    double_click_target_WO(target_table=work_order_list[0])
    wo_start_date_str = get_work_order_item_information(locator=VALUE_LOCATOR_LIST[0]) # start date
    wo_end_date_str = get_work_order_item_information(locator=VALUE_LOCATOR_LIST[1])   # end date
    wo_assignto_str = get_work_order_item_information(locator=VALUE_LOCATOR_LIST[2])   # name
    click_tag(locator=BOOK_LABOR_TAG,tag_title_compare='Book Labor') # book labor tag 点击
    # Labor Detail fill
    input_work_order_detail(locator=EMPLOYEE,text=wo_assignto_str)
    input_work_order_detail(locator=HOURS_WORKED,text='0.5')
    input_work_order_detail(locator=DATE_WORKED,text=wo_end_date_str)




