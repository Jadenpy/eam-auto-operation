import time
import random
import traceback
import csv
import logging
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import yaml
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# ========= 日志配置 =========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("eam.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)


class SeleniumHelper:
    """通用 Selenium 操作类"""

    def __init__(self, driver_path=None):
        self.driver = self._create_driver(driver_path)

    def _create_driver(self, driver_path):
        """
        创建 WebDriver 实例
        :param 
        driver_path: WebDriver 可执行文件路径
        :return: WebDriver 实例
        """
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--log-level=3")
        options.add_experimental_option("detach", True)
        if driver_path:
            service = Service(executable_path=driver_path)
        # 使用 WebDriver Manager 自动管理驱动
        else:
            service = Service(EdgeChromiumDriverManager(url='https://registry.npmmirror.com/-/binary/edgedriver/').install())
        driver = webdriver.Edge(service=service, options=options)
        driver.set_page_load_timeout(300)
        driver.set_script_timeout(300)
        return driver

    def open_url(self, url):
        """
        打开网页
        :param url: 网页地址
        """
        self.driver.get(url)

    def auto_retry(self, func, retries=3, wait=2):
        """
        自动重试
        :param 
        func: 需要重试的函数
        retries: 重试次数
        wait: 重试间隔时间
        """
        for attempt in range(1, retries + 1):
            try:
                return func()
            except Exception as e:
                logging.warning(f"尝试 {attempt} 失败: {e}")
                if attempt < retries:
                    time.sleep(wait)
                else:
                    raise

    def operate_element(self, by, value, action, input_text=None,
                        timeout=20, tag_comment=None, if_scroll=True,
                        retries=3, wait_float=1.5):
        """
            操作元素
        :param by: 定位方式
        :param value: 定位值
        :param action: 操作方式
        :param input_text: 输入文本
        :param timeout: 超时时间
        :param tag_comment: 标签注释
        :param if_scroll: 是否滚动
        :param retries: 重试次数
        :param wait_float: 等待浮层消失时间
        """
        def wait_for_floats():
            """
                等待浮层消失
            """
            try:
                WebDriverWait(self.driver, wait_float).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "x-autocontainer-innerCt"))
                )
            except TimeoutException:
                pass

        wait = WebDriverWait(self.driver, timeout)
        element = wait.until(EC.presence_of_element_located((by, value)))
        if if_scroll:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        element = wait.until(EC.element_to_be_clickable((by, value)))

        if action in ['click', 'right_click']:
            for attempt in range(retries):
                try:
                    wait_for_floats()
                    if action == 'click':
                        element.click()
                    else:
                        ActionChains(self.driver).context_click(element).perform()
                    break
                except ElementClickInterceptedException:
                    logging.warning(f"第 {attempt+1} 次点击被挡住，重试")
                    element = self.driver.find_element(by, value)
            else:
                raise ElementClickInterceptedException(f"点击失败: {value}")

        elif action == 'send_keys':
            element.click()
            element.send_keys(Keys.CONTROL, 'a', Keys.DELETE, input_text)

        elif action == 'send_keys_and_enter':
            element.click()
            element.send_keys(Keys.CONTROL, 'a', Keys.DELETE, input_text, Keys.ENTER)

        elif action.startswith("get_attribute:"):
            attr = action.split(":", 1)[1]
            return element.get_attribute(attr)

        elif action == 'get_text':
            return element.text

        elif action == 'get_element':
            return element

        else:
            logging.error(f"未知操作: {action}")

    def handle_new_tab(self, expected_tabs=2, timeout=30):
        WebDriverWait(self.driver, timeout).until(EC.number_of_windows_to_be(expected_tabs))
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def switch_to_iframe(self, iframe_by, iframe_value, timeout=30):
        try:
            iframe = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((iframe_by, iframe_value)))
            self.driver.switch_to.frame(iframe)
            return True
        except Exception:
            self.driver.switch_to.default_content()
            return False

class Config:
    """配置管理"""
    def __init__(self, config_file="config.yaml"):
        with open(config_file, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    def get(self, key, default=None):
        return self.data.get(key, default)


class EAMAutomation(SeleniumHelper):
    """EAM 工单自动化"""

    locators = {
        "table": '//*[@id="tableview-1103"]/div[3]//table[starts-with(@id, "tableview-1103-record-")]',
        "record_view": '//*[@id="tab-1163-btnInnerEl"]',
        "book_labor": '//*[@id="tab-1166-btnInnerEl"]',
        "record_save": '//*[@id="button-1033-btnIconEl"]',
        "submit": "(//*[starts-with(@id, 'button-') and substring(@id, string-length(@id) - string-length('-btnIconEl') +1) = '-btnIconEl'])[38]",
        "start_date": '//*[@id="uxdate-1412-inputEl"]',
        "end_date": '//*[@id="uxdate-1413-inputEl"]',
        "assigned_to": '//*[@id="lovfield-1414-inputEl"]',
        "status": '//*[@id="uxcombobox-1415-inputEl"]',
        "estimated_hours": '//*[@id="uxnumber-1425-inputEl"]',
        "panel": "(//*[starts-with(@id, 'panel-') and substring(@id, string-length(@id) - string-length('-bodyWrap') +1) = '-bodyWrap'])[19]",
        "employee": './/input[contains(@id, "lovmultiselectfield")]',
        "hours_worked": './/input[contains(@id, "uxnumber")]',
        "date_worked": './/input[contains(@id, "uxdate")]',
        "activity": "(//input[starts-with(@id, 'uxcombobox-') and substring(@id, string-length(@id)-6)='inputEl'])[9]",
    }

    def __init__(self, driver_path, result_file="eam_results.csv"):
        super().__init__(driver_path)
        self.result_file = result_file
        with open(self.result_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["工单编号", "开始日期", "结束日期", "人员", "状态", "结果"])
            writer.writeheader()
    def __init__(self, config: Config):
        self.config = config
        super().__init__(driver_path=config.get("driver_path"))
        self.result_file = config.get("result_file")

    def random_weekday(self, start_date, end_date, exclude=None):
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        exclude = set(exclude or [])
        candidates = []
        curr = start
        while curr <= end:
            date_str = curr.strftime("%Y-%m-%d")
            if date_str not in exclude and curr.weekday() < 5:
                candidates.append(date_str)
            curr += timedelta(days=1)
        return random.choice(candidates) if candidates else None

    def save_result(self, order_id, start_date, end_date, assigned_to, status, result):
        with open(self.result_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["工单编号", "开始日期", "结束日期", "人员", "状态", "结果"])
            writer.writerow({
                "工单编号": order_id,
                "开始日期": start_date,
                "结束日期": end_date,
                "人员": assigned_to,
                "状态": status,
                "结果": result
            })

    def fill_order_form(self, parent, assigned_to, estimated_hours, start_date, end_date, exclude=None):
        """填写表单"""
        exclude = exclude or []
        # 活动
        act = parent.find_element(By.XPATH, self.locators["activity"])
        if not act.get_attribute("value").strip():
            act.send_keys("10 - DEFAULT / ALL TRADES")

        # 员工
        emp = parent.find_element(By.XPATH, self.locators["employee"])
        emp.send_keys(Keys.CONTROL, "a", Keys.DELETE, assigned_to)

        # 工时
        hrs = parent.find_element(By.XPATH, self.locators["hours_worked"])
        hrs.send_keys(Keys.CONTROL, "a", Keys.DELETE, estimated_hours)

        # 日期
        worked_date = self.random_weekday(start_date, end_date, exclude)
        dt = parent.find_element(By.XPATH, self.locators["date_worked"])
        dt.send_keys(Keys.CONTROL, "a", Keys.DELETE, worked_date)

        return worked_date

    def submit_with_retry(self, parent, assigned_to, estimated_hours, start_date, end_date):
        exclude = []
        for attempt in range(5):
            worked_date = self.fill_order_form(parent, assigned_to, estimated_hours, start_date, end_date, exclude)
            exclude.append(worked_date)
            self.operate_element(By.XPATH, self.locators["submit"], "click")
            time.sleep(1)

            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//div[starts-with(@id, 'eammsgbox-')]"))
                )
                logging.warning(f"日期 {worked_date} 冲突，重试")
                ok_btn = self.driver.find_element(By.XPATH, ".//*[starts-with(@id, 'button-') and contains(@id, '-btnInnerEl')]")
                ok_btn.click()
            except TimeoutException:
                logging.info(f"日期 {worked_date} 提交成功")
                return True
        return False

    def process_orders(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, self.locators["table"])))
        tables = self.driver.find_elements(By.XPATH, self.locators["table"])
        logging.info(f"找到 {len(tables)} 个工单")

        for idx, table in enumerate(tables, 1):
            try:
                logging.info(f"➡️ 处理工单 {idx}")
                ActionChains(self.driver).double_click(table).perform()

                # 基本信息
                self.operate_element(By.XPATH, self.locators["record_view"], "click")
                start_date = self.operate_element(By.XPATH, self.locators["start_date"], "get_attribute:value")
                end_date = self.operate_element(By.XPATH, self.locators["end_date"], "get_attribute:value")
                assigned_to = self.operate_element(By.XPATH, self.locators["assigned_to"], "get_attribute:value")
                estimated_hours = self.operate_element(By.XPATH, self.locators["estimated_hours"], "get_attribute:value")

                # Book Labor
                self.operate_element(By.XPATH, self.locators["book_labor"], "click")
                parent = self.driver.find_element(By.XPATH, self.locators["panel"])

                if not self.submit_with_retry(parent, assigned_to, estimated_hours, start_date, end_date):
                    raise Exception("多次提交失败")

                # 保存并修改状态
                self.operate_element(By.XPATH, self.locators["record_save"], "click")
                self.operate_element(By.XPATH, self.locators["status"], "send_keys", input_text="Completed")
                self.operate_element(By.XPATH, self.locators["record_save"], "click")

                self.save_result(f"工单{idx}", start_date, end_date, assigned_to, "Completed", "成功")
                logging.info(f"✅ 工单 {idx} 完成")

            except Exception as e:
                logging.error(f"❌ 工单 {idx} 失败: {e}")
                self.save_result(f"工单{idx}", "-", "-", "-", "-", "失败")

    def run(self):
        try:
            self.open_url("https://myeric.textron.com/")
            self.auto_retry(lambda: self.operate_element(By.XPATH, '//*[@id="MyTools"]/div/ul/li[7]/a', 'click'))
            self.handle_new_tab()
            self.auto_retry(lambda: self.operate_element(By.XPATH, '//*[@id="tab-1052"]', 'click'))
            self.switch_to_iframe(By.ID, "uxtabiframe-1040-iframeEl")
            self.process_orders()
        except Exception as e:
            logging.error(f"EAM 自动化失败: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    # cfg = Config("config.yaml")
    # bot = EAMAutomation(cfg)
    # bot.run()
    
    baidu = SeleniumHelper()
    baidu.open_url('www.baidu.com')
