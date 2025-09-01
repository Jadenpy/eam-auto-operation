from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException,NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys

import time

import time
import os
from path import ERIC

from path import locators

class ExtJSSeleniumHelper:

    LONG = 30
    MIDDLE = 10
    SHORT = 3
    
    def __init__(self,  headless=False, executable_path = None):
        self.driver = None
        self.headless = headless
        self.executable_path = executable_path
        self.setup_driver()
    
    def setup_driver(self):
        """配置 Edge 浏览器驱动"""
        options = self.get_optimized_options()
        
        if  self.executable_path is None:
            # 使用 WebDriver Manager 自动管理驱动
            service = Service(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=options)
        else:
            # 验证路径是否存在
            if not os.path.exists(self.executable_path):
                print(f"错误: 驱动文件不存在于 {self.executable_path}")
                print("请确保路径正确且文件存在")
                return None
            # 使用本地的驱动文件
            service = Service(executable_path=self.executable_path)  # 如果 msedgedriver 在 PATH 中，无需指定路径
            self.driver = webdriver.Edge(service=service, options=options)

        # 设置超时时间（针对国外服务器，设置较长超时）
        self.driver.set_page_load_timeout(300)  # 5分钟
        self.driver.set_script_timeout(300)
        # 慢速网络优化
        self.optimize_for_slow_connection()
        # 隐藏自动化特征
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def get_optimized_options(self):
        """option 优化"""
        options = Options()
        
        # 基本配置
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--log-level=3")  # 设置日志级别
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", True)  # 关键，设置浏览器关闭时不退出
        
        # 性能优化
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--disable-gpu')
        
        # 网络优化
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        
        # 禁用图片和CSS加载以加快速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.javascript": 1,  # 允许JS（ExtJS需要）
            "profile.managed_default_content_settings.flash": 2,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.notifications": 2,
        }
        options.add_experimental_option("prefs", prefs)
        
        # 无头模式（可选）
        if self.headless:
            options.add_argument('--headless=new')
        
        return options
    def openURL(self,url):
        self.driver.get(url)   
    # 关闭浏览器
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

    # 针对国外服务器的额外优化
    def optimize_for_slow_connection(self):
        """针对慢速连接的优化设置"""
        # 增加所有超时时间
        self.driver.set_page_load_timeout(600)  # 10分钟
        self.driver.set_script_timeout(600)
        
        # 启用网络缓存
        self.driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': False})
        
        print("已针对慢速连接进行优化")

  



    def _wait(self, overtime = SHORT ):
        return WebDriverWait(self.driver,overtime)

    def _is_element_exist(self,value,by=By.XPATH) -> WebElement:
        try:
            return self.driver.find_element(by,value)
        except NoSuchElementException:
            return False 
        

    def _getting_element_into_view(self, elem:WebElement):
        self.driver.execute_script("""
            arguments[0].scrollIntoView({
                block: 'center',  // 垂直居中
                inline: 'nearest',// 水平最近
                behavior: 'smooth'// 平滑滚动（避免滚动过快导致的元素状态不稳定）
            });
        """, elem)

    def _is_element_blocked(self,elem):
        
        is_not_blocked = self.driver.execute_script("""
            var elem = arguments[0];
            var rect = elem.getBoundingClientRect();
            var centerX = rect.left + rect.width/2;
            var centerY = rect.top + rect.height/2;
            var topElem = document.elementFromPoint(centerX, centerY);
            // 遮挡会导致文本渲染不完整，需确保顶层元素是当前元素或其后代
            return elem.contains(topElem);
        """, elem)
        if not is_not_blocked:
            return False

    def _element_ensure_clickable(self, value, by=By.XPATH):
        """内部条件函数：校验元素是否满足所有可点击条件"""
        # ---------------------- 1. 校验1：元素存在于DOM中（避免NoSuchElementException） ----------------------
        
        elem = self._is_element_exist(value)
        

        # ---------------------- 2. 校验2：元素未被禁用（排除disabled属性和禁用类） ----------------------
        # 场景1：原生disabled属性（如<button disabled>、<input disabled>）
        if elem.get_attribute("disabled") in ("true", "disabled", True):
            return False
        # 场景2：自定义禁用类（如class="disabled"、class="btn-disabled"，需根据项目调整类名）
        disabled_classes = ["disabled", "btn-disabled", "is-disabled"]  # 常见禁用类，可扩展
        elem_classes = elem.get_attribute("class") or ""
        if any(cls in elem_classes for cls in disabled_classes):
            return False

        # ---------------------- 3. 校验3：元素在视图内（不可见则自动滚动） ----------------------
        # 用JS将元素滚动到视图中心（避免“元素存在但在屏幕外”导致的点击失败）
        self.driver.execute_script("""
            arguments[0].scrollIntoView({
                block: 'center',  // 垂直居中
                inline: 'nearest',// 水平最近
                behavior: 'smooth'// 平滑滚动（避免滚动过快导致的元素状态不稳定）
            });
        """, elem)
        # 校验元素是否在视口内（避免滚动后仍未完全显示）
        is_in_viewport = self.driver.execute_script("""
            var rect = arguments[0].getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        """, elem)
        if not is_in_viewport:
            return False

        # ---------------------- 4. 校验4：元素完全可见（排除隐藏样式） ----------------------
        # is_displayed()是Selenium原生方法，能识别display: none、visibility: hidden等隐藏逻辑
        if not elem.is_displayed():
            return False

        # ---------------------- 5. 校验5：无遮挡元素（排除浮层、遮罩等干扰） ----------------------
        # 用JS获取元素中心点的“顶层元素”，判断是否为当前元素或其后代（避免被其他元素覆盖）
        is_not_blocked = self.driver.execute_script("""
            var elem = arguments[0];
            var rect = elem.getBoundingClientRect();
            // 元素中心点坐标
            var centerX = rect.left + rect.width / 2;
            var centerY = rect.top + rect.height / 2;
            // 获取中心点的顶层元素
            var topElem = document.elementFromPoint(centerX, centerY);
            // 若顶层元素是当前元素或其后代，则无遮挡
            return elem.contains(topElem);
        """, elem)
        if not is_not_blocked:
            return False

        # ---------------------- 6. 校验6：元素可交互（确保是浏览器认可的可点击元素） ----------------------
        # 检查元素是否有“可点击”的CSS特征（如cursor: pointer），或本身是可点击标签（button/a/input[type=button]）
        clickable_tag = elem.tag_name.lower() in ("button", "a", "input")
        if clickable_tag and elem.get_attribute("type") in ("button", "submit", "reset"):
            pass  # 原生可点击标签，直接通过
        else:
            # 非原生标签，检查cursor样式（避免div等非可点击标签误判）
            cursor_style = self.driver.execute_script("""
                return window.getComputedStyle(arguments[0]).getPropertyValue('cursor');
            """, elem)
            if cursor_style != "pointer":
                return False

        # 所有条件满足，返回元素实例
        return elem

    def _element_ensure_readable(self, value, by=By.XPATH) -> str:
        """
        确保元素可读取文本，返回非空、可识别的文本内容
        校验逻辑：元素存在→可见→无遮挡→文本非空→文本可识别（排除乱码/占位符）
        :param value: 定位值（如XPath表达式、ID值）
        :param by: 定位方式（默认By.XPATH）
        :return: 元素的非空文本内容
        :raises TimeoutException: 超时未满足可读取条件
        """
        # ---------------------- 1. 校验1：元素存在于DOM中（避免NoSuchElementException） ----------------------
        elem = self._is_element_exist(value)

        # ---------------------- 2. 校验2：元素完全可见（隐藏元素文本可能读取为空） ----------------------

        self._getting_element_into_view(elem)

        # ---------------------- 3. 校验3：无遮挡（避免遮挡导致文本渲染不完整） ----------------------
        self._is_element_blocked(elem)

        # ---------------------- 4. 校验4：文本非空且可识别（排除空文本/乱码/占位符） ----------------------
        # 获取元素文本（优先用text，若为空则尝试获取innerText（兼容部分框架））
        elem_text = elem.text.strip() or elem.get_attribute("innerText").strip()
        # 排除“空文本”“占位符文本”“乱码”（可根据项目调整排除规则）
        invalid_text_patterns = ["", "请输入", "加载中...", "暂无数据", "????", "###"]
        if elem_text in invalid_text_patterns:
            return False

        # ---------------------- 5. 校验5：文本稳定（避免动态渲染中的临时文本） ----------------------
        # 两次读取文本，确保内容一致（排除“正在渲染中”的动态文本）
        elem_text_second = elem.text.strip() or elem.get_attribute("innerText").strip()
        if elem_text != elem_text_second:
            return False

        # 所有条件满足，返回非空可识别的文本
        return elem_text
    
    def _element_ensure_writable(self, value, by=By.XPATH, input_text: str = None, enter = False) -> bool:
        """
        确保元素可写入内容（如输入框），并验证写入内容生效
        校验逻辑：元素存在→是可输入类型→非禁用→非只读→可见→可聚焦→写入内容匹配
        :param value: 定位值（如XPath表达式、ID值）
        :param by: 定位方式（默认By.XPATH）
        :param input_text: 待写入的文本（若为None，仅校验“可写入状态”，不实际写入）
        :return: True（可写入且内容生效）/ False（未满足条件）
        :raises TimeoutException: 超时未满足可写入条件
        """
        # ---------------------- 1. 校验1：元素存在于DOM中 ----------------------
        elem = self._is_element_exist(value)
        # ---------------------- 2. 校验2：元素是“可输入类型”（排除非输入元素） ----------------------
        valid_input_tags = ["input", "textarea"]  # 支持的可输入标签
        tag_name = elem.tag_name.lower()
        if tag_name not in valid_input_tags:
            # 特殊场景：ExtJS/Vue的自定义输入框（可能用div模拟，需有contenteditable属性）
            if elem.get_attribute("contenteditable") != "true":
                return False  # 非可输入元素，返回False

        # ---------------------- 3. 校验3：非禁用、非只读（核心可写入前提） ----------------------
        # 排除禁用状态（disabled属性或禁用类）
        if elem.get_attribute("disabled") in ("true", "disabled", True):
            return False
        disabled_classes = ["disabled", "input-disabled", "is-disabled"]
        if any(cls in (elem.get_attribute("class") or "") for cls in disabled_classes):
            return False
        # 排除只读状态（readonly属性）
        if elem.get_attribute("readonly") in ("true", "readonly", True):
            return False

        # ---------------------- 4. 校验4：元素可见且在视图内（避免聚焦失败） ----------------------
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", elem)
        if not elem.is_displayed():
            return False

        # ---------------------- 5. 校验5：元素可聚焦（输入框需能获取焦点才能写入） ----------------------
        # 用JS尝试聚焦元素，并验证是否成功聚焦
        is_focused = self.driver.execute_script("""
            arguments[0].focus();  // 主动聚焦
            return document.activeElement === arguments[0];  // 验证当前焦点是否为该元素
        """, elem)
        if not is_focused:
            return False  # 无法聚焦，写入会失败

        # ---------------------- 6. 校验6：写入内容并验证生效（若传入input_text） ----------------------
        if input_text is not None:
            # 清空原有内容（避免叠加写入）
            elem.clear()
            # 写入新内容（用send_keys模拟真实输入，适配输入法/自动补全）
            elem.send_keys(input_text)
            if enter:
                elem.send_keys(Keys.ENTER)
            # 验证写入内容是否生效（不同元素获取内容的方式不同）
            if tag_name == "input":
                # input元素用value属性获取内容
                written_text = elem.get_attribute("value").strip()
            elif tag_name == "textarea":
                # textarea元素用text或value获取内容
                written_text = elem.text.strip() or elem.get_attribute("value").strip()
            else:
                # 自定义可编辑元素（contenteditable）用innerText获取内容
                written_text = elem.get_attribute("innerText").strip()
            # 验证写入内容与预期一致（允许前后空格差异，可根据需求调整）
            if written_text != input_text.strip():
                return False

        # 所有条件满足（可写入且内容生效）
        return True


    def element_click(self,locator,overtime =10, by=By.XPATH):
        """
        自定义条件函数：定位元素，若不可见则滚动到可见，并执行点击
        :param self: 实例自身
        :param locator: 元素定位器value
        :return: None
        """
        try:
            # 1. 定位元素（存在于DOM中）
            wait = self._wait()
            elem = wait.until(lambda x:self._element_ensure_clickable(locator))
           
            # 2. 检查元素是否可见
            if elem:
                elem.click()
        except:
            # 元素暂未找到：返回False（继续等待）
            raise


