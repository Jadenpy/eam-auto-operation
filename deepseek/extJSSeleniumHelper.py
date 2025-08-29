from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException

import time

import time
import os
from path import ERIC

from path import locators

class ExtJSSeleniumHelper:
    
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
     
    # 关闭浏览器
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
# ---------------debug---------------------------
    # 针对国外服务器的额外优化
    def optimize_for_slow_connection(self):
        """针对慢速连接的优化设置"""
        # 增加所有超时时间
        self.driver.set_page_load_timeout(600)  # 10分钟
        self.driver.set_script_timeout(600)
        
        # 启用网络缓存
        self.driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': False})
        
        print("已针对慢速连接进行优化")

    # 高级调试和错误处理
    def debug_extjs_state(self):
        """调试 ExtJS 应用状态"""
        state = self.driver.execute_script("""
            if (typeof Ext === 'undefined') {
                return {loaded: false, reason: 'ExtJS not loaded'};
            }
            
            // 检查各种 ExtJS 组件的状态
            var components = Ext.ComponentQuery.query('component');
            var unrendered = Ext.ComponentQuery.query('component[rendered=false]');
            
            return {
                loaded: Ext.isReady,
                componentCount: components.length,
                unrenderedCount: unrendered.length,
                unrenderedIds: unrendered.map(function(c) { 
                    return c.id || c.getItemId && c.getItemId() || 'anonymous'; 
                }),
                app: typeof Ext.app && Ext.app.Application ? 'Application exists' : 'No application',
                version: Ext.versions && Ext.versions.extjs ? Ext.versions.extjs.version : 'Unknown'
            };
        """)
        
        print("ExtJS 调试信息:")
        for key, value in state.items():
            print(f"  {key}: {value}")
        
        return state

    def take_debug_screenshot(self, filename="debug_screenshot.png"):
        """截取调试截图"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # 截取屏幕截图
            self.driver.save_screenshot(filename)
            print(f"调试截图已保存到: {filename}")
            return True
        except Exception as e:
            print(f"截取调试截图失败: {e}")
            return False
# -----------------operation---------------------

    def load_extjs_page(self, url, max_retries=3, component_query=None):
        """
        加载 ExtJS 页面，带有重试机制和特殊等待
        component_query: 可选，等待特定的 ExtJS 组件
        """
        for attempt in range(max_retries):
            try:
                print(f"尝试第 {attempt + 1} 次加载页面...")
                
                # 加载页面
                self.driver.get(url)
                
                # 等待 ExtJS 框架就绪
                # self.wait_for_extjs_ready(120)
                
                # 如果指定了组件，等待该组件
                if component_query:
                    self.wait_for_ext_component(component_query, 60)
                
                print("页面加载成功!")
                return True
                
            except TimeoutException as e:
                print(f"第 {attempt + 1} 次尝试超时: {e}")
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)  # 指数退避
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print("达到最大重试次数，放弃加载")
                    return False
            except Exception as e:
                print(f"加载页面时发生异常: {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
                else:
                    return False
        return False
    
    def wait_for_extjs_ready(self, timeout=120):
        """等待 ExtJS 框架完全加载"""
        try:
            # 等待 ExtJS 核心对象可用
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return typeof Ext !== 'undefined'")
            )
            
            # 等待 ExtJS 应用初始化完成
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return Ext.isReady || false")
            )
            
            print("ExtJS 框架已完全加载")
            return True
        except TimeoutException:
            print("等待 ExtJS 加载超时，但继续执行")
            return False
    
    def wait_for_ext_component(self, component_query, timeout=60):
        """等待特定的 ExtJS 组件加载完成"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(f"""
                    if (typeof Ext === 'undefined') return false;
                    var comp = Ext.ComponentQuery.query('{component_query}')[0];
                    return comp && comp.rendered;
                """)
            )
            print(f"ExtJS 组件 '{component_query}' 已加载")
            return True
        except TimeoutException:
            print(f"等待 ExtJS 组件 '{component_query}' 超时")
            return False
    
    def execute_extjs_method(self, component_query, method_name, *args):
        """
        执行 ExtJS 组件的方法
        例如: execute_extjs_method('grid[title="Users"]', 'getStore')
        """
        try:
            # 将参数转换为 JSON 字符串以便在 JavaScript 中使用
            args_json = ", ".join([f"'{arg}'" if isinstance(arg, str) else str(arg) for arg in args])
            
            result = self.driver.execute_script(f"""
                if (typeof Ext === 'undefined') return null;
                var comp = Ext.ComponentQuery.query('{component_query}')[0];
                if (!comp) return null;
                return comp.{method_name}({args_json});
            """)
            
            return result
        except Exception as e:
            print(f"执行 ExtJS 方法失败: {e}")
            return None
    
    def click_and_switch_in_extjs(self, element_locator, locator_type=By.CSS_SELECTOR, timeout=30):
            """
            针对 ExtJS 应用的点击和切换标签页方法
            
            参数:
            - element_locator: 元素定位器
            - locator_type: 定位器类型（默认为 CSS_SELECTOR）
            - timeout: 超时时间（秒）
            
            返回:
            - 新标签页的句柄，如果失败则返回 None
            """
            # 首先等待 ExtJS 框架加载完成
            self.wait_for_extjs_ready(timeout)
            
            # 获取原始窗口句柄
            original_handles = self.driver.window_handles
            
            try:
                # 等待元素可点击（可能需要特殊处理 ExtJS 组件）
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((locator_type, element_locator))
                )
                
                # 点击元素
                element.click()
                print(f"已点击 ExtJS 元素: {element_locator}")
                
                # 等待 ExtJS 可能触发的动画或效果完成
                time.sleep(1)  # 适当等待
                
            except Exception as e:
                print(f"点击 ExtJS 元素失败: {e}")
                return None
            
            # 切换到新标签页
            return self.switch_to_new_tab(original_handles, timeout)

    # 标签操作
    def switch_to_new_tab(self,page_title, timeout=120):
        """
        切换到最新打开的标签页
        
        参数:
        - original_handles: 原始窗口句柄列表，如果不提供则使用当前所有窗口句柄
        - timeout: 等待新标签页打开的超时时间（秒）
        
        返回:
        - 新标签页的句柄，如果失败则返回 None
        """
        # 设置等待
        wait = WebDriverWait(self.driver, timeout)

        # 存储原始窗口的 ID
        original_window = self.driver.current_window_handle

        # # 检查一下，我们还没有打开其他的窗口
        # assert len(self.driver.window_handles) == 1

        # 单击在新窗口中打开的链接
        # self.driver.find_element(By.XPATH, "new window").click()

        # 等待新窗口或标签页
        wait.until(EC.number_of_windows_to_be(2))

        # 循环执行，直到找到一个新的窗口句柄
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break

        # 等待新标签页完成加载内容
        wait.until(EC.title_is(page_title))
        print(f'{page_title}已经切换并载入')
    def switch_to_original_tab(self):
        """
        切换回原始标签页
        return: True if successful, False otherwise
        """
        if self.original_tab and self.original_tab in self.driver.window_handles:
            try:
                self.driver.switch_to.window(self.original_tab)
                print("已切换回原始标签页")
                return True
            except NoSuchWindowException:
                print("原始标签页已关闭")
                return False
        return False
    
    def close_current_tab_and_switch_back(self):
        """
        关闭当前标签页并切换回原始标签页
        return: True if successful, False otherwise
        """
        if len(self.driver.window_handles) <= 1:
            print("只有一个标签页，无法关闭")
            return False
        
        current_handle = self.driver.current_window_handle
        self.driver.close()
        
        # 如果关闭的是原始标签页，需要更新原始标签页引用
        if current_handle == self.original_tab:
            self.original_tab = None
        
        return self.switch_to_original_tab()

    # frame操作
    def switch_to_iframe(self, frame_reference, timeout=30):
        """
        切换到指定的 iframe
        
        参数:
        - frame_reference: 可以是 iframe 的 ID、name、索引或 WebElement 对象
        - timeout: 等待 iframe 可用的超时时间（秒）
        
        返回:
        - 成功返回 True，失败返回 False
        """
        try:
            # 等待 iframe 可用并切换到它
            WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it(frame_reference)
            )
            print(f"已切换到 iframe: {frame_reference}")
            return True
        except TimeoutException:
            print(f"等待 iframe {frame_reference} 超时")
            return False
        except Exception as e:
            print(f"切换到 iframe 失败: {e}")
            return False

    def switch_to_default_content(self):
        """
        切换回默认内容（主文档）
        
        返回:
        - 总是返回 True
        """
        try:
            self.driver.switch_to.default_content()
            print("已切换回默认内容")
            return True
        except Exception as e:
            print(f"切换回默认内容失败: {e}")
            return False

    def switch_to_parent_frame(self):
        """
        切换回父级框架（用于嵌套 iframe 的情况）
        
        返回:
        - 成功返回 True，失败返回 False
        """
        try:
            self.driver.switch_to.parent_frame()
            print("已切换回父级框架")
            return True
        except Exception as e:
            print(f"切换回父级框架失败: {e}")
            return False

    def find_element_in_iframe(self, iframe_reference, element_locator, locator_type=By.CSS_SELECTOR, timeout=30):
        """
        在 iframe 中查找元素
        
        参数:
        - iframe_reference: iframe 的引用（ID、name、索引或 WebElement）
        - element_locator: 要查找的元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        
        返回:
        - 找到的元素对象，如果失败则返回 None
        """
        original_handle = self.driver.current_window_handle
        
        try:
            # 切换到 iframe
            if not self.switch_to_iframe(iframe_reference, timeout):
                return None
            
            # 在 iframe 中查找元素
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((locator_type, element_locator))
            )
            print(f"在 iframe 中找到元素: {element_locator}")
            return element
            
        except TimeoutException:
            print(f"在 iframe 中等待元素 {element_locator} 超时")
            return None
        except Exception as e:
            print(f"在 iframe 中查找元素失败: {e}")
            return None
        finally:
            # 确保切换回默认内容
            self.switch_to_default_content()
            
            # 确保切换回原始窗口（如果有多个窗口）
            if self.driver.current_window_handle != original_handle:
                self.driver.switch_to.window(original_handle)

    def click_element_in_iframe(self, iframe_reference, element_locator, locator_type=By.CSS_SELECTOR, timeout=30):
        """
        在 iframe 中点击元素
        
        参数:
        - iframe_reference: iframe 的引用（ID、name、索引或 WebElement）
        - element_locator: 要点击的元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        
        返回:
        - 成功返回 True，失败返回 False
        """
        element = self.find_element_in_iframe(iframe_reference, element_locator, locator_type, timeout)
        
        if element:
            try:
                element.click()
                print(f"已在 iframe 中点击元素: {element_locator}")
                return True
            except Exception as e:
                print(f"点击 iframe 中的元素失败: {e}")
        
        return False

    def wait_for_iframe_and_switch(self, iframe_locator, locator_type=By.CSS_SELECTOR, timeout=30):
        """
        等待 iframe 可用并切换到它（使用定位器而不是直接引用）
        
        参数:
        - iframe_locator: iframe 元素的定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        
        返回:
        - 成功返回 True，失败返回 False
        """
        try:
            # 等待 iframe 元素存在
            iframe_element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((locator_type, iframe_locator))
            )
            
            # 切换到 iframe
            return self.switch_to_iframe(iframe_element, timeout)
        except TimeoutException:
            print(f"等待 iframe 元素 {iframe_locator} 超时")
            return False
        except Exception as e:
            print(f"等待并切换到 iframe 失败: {e}")
            return False

    def execute_in_iframe(self, iframe_reference, function, *args, **kwargs):
        """
        在 iframe 中执行函数，执行后自动切换回默认内容
        
        参数:
        - iframe_reference: iframe 的引用
        - function: 要在 iframe 中执行的函数
        - args, kwargs: 传递给函数的参数
        
        返回:
        - 函数的返回值，如果失败则返回 None
        """
        original_handle = self.driver.current_window_handle
        
        try:
            # 切换到 iframe
            if not self.switch_to_iframe(iframe_reference):
                return None
            
            # 执行函数
            result = function(*args, **kwargs)
            return result
            
        except Exception as e:
            print(f"在 iframe 中执行函数失败: {e}")
            return None
        finally:
            # 确保切换回默认内容
            self.switch_to_default_content()
            
            # 确保切换回原始窗口（如果有多个窗口）
            if self.driver.current_window_handle != original_handle:
                self.driver.switch_to.window(original_handle)

    # 元素操作
    def find_visible_element(self, locator, locator_type=By.XPATH, timeout=30, poll_frequency=0.5):
        """
        查找可见元素（带等待）
        
        参数:
        - locator: 元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        - poll_frequency: 轮询频率（秒）
        
        返回:
        - 找到的可见元素对象，如果失败则返回 None
        """
        try:
            element = WebDriverWait(
                self.driver, timeout, poll_frequency=poll_frequency
            ).until(
                EC.visibility_of_element_located((locator_type, locator))
            )
            # print(f"找到可见元素: {locator}")
            return element
        except TimeoutException:
            print(f"等待元素可见超时: {locator}")
            return None
        except Exception as e:
            print(f"查找可见元素失败: {locator}, 错误: {e}")
            return None

    def find_clickable_element(self, locator, locator_type=By.XPATH, timeout=30, poll_frequency=0.5):
        """
        查找可点击元素（带等待）
        
        参数:
        - locator: 元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        - poll_frequency: 轮询频率（秒）
        
        返回:
        - 找到的可点击元素对象，如果失败则返回 None
        """
        try:
            element = WebDriverWait(
                self.driver, timeout, poll_frequency=poll_frequency
            ).until(
                EC.element_to_be_clickable((locator_type, locator))
            )
            # print(f"找到可点击元素: {locator}")
            return element
        except TimeoutException:
            print(f"等待元素可点击超时: {locator}")
            return None
        except Exception as e:
            print(f"查找可点击元素失败: {locator}, 错误: {e}")
            return None

    def wait_for_element_visible(self, locator, locator_type=By.XPATH, timeout=30):
        """
        等待元素可见
        
        参数:
        - locator: 元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        
        返回:
        - 成功返回 True，失败返回 False
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((locator_type, locator))
            )
            print(f"元素已可见: {locator}")
            return True
        except TimeoutException:
            print(f"等待元素可见超时: {locator}")
            return False
        except Exception as e:
            print(f"等待元素可见失败: {locator}, 错误: {e}")
            return False

    def wait_for_element_clickable(self, locator, locator_type=By.XPATH, timeout=30):
        """
        等待元素可点击
        
        参数:
        - locator: 元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        
        返回:
        - 成功返回 True，失败返回 False
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((locator_type, locator))
            )
            # print(f"元素已可点击: {locator}")
            return True
        except TimeoutException:
            print(f"等待元素可点击超时: {locator}")
            return False
        except Exception as e:
            print(f"等待元素可点击失败: {locator}, 错误: {e}")
            return False

    def is_element_visible_and_enabled(self, locator, locator_type=By.XPATH, timeout=5):
        """
        检查元素是否可见且启用
        
        参数:
        - locator: 元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        
        返回:
        - 元素可见且启用返回 True，否则返回 False
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((locator_type, locator))
            )
            enabled = element.is_enabled()
            result = enabled and element.is_displayed()
            # print(f"元素可见且启用: {locator}, 结果: {result}")
            return result
        except TimeoutException:
            print(f"元素不可见或未启用: {locator}")
            return False
        except Exception as e:
            print(f"检查元素可见性和启用状态失败: {locator}, 错误: {e}")
            return False

    def safe_click(self, locator, locator_type=By.XPATH, timeout=30, max_attempts=3):
        """
        安全点击元素，带有重试机制和可见性检查
        
        参数:
        - locator: 元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 每次尝试的超时时间（秒）
        - max_attempts: 最大尝试次数
        
        返回:
        - 成功返回 True，失败返回 False
        """
        for attempt in range(max_attempts):
            try:
                # 等待元素可见且可点击
                element = WebDriverWait(self.driver, timeout).until(
                    lambda driver: EC.visibility_of_element_located((locator_type, locator))(driver) and 
                                EC.element_to_be_clickable((locator_type, locator))(driver)
                )
                
                # 滚动到元素
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                
                # 点击元素
                # if self.is_mask_go_away():
                    # element.click()
                self.driver.execute_script("arguments[0].click();", element)
                # print(f"已安全点击元素: {locator} (尝试 {attempt + 1}/{max_attempts})")
                return True
                
            except TimeoutException:
                print(f"等待元素可见且可点击超时: {locator} (尝试 {attempt + 1}/{max_attempts})")
            except Exception as e:
                print(f"安全点击元素失败: {locator}, 错误: {e} (尝试 {attempt + 1}/{max_attempts})")
            
            # 如果不是最后一次尝试，等待一段时间后重试
            if attempt < max_attempts - 1:
                time.sleep(2)  # 等待2秒后重试
        
        print(f"经过 {max_attempts} 次尝试后，安全点击元素失败: {locator}")
        return False

    # def safe_input(self, locator, text, locator_type=By.XPATH, timeout=30, clear_first=True, max_attempts=3):
    #     """
    #     安全输入文本，带有重试机制和可见性检查
        
    #     参数:
    #     - locator: 元素定位器
    #     - text: 要输入的文本
    #     - locator_type: 定位器类型（默认为 CSS_SELECTOR）
    #     - timeout: 每次尝试的超时时间（秒）
    #     - clear_first: 是否先清空输入框
    #     - max_attempts: 最大尝试次数
        
    #     返回:
    #     - 成功返回 True，失败返回 False
    #     """
    #     for attempt in range(max_attempts):
    #         try:
    #             # 等待元素可见且可点击
    #             element = WebDriverWait(self.driver, timeout).until(
    #                 lambda driver: EC.visibility_of_element_located((locator_type, locator))(driver) and 
    #                             EC.element_to_be_clickable((locator_type, locator))(driver)
    #             )
                
    #             # 滚动到元素
    #             self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                
    #             # 清空输入框（如果需要）
    #             if clear_first:
    #                 element.clear()
                
    #             # 输入文本
    #             element.send_keys(text)
    #             print(f"已安全输入文本: {locator}, 文本: {text} (尝试 {attempt + 1}/{max_attempts})")
    #             return True
                
    #         except TimeoutException:
    #             print(f"等待元素可见且可点击超时: {locator} (尝试 {attempt + 1}/{max_attempts})")
    #         except Exception as e:
    #             print(f"安全输入文本失败: {locator}, 错误: {e} (尝试 {attempt + 1}/{max_attempts})")
            
    #         # 如果不是最后一次尝试，等待一段时间后重试
    #         if attempt < max_attempts - 1:
    #             time.sleep(2)  # 等待2秒后重试
        
    #     print(f"经过 {max_attempts} 次尝试后，安全输入文本失败: {locator}")
    #     return False

    def safe_input(self, locator, text, locator_type=By.XPATH, timeout=30, 
                clear_first=True, max_attempts=3, enter=False):
        """
        安全输入文本，带有重试机制和可见性检查，支持回车键操作
        
        参数:
        - locator: 元素定位器
        - text: 要输入的文本
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 每次尝试的超时时间（秒）
        - clear_first: 是否先清空输入框
        - max_attempts: 最大尝试次数
        - enter: 是否在输入后按下回车键
        
        返回:
        - 成功返回 True，失败返回 False
        """
        for attempt in range(max_attempts):
            try:
                # 等待元素可见且可点击
                element = WebDriverWait(self.driver, timeout).until(
                    lambda driver: EC.visibility_of_element_located((locator_type, locator))(driver) and 
                                EC.element_to_be_clickable((locator_type, locator))(driver)
                )
                
                # 滚动到元素
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                
                # 清空输入框（如果需要）
                if clear_first:
                    element.clear()
                
                # 输入文本
                element.send_keys(text)
                
                # 如果需要按下回车键
                if enter:
                    from selenium.webdriver.common.keys import Keys
                    element.send_keys(Keys.RETURN)
                    # print(f"已安全输入文本并按下回车键: {locator}, 文本: {text} (尝试 {attempt + 1}/{max_attempts})")
                else:
                    print(f"已安全输入文本: {locator}, 文本: {text} (尝试 {attempt + 1}/{max_attempts})")
                    
                return True
                
            except TimeoutException:
                print(f"等待元素可见且可点击超时: {locator} (尝试 {attempt + 1}/{max_attempts})")
            except Exception as e:
                print(f"安全输入文本失败: {locator}, 错误: {e} (尝试 {attempt + 1}/{max_attempts})")
            
            # 如果不是最后一次尝试，等待一段时间后重试
            if attempt < max_attempts - 1:
                time.sleep(2)  # 等待2秒后重试
        
        print(f"经过 {max_attempts} 次尝试后，安全输入文本失败: {locator}")
        return False

    def is_element_in_viewport(self, locator, locator_type=By.XPATH, timeout=5):
        """
        检查元素是否在视口内（可见且未被遮挡）
        
        参数:
        - locator: 元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        
        返回:
        - 元素在视口内返回 True，否则返回 False
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator))
            )
            
            # 使用 JavaScript 检查元素是否在视口内
            in_viewport = self.driver.execute_script("""
                var elem = arguments[0];
                var rect = elem.getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
            """, element)
            
            # print(f"元素在视口内: {locator}, 结果: {in_viewport}")
            return in_viewport
        except TimeoutException:
            print(f"等待元素存在超时: {locator}")
            return False
        except Exception as e:
            print(f"检查元素是否在视口内失败: {locator}, 错误: {e}")
            return False

    def ensure_element_visible(self, locator, locator_type=By.XPATH, timeout=30):
        """
        确保元素可见（如果不在视口内，则滚动到元素位置）
        
        参数:
        - locator: 元素定位器
        - locator_type: 定位器类型（默认为 CSS_SELECTOR）
        - timeout: 超时时间（秒）
        
        返回:
        - 成功返回 True，失败返回 False
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator))
            )
            
            # 检查元素是否在视口内
            in_viewport = self.driver.execute_script("""
                var elem = arguments[0];
                var rect = elem.getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
            """, element)
            
            # 如果不在视口内，滚动到元素位置
            if not in_viewport:
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                # print(f"已滚动元素到视口内: {locator}")
            else:
                # print(f"元素已在视口内: {locator}")
                pass
            # 等待元素可见
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of(element)
            )
            # TODO  在此处增加遮蔽消除
            return True
        except TimeoutException:
            print(f"等待元素存在或可见超时: {locator}")
            return False
        except Exception as e:
            print(f"确保元素可见失败: {locator}, 错误: {e}")
            return False
        

    def is_mask_go_away(self):  
        # 等待遮罩层消失（最多等10秒）
        try:
            # 定位遮罩层（根据实际class或id调整）
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "x-mask"))
            )
            # print("遮罩层已消失")
            return True
        except TimeoutException:
            print("超时：遮罩层未消失")

    def double_click(self,element):
        ActionChains(self.driver).double_click(element).perform()

    def get_elements(self, locator, locator_type=By.XPATH):
        """

        查找一组元素（带等待）
        
        参数:
        - locator: 元素定位器
        - locator_type: 定位器类型（默认为 XPATH）
        - timeout: 超时时间（秒）
        - poll_frequency: 轮询频率（秒）
        
        返回:
        - 找到的可见元素列表，如果失败则返回 None
        """
        try:

            elements = self.driver.find_elements(by=locator_type,value=locator)
            
            # print(f"找到可见元素: {locator}")
            return elements
        
        except Exception as e:
            print(f"查找可见元素失败: {locator}, 错误: {e}")
            return None


# 使用示例
if __name__ == "__main__":
    edge_driveFile_path = r"C:\Users\jhu00\OneDrive - Textron\Documents\code\eam-auto-operation\drive files\msedgedriver.exe"

    eam_edge = ExtJSSeleniumHelper(headless=False,executable_path=edge_driveFile_path)  # 设置为 True 可启用无头模式
    
    try:
        # 加载ERIC页面
        success = eam_edge.load_extjs_page(
            ERIC, 
            max_retries=3,
            # component_query='grid[title="用户列表"]'  # 等待用户列表网格加载
        )
        
        if success:
            # 页面加载成功，可以进行操作
            print("可以开始操作页面")
            success = False
            ema_tag = eam_edge.switch_to_new_tab()
        else:
            print("页面加载失败，请检查网络连接或页面地址")
            
        
            # if ema_tag:
            #     print(f'成功切换到新标签页')
            #     # 进入iframe
            #     success = eam_helper.switch_to_iframe(locators['page_frame'])
            #     if success:
            #         print(f'成功进入iframe')


    finally:
        time.sleep(5)
        eam_edge.quit()
        # pass