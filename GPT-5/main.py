
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from datetime import datetime, timedelta
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Optional
import time
import random

URL = 'https://eu1.eam.hxgnsmartcloud.com/web/base/logindisp?tenant=KAUTEX_PRD'

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option('detach',True)  #不自动关闭浏览器
# service = Service(executable_path=r'C:\baiduDownload\msedgedriver.exe')

# driver = webdriver.Edge(service=service, options=options)
driver = webdriver.Edge(options=options)
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

def select_option(
    driver: webdriver.Remote = driver,
    timeout: int = 10,   
    by:By = By.XPATH,
    locator:str = '',
    condition:str = 'Less Than or Equals'
    
) -> bool:
    """
    点击 Ext JS Grid 中第 n 个列筛选按钮（通常为下拉箭头）

    :param driver: WebDriver 实例（如 Chrome(), Firefox()）
    :param n: 第几个筛选按钮（从 1 开始计数）
    :param tag_name: 元素标签名，默认 'div'（Ext JS 6/7 常用 div 模拟按钮）
    :param timeout: 显式等待超时时间（秒）
    :return: 是否成功点击
    """
 
    try:
        # step 1 . 点击 弹出筛选按钮   done
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by,locator))
        )
        print("✅ 成功定位并点击个筛选按钮")
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
            if text == condition:
                target_item = item
                break

        if target_item:
            # 确保可点击（有时需要短暂等待渲染）
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable(target_item))
            target_item.click()
            print(f"✅ 成功选择 {condition}")
            return True
        else:
            available = [item.text.strip() for item in menu_items]
            print(f"❌ 未找到 {condition}，可用选项: {available}")
            return False

        # return True
    except TimeoutException:
        print("❌ 超时：未找到筛选按钮")
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
            EC.presence_of_element_located((By.NAME, el_name))
        )
        print("👁️  已定位到分配人员输入框")

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

def click_button(
    driver: webdriver.Remote = driver,
    by:By = By.XPATH,
    locator : str =  '' ,

):
    el = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((by, locator))
    )
    el.click()
    wait_ext_ready()
    wait_ajax_done()
    print("✅ 已经点击按钮")

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

def get_an_element(
    objct: webdriver.Remote | WebElement = driver,  
    by: By = By.XPATH,
    locator:str = '',
    timeout:int = 10
    ) -> WebElement | None: 
    try:
        return WebDriverWait(objct, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
    except (TimeoutException, NoSuchElementException) as e:
        msg = f"❌ 元素未在 {timeout} 秒内出现: ({by}, {locator})"
        return None

    except Exception as e:
        # 捕获其他异常（如 StaleElementReferenceException）
        msg = f"⚠️ 定位元素时发生意外错误: ({by}, {locator}) - {str(e)}"
        print(msg)
        return None

def double_click_elment(
    driver: webdriver.Remote = driver,
    el:WebElement = None,   
):
    # 假设 target_table 是你选中的那个 <table> 元素
    if el is not None:
        # print(target_table)
        ActionChains(driver).double_click(el).perform()
        wait_ext_ready()
        wait_ajax_done()
        # time.sleep(1)
        print('双击元素执行')

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

def input_text(
    driver:webdriver.Remote = driver,
    by:By = By.XPATH,
    locator: str = '',
    text:str = '',
    is_enter:bool = False,
    is_tab:bool = False,
):

    # 通过 locator 定位
    el = driver.find_element(by=by,value=locator)

     # elem.clear()
    el.click()
    el.clear()
    el.send_keys(Keys.CONTROL, 'a')
    el.send_keys(Keys.DELETE)
    # 写入新内容（用send_keys模拟真实输入，适配输入法/自动补全）
    
    el.send_keys(text)
    if is_enter:
        el.send_keys(Keys.ENTER)
    if is_tab:
        el.send_keys(Keys.TAB)

    # 触发 change 事件（必须！）
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", el)

    print(f"✅已经录入信息:{text} ")

def select_combobox_option(
        driver:webdriver.Remote = driver, 
        option_text: str = '', 
        timeout: int = 10):
    """专用于 Ext JS ComboBox"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".x-boundlist"))
        )

        # 3. 查找并点击选项
        options = driver.find_elements(By.CSS_SELECTOR, ".x-boundlist-item")
        for opt in options:
            if opt.text.strip() == option_text:
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(opt))
                opt.click()
                print(f"✅ 已选择: {option_text}")
                return True

        available = [opt.text.strip() for opt in options]
        print(f"❌ 未找到 '{option_text}'，可用选项: {available}")
        return False
        # return True
    except TimeoutException:
        print("❌ 超时：未找到筛选按钮")
        return False
    except Exception as e:
        available = [opt.text.strip() for opt in options]
        print(f"❌ 未找到 '{option_text}'，可用选项: {available}")
        print(f"⚠️ 选择失败: {type(e).__name__}: {e}")
        return False

def safe_click_combobox_trigger(
        driver:webdriver.Remote=driver, 
        by:By = By.XPATH, 
        locator :str = '', 
        timeout=10):
    """
    安全点击 ComboBox trigger，确保下拉弹出
    """

    # Step 1: 等待 loading 消失（关键！）
    time.sleep(0.5)
    try:
        WebDriverWait(driver, 3).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".x-mask-loading"))
        )
    except:
        pass  # 没有 loading 就跳过

    # Step 2: 等待 trigger 可点击
    trigger = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )

    # Step 3: 点击 + 验证是否弹出（带重试）
    max_retries = 3
    for attempt in range(max_retries):
        # 等待遮罩层消失
        wait = WebDriverWait(driver, 10)
        wait.until(EC.invisibility_of_element_located((By.ID, "ext-element-30")))

        # 或者更通用：等待所有 x-mask 遮罩消失
        wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, "x-mask")))
        trigger.click()
        time.sleep(0.3)  # 给 JS 响应时间

        try:
            WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".x-boundlist"))
            )
            print("✅ 下拉面板已成功弹出")
            return True
        except:
            if attempt < max_retries - 1:
                print(f"⚠️ 第 {attempt+1} 次点击未生效，重试...")
                # 重新获取 trigger（防止 stale element）
                trigger = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((by, locator))
                )
            else:
                raise Exception("❌ 多次尝试后下拉仍未弹出")

    return False

def wait_for_save_confirmation(
        driver:webdriver.Remote = driver, 
        timeout: int = 10
        ):
    """
    全局等待页面出现 'successfully saved' 文本（不区分大小写）
    只要出现，就返回 True；超时未出现，返回 False
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: "successfully saved" in d.page_source.lower()
        )
        print("✅ 检测到 'successfully saved'，工单处理完成")
        # 尝试执行 Ext JS 的 close 命令
        driver.execute_script("""
            var msgBox = Ext.ComponentQuery.query('messagebox')[0];
            if (msgBox) {
                msgBox.close();
            }
        """)
        print("✅ 通过 JS 关闭提示框")
        return True
    except TimeoutException:
        print("❌ 超时：未检测到 'successfully saved'")
        return False
    except Exception as e:
        # print(f"⚠️ 意外错误: {e}")
        return False

def get_workday(
    start_date: str,
    end_date: str,
    exclude_dates: Optional[List[str]] = None,
    date_format: str = "%Y-%m-%d"
) -> str:
    """
    在 [start_date, end_date) 范围内随机返回一个日期字符串（不包含 end_date），
    并排除 exclude_dates 中指定的日期。

    参数:
        start_date (str): 起始日期（包含）
        end_date (str): 结束日期（不包含）
        exclude_dates (List[str], optional): 要排除的日期列表（格式同 date_format）
        date_format (str): 日期格式，默认 "%Y-%m-%d"

    返回:
        str: 随机选择的、未被排除的有效日期
    """
    start = datetime.strptime(start_date, date_format).date()
    end = datetime.strptime(end_date, date_format).date()

    # 确保 start <= end
    if start > end:
        start, end = end, start

    # 构建排除集合（转为 date 对象，便于比较）
    exclude_set = set()
    if exclude_dates:
        for d_str in exclude_dates:
            try:
                exclude_set.add(datetime.strptime(d_str, date_format).date())
            except ValueError:
                # 忽略格式错误的排除日期（或可抛出异常）
                continue

    # 生成所有候选日期：[start, end)
    candidates = []
    current = start
    while current < end:
        if current not in exclude_set:
            candidates.append(current)
        current += timedelta(days=1)

    # 如果没有有效候选日期，回退到 start（或可抛异常）
    if not candidates:
        return start.strftime(date_format)

    # 随机选择一个
    selected = random.choice(candidates)
    return selected.strftime(date_format)

def get_hours(value_str: str) -> str:
    """
    处理工时字符串，按规则返回格式化后的字符串：
      - <1: 原样返回（去尾 .0）
      - 1≤x<2: 返回 0.8*x，对齐到 0.5 倍数，去尾 .0
      - ≥2: 在 [x/2, x] 内随机选一个 0.5 倍数，去尾 .0
    
    返回示例: "1", "1.5", "2", "0.8" → "1"
    """
    try:
        x = float(value_str)
    except (ValueError, TypeError):
        raise ValueError(f"无效输入: '{value_str}' 不是有效数字")

    # 将数值对齐到最近的 0.5 倍数
    def round_to_half(num: float) -> float:
        return round(num * 2) / 2

    # 格式化：去掉不必要的 .0
    def format_clean(num: float) -> str:
        if num.is_integer():
            return str(int(num))
        else:
            # 确保只有一位小数（0.5 的倍数最多一位）
            return f"{num:.1f}"

    if x < 1:
        return format_clean(x)

    elif 1 <= x < 2:
        result = round_to_half(0.8 * x)
        return format_clean(result)

    else:  # x >= 2
        low = x / 2
        high = x

        # 生成 [low, high] 范围内所有 0.5 步长的候选值
        start = round_to_half(low)
        end = round_to_half(high)

        candidates = []
        current = start
        while current <= end + 1e-9:  # 避免浮点误差
            candidates.append(current)
            current += 0.5

        if not candidates:
            result = round_to_half(x)
        else:
            result = random.choice(candidates)

        return format_clean(result)

def has_too_many_hours_error(
        driver:webdriver.Remote = driver, 
        timeout:int=2):
    """
    检查是否出现 'Too many Hours' 错误弹窗
    返回 True/False
    """
    try:
        # 等待消息框出现（最多 timeout 秒）
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, TOO_MANY_TIMES_MSG))
        )
        return True
    except TimeoutException:
        return False


WO_NUMBER = "//div[not(div) and contains(., 'Records:')]"
WORK_ORDER_TAG = "//span[normalize-space(.)='Work Orders' and not (./span)]"
grid_filter = "//a[contains(@class, 'x-btn-gridfilter')]"              # 筛选按钮列表
grid_filter_end_date = "(//a[contains(@class, 'x-btn-gridfilter')])[6]"     # 筛选按钮列表的第6个为结束日期的筛选
FILTER_DATE_CONDITION = "(//a[contains(@class, 'x-btn-gridfilter')])[6]"
date_triggers = 'div.x-form-date-trigger-gridfilter'                   # 日期图标，包含Schd.Start Date & Schd.End Date 2个                  
DATE_TRIGGER_END_DATE = "(//div[contains(@class, 'x-form-date-trigger-gridfilter')])[2]"
RUN_BTN = "//span[text()='Run' and contains(@class, 'x-btn-inner')]"
VALUE_LOCATOR_LIST = [
    "//input[@name='schedstartdate' and @type='text']",
    "//input[@name='schedenddate' and @type='text']",
    "//input[@name='assignedto' and @type='text']",
    "//input[@name='workorderstatus' and @role='combobox']",
    ]
WORK_ORDER_STATUS = "//input[@name='workorderstatus' and @role='combobox']"
ESTIMATED_HOURS = "//input[@name='esthrs']"
# WORK_ORDER_STATUS_SELECT = "//input[@name='workorderstatus']/ancestor::div[contains(@class, 'x-form-item')]//div[contains(@class, 'x-form-arrow-trigger')]"
WORK_ORDER_STATUS_SELECT = '//*[@id="uxcombobox-1416-trigger-picker"]'
BOOK_LABOR_TAG = "//span[contains(@class, 'x-tab-inner') and text()='Book Labor']"
RECORD_VIEW_TAG = "//span[contains(@class, 'x-tab-inner') and text()='Record View']"

ACTIVITY = "//input[@name='booactivity']"

EMPLOYEE = "//input[@name='employee' and @type='text' and @role='textbox']"
HOURS_WORKED = "//input[@name='hrswork' and @type='text']"
DATE_WORKED = "//input[@name='datework' and @role='combobox']"

TOO_MANY_TIMES_MSG = "//div[contains(@class, 'x-message-box')]//h6[contains(text(), 'Too many Hours')]"
OK_BTN_ON_MSG = "(//a[contains(@class, 'uft-id-ok') and @role='button'])[2]"
SAVE_LABOR_RECORD = "(//span[contains(@class, 'x-btn-icon-el') and contains(@class, 'toolbarSave')])[2]"
SAVE_WORK_ORDER = "(//span[contains(@class, 'x-btn-icon-el') and contains(@class, 'toolbarSave')])[1]"

SPLITTER_BAR = "//div[@role='separator' and @aria-orientation='vertical' and contains(@class, 'x-splitter') and contains(@class, 'x-splitter-vertical')]"

if __name__ == "__main__":
    open_page()  # 打开页面
    click_tag(locator=WORK_ORDER_TAG,tag_title_compare='Work Order') # work orders 点击
    switch_to_iframe_and_check_grid()  #工单列表呈现
    # get_wo_total_number()            #显示工单总数
    print("🎉 环境 + iframe + 工单列表全部确认成功")
    select_option(locator=FILTER_DATE_CONDITION)  #日期筛选条件
    # trigger_date_picker_and_select_date() #日期选为今天
    input_end_date() # 日期输入为今天
    # time.sleep(0.5)
    # input_assigned_person_name(name='HXSH') #人员筛选
    input_assigned_person_name() #人员筛选
    # time.sleep(0.5)
    click_button(locator=RUN_BTN) # 开始筛选

    # section 2
    work_order_list = get_work_orders()
    for i, wo in enumerate(work_order_list):
        print(f"🔧 正在处理第 {i+1} 个工单...")
        double_click_elment(el=work_order_list[i])
        wo_start_date_str = get_work_order_item_information(locator=VALUE_LOCATOR_LIST[0]) # start date
        wo_end_date_str = get_work_order_item_information(locator=VALUE_LOCATOR_LIST[1])   # end date
        wo_assignto_str = get_work_order_item_information(locator=VALUE_LOCATOR_LIST[2])   # name
        wo_estimated_hours_str = get_work_order_item_information(locator=ESTIMATED_HOURS)   # work hours
        if '' in (wo_estimated_hours_str, wo_assignto_str):
            # go to 
            splitter_bar = get_an_element(locator=SPLITTER_BAR)
            double_click_elment(el=splitter_bar)
            print(f"✅ 第 {i+1} 个工单处理中断，初始工时或者分配人员为空\n")
            continue  
        # else:
        act_workday = get_workday(wo_start_date_str,wo_end_date_str)
        act_workhours = get_hours(wo_estimated_hours_str)

        click_tag(locator=BOOK_LABOR_TAG,tag_title_compare='Book Labor') # book labor tag 点击
        # is activity filled?
        activity = get_an_element(locator=ACTIVITY).get_attribute("value")
        if activity == '':
            # refill it to '10 - engineer' 
            # go to 
            click_tag(locator=RECORD_VIEW_TAG,tag_title_compare='Record View')
            splitter_bar = get_an_element(locator=SPLITTER_BAR)
            double_click_elment(el=splitter_bar)
            print(f"✅ 第 {i+1} 个工单处理中断，Activity为空\n")
            continue
        # Labor Detail fill
        input_text(locator=EMPLOYEE,text=wo_assignto_str)
        # input_text(locator=HOURS_WORKED,text='0.5')
        input_text(locator=HOURS_WORKED,text=act_workhours)
        # input_text(locator=DATE_WORKED,text=wo_start_date_str)
        input_text(locator=DATE_WORKED,text=act_workday)
        if has_too_many_hours_error():
            print('to many time ,please try again!')
            # click ok btn on msg window
            click_button(locator=OK_BTN_ON_MSG)
            # reInput date
            act_workday = get_workday(wo_start_date_str,wo_end_date_str,[act_workday])
            input_text(locator=DATE_WORKED,text=act_workday)
            print('reInput successful')

        # save record
        click_button(locator=SAVE_LABOR_RECORD)
        # record view page
        click_tag(locator=RECORD_VIEW_TAG,tag_title_compare='Record View')
        # chage work order status   open -->completed
        # input_text(locator=WORK_ORDER_STATUS,text='Completed')
        # click_filter_condition(locator=WORK_ORDER_STATUS,condition='Completed')
        safe_click_combobox_trigger(locator=WORK_ORDER_STATUS_SELECT)
        select_combobox_option(option_text='Completed')
        # save wo
        click_button(locator=SAVE_WORK_ORDER)
        wait_for_save_confirmation()    # feedback information
        splitter_bar = get_an_element(locator=SPLITTER_BAR)
        double_click_elment(el=splitter_bar)
        print(f"✅ 第 {i+1} 个工单处理完成\n")
    print("🎉 所有工单处理完毕！")





