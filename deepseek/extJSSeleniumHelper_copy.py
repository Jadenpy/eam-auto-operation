from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException,NoSuchElementException,WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from typing import Optional,Union
import time

import time
import os
from path import ERIC

from path import locators

class ExtJSSeleniumHelper:

    LONG = 130
    MIDDLE = 70
    SHORT = 30
    
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
        options.add_argument("--start-fullscreen")
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
            # 1. 图片加载：禁用（核心目标项）
            # 2表示「禁止加载」；
            # 1（允许加载，CONTENT_SETTING_ALLOW），或 0（默认行为，CONTENT_SETTING_DEFAULT）。
            "profile.managed_default_content_settings.images": 2,
            # 2. CSS 加载：禁用（核心目标项）
            # 表示「禁止加载」；
            # 恢复加载 CSS 需改为 1（允许）或 0（默认）
            "profile.managed_default_content_settings.stylesheets": 2,
            # 3. JavaScript 加载：允许（你配置中保留了 JS，因 ExtJS 需要）
            "profile.managed_default_content_settings.javascript": 1,  # 允许JS（ExtJS需要）
            # 4. Flash 加载：禁用
            "profile.managed_default_content_settings.flash": 2,
            # 5. 浏览器插件加载：禁用
            "profile.managed_default_content_settings.plugins": 2,
            # 6. 弹窗（如广告弹窗）：禁用
            "profile.managed_default_content_settings.popups": 2,
            # 7. 地理位置请求：禁用（避免网站请求获取位置）
            "profile.managed_default_content_settings.geolocation": 2,
            # 8. 通知请求：禁用（避免网站弹出通知）
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




    def _wait(self, overtime:float=LONG ,ignored_exceptions:WebDriverException=None) ->WebDriverWait:
        """
        定义显示等待
        参数：
            overtime: 超时时间设置值， 默认为LONG.
        返回：
            WebDriverWait的实例
        """
        
        return WebDriverWait(driver=self.driver,timeout=float(overtime),poll_frequency=0.5,ignored_exceptions=ignored_exceptions)

    def _getting_element_method(self,pos_value:str,element:WebElement,pos_by=By.XPATH)->WebElement:
        """
        获取element,依据是否有by_value以及element
        """
        if pos_value and not element:
            # el = wait.until(self._element_ensure_clickable(pos_value,pos_by))
            el = self.driver.find_element(pos_by,pos_value)
        elif not pos_value and element:
            el = element
        return el

    def _is_element_exist(self,pos_value,pos_by=By.XPATH) -> Union[WebElement,bool]:
        """
        判断元素是否存在？
        参数：
        value: 元素的定位值;
        by:    元素的定位方式， 默认XPATH;
        返回：
        如果元素存在，则返回元素，否则为False。
        """
        try:
            # print('检查元素是否存在...')
            return self.driver.find_element(pos_by,pos_value)
        except NoSuchElementException:
            return False 

    # def _are_elements_exist(self,pos_value,pos_by=By.XPATH) -> Union[WebElement,bool]:
    #     """
    #     判断元素是否存在？
    #     参数：
    #     value: 元素的定位值;
    #     by:    元素的定位方式， 默认XPATH;
    #     返回：
    #     如果元素存在，则返回元素，否则为False。
    #     """
    #     try:
    #         # print('检查元素是否存在...')
    #         return self.driver.find_element(pos_by,pos_value)
    #     except NoSuchElementException:
    #         return False    

    def _is_element_into_view(self, elem:WebElement) ->None:
        """
        执行脚本，让元素进入视角。
        """
        self.driver.execute_script("""
            arguments[0].scrollIntoView({
                block: 'center',  // 垂直居中
                inline: 'nearest',// 水平最近
                behavior: 'smooth'// 平滑滚动（避免滚动过快导致的元素状态不稳定）
            });
        """, elem)
        


    def _is_element_blocked(self,elem:WebElement) -> bool:
        """
        执行脚本，检查元素是否被遮蔽
        """
        try:
            is_not_blocked = self.driver.execute_script("""
                var elem = arguments[0];
                var rect = elem.getBoundingClientRect();
                var centerX = rect.left + rect.width/2;
                var centerY = rect.top + rect.height/2;
                var topElem = document.elementFromPoint(centerX, centerY);
                // 遮挡会导致文本渲染不完整，需确保顶层元素是当前元素或其后代
                return elem.contains(topElem);
            """, elem)
            # 方式1：通过class定位遮罩层（如果class唯一）
            wait = self._wait()
            wait.until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, "div.x-mask.x-border-box.x-mask-fixed")  # 遮罩层的完整class
    ))
            if is_not_blocked:
                return True
            print('元素被遮挡,调整中...')
            return False
        except:
            raise

    def _element_ensure_clickable(self, pos_value:str, pos_by=By.XPATH) -> Optional[Union[bool,WebElement]]:
        """内部条件函数：校验元素是否满足所有可点击条件"""
        # ---------------------- 1. 校验1：元素存在于DOM中（避免NoSuchElementException） ----------------------
        try:
        
            wait = self._wait()
            elem = wait.until(lambda x: self._is_element_exist(pos_value,pos_by))

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
            self._is_element_into_view(elem)
        
            # ---------------------- 4. 校验4：元素完全可见（排除隐藏样式） ----------------------
            # is_displayed()是Selenium原生方法，能识别display: none、visibility: hidden等隐藏逻辑
            if not elem.is_displayed():
                return False

            # ---------------------- 5. 校验5：无遮挡元素（排除浮层、遮罩等干扰） ----------------------
            # 用JS获取元素中心点的“顶层元素”，判断是否为当前元素或其后代（避免被其他元素覆盖）
            self._is_element_blocked(elem)

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
            # print(elem)
            return elem
        except:
            raise

    def _element_ensure_readable(self, pos_value:str, pos_by=By.XPATH) -> Optional[Union[bool,WebElement]]:
        """
        确保元素可读取文本
        校验逻辑：元素存在→可见→无遮挡
        :param value: 定位值（如XPath表达式、ID值）
        :param by: 定位方式（默认By.XPATH）
        """
        try:
            # ---------------------- 1. 校验1：元素存在于DOM中（避免NoSuchElementException） ----------------------
            wait = self._wait()
            elem = wait.until(lambda x: self._is_element_exist(pos_value,pos_by))
            

            # ---------------------- 2. 校验2：元素完全可见（隐藏元素文本可能读取为空） ----------------------

            self._is_element_into_view(elem)

            # ---------------------- 3. 校验3：无遮挡（避免遮挡导致文本渲染不完整） ----------------------
            self._is_element_blocked(elem)

            return elem
        except:
            raise
    

    def _element_ensure_writable(self, pos_value:str, pos_by=By.XPATH) -> Optional[Union[bool,WebElement]]:
        """
        确保元素可写入内容（如输入框
        校验逻辑：元素存在→是可输入类型→非禁用→非只读→可见→可聚焦
        :param value: 定位值（如XPath表达式、ID值）
        :param by: 定位方式（默认By.XPATH）
        """
        try:
            # ---------------------- 1. 校验1：元素存在于DOM中 ----------------------
            wait = self._wait()
            elem = wait.until(lambda x: self._is_element_exist(pos_value,pos_by))
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
            self._is_element_into_view(elem)

            # ---------------------- 5. 校验5：元素可聚焦（输入框需能获取焦点才能写入） ----------------------
            # 用JS尝试聚焦元素，并验证是否成功聚焦
            is_focused = self.driver.execute_script("""
                arguments[0].focus();  // 主动聚焦
                return document.activeElement === arguments[0];  // 验证当前焦点是否为该元素
            """, elem)
            if not is_focused:
                return False  # 无法聚焦，写入会失败
            
            return elem
        except:
            raise
    
    def _read_element(self, elem:WebElement,retry_count:int=10) ->Optional[Union[bool,str]]:
        """
        读取文本
        校验逻辑：文本非空→文本可识别（排除乱码/占位符）
        :param elem: 目标元素
        
        """
        # 记录当前重试次数（用于日志和终止条件）
        current_retry = 0
        while current_retry < retry_count:
            try:
                # ---------------------- 4. 校验4：文本非空且可识别（排除空文本/乱码/占位符） ----------------------
                # 获取元素文本（优先用text，若为空则尝试获取innerText（兼容部分框架））
                
                elem_text = elem.text.strip() or elem.get_attribute("value").strip()
                if elem_text != '':
                    return elem_text
                else:
                    raise ValueError(
                        f"读取值为空，重新读取"
                    )
            except ValueError as e:
                # 捕获到 TypeError，准备重试
                time.sleep(0.5)
                current_retry += 1
                print(f"{str(e)}，第 {current_retry}/{retry_count} 次重试...")
            
                # 若重试次数已达上限，不再重试，重新抛出异常
                if current_retry >= retry_count:
                    print(f"重试次数已耗尽（共 {retry_count} 次）")
                    raise
                    

            except Exception as e:
                # 捕获其他未知异常（如元素不可点击、页面刷新等），直接抛出
                print(f"元素点击失败（未知错误）：{str(e)}")
                raise

    def _write_element(self,elem: WebElement,input_text:str = None, enter:bool= False, tab:bool=False) ->bool:
        """
        写入内容（如输入框），并验证写入内容生效
        校验逻辑：写入内容匹配
        :param input_text: 待写入的文本
        :return: True（可写入且内容生效）/ False（未满足条件）
        
        """
        try:
            tag_name = elem.tag_name.lower()
            # ---------------------- 6. 校验6：写入内容并验证生效（若传入input_text） ----------------------
        
            # elem.clear()
            elem.click()
            elem.send_keys(Keys.CONTROL, 'a')
            elem.send_keys(Keys.DELETE)
            # 写入新内容（用send_keys模拟真实输入，适配输入法/自动补全）
            elem.send_keys(input_text)
            if enter:
                elem.send_keys(Keys.ENTER)
            if tab:
                elem.send_keys(Keys.TAB)
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
        except:
            raise


    def element_click(self,pos_value, pos_by=By.XPATH, retry_count:int = 3):
        """
        自定义条件函数：定位元素，若不可见则滚动到可见，并执行点击
        :param self: 实例自身
        :param locator: 元素定位器value
        :return: None
        """
        # 记录当前重试次数（用于日志和终止条件）
        current_retry = 0
        while current_retry < retry_count:
            try:
                # 1. 定位元素（存在于DOM中）
                wait = self._wait()
                elem = wait.until(lambda x:self._element_ensure_clickable(pos_value,pos_by))
                
                # 2. 检查元素是否可见
                if isinstance(elem,WebElement):
                    time.sleep(0.2)
                    # elem.click()
                    self.driver.execute_script("arguments[0].click();", elem)
                    time.sleep(0.2)
                    return
                else:
                    actual_type = type(elem).__name__
                    raise TypeError(
                        f"元素类型错误：期望传入 WebElement 实例，实际传入的是 {actual_type} 类型（值：{elem}）"
                    )
            except TypeError as e:
                # 捕获到 TypeError，准备重试
                current_retry += 1
                print(f"捕获到 TypeError：{str(e)}，第 {current_retry}/{retry_count} 次重试...")
            
                # 若重试次数已达上限，不再重试，重新抛出异常
                if current_retry >= retry_count:
                    print(f"重试次数已耗尽（共 {retry_count} 次），无法修复 TypeError，终止重试")
                    raise  # 重新抛出最终异常，让调用方感知错误
        
            except TimeoutException as e:
                # 捕获“元素定位超时”异常（非TypeError，无需重试，直接抛出）
                print(f"元素定位超时（定位方式：{pos_by}，定位值：{pos_value}）：{str(e)}")
                raise                       
        
            except Exception as e:
                # 捕获其他未知异常（如元素不可点击、页面刷新等），直接抛出
                print(f"元素点击失败（未知错误）：{str(e)}")
                raise

    def element_read(self,pos_value:str,pos_by=By.XPATH) -> str:
        try:
            wait = self._wait()
            el = wait.until(lambda x:self._element_ensure_readable(pos_value,pos_by))
            if isinstance(el,WebElement):
                time.sleep(0.2)
                return  self._read_element(el)
            else:
                actual_type = type(el).__name__
                raise TypeError(f'定位值{pos_value}，定位方式：{pos_by},应该为WebElement实例，但实际为{actual_type}的实例')
        except TypeError as e:
            print(f'类型错误：{str(e)}')
            raise
        except Exception as e:
            print(f'未知错误：{str(e)}')
            raise

    def element_write(self, pos_value:str,input_text:str,pos_by=By.XPATH,enter=False,tab=False): 

        try:
            wait = self._wait()
            el = wait.until(lambda x:self._element_ensure_writable(pos_value,pos_by))
            if isinstance(el,WebElement):
                time.sleep(0.2)
                self._write_element(el,input_text,enter,tab)
            else:
                actual_type = type(el).__name__
                raise TypeError(f'定位值{pos_value}，定位方式：{pos_by},应该为WebElement实例，但实际为{actual_type}的实例')
        except TypeError as e:
            print(f'类型错误：{str(e)}')
            raise
        except Exception as e:
            print(f'未知错误：{str(e)}')
            raise
    
 
    def tab_change(self,new_tag_title:str,number_windows:int = 2)->bool: 
        """
        when new tab is opened, change to it
        """
        try:
            # save the handle of current window
            original_window = self.driver.current_window_handle

            # wait that the window is opened
            wait = self._wait()
            wait.until(EC.number_of_windows_to_be(number_windows))

            # check and change into new tag
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    self.driver.switch_to.window(window_handle)
                    break
            # if title is right 
            if wait.until(EC.title_is(new_tag_title)):
                return True
        except:
            return False

    def elements_get(self,pos_value:str,pos_by=By.XPATH) -> list[WebElement]:

        """
        
        """
        try:
        # 1. 显式等待
            wait = self._wait()
            
        # 2. 定位
            _ = wait.until(EC.presence_of_all_elements_located((pos_by,pos_value)))
        # 3. 返回

            if _:
                return _
        except:
            raise

    def element_get(self,pos_value:str,pos_by=By.XPATH)->WebElement:
        try:
        # 1. 显式等待
            wait = self._wait()
            
        # 2. 定位
            _ = wait.until(EC.presence_of_element_located((pos_by,pos_value)))
        # 3. 返回

            if _:
                return _
        except:
            raise 

    def action_double_click(self,element:WebElement)->None:
        try:
            ActionChains(self.driver).double_click(element).perform()
        except:
            raise

    def element_double_click(self,element:WebElement,pos_value:str=None,pos_by=By.XPATH,overtime=SHORT)->None:

        try:
        # 1. wait def
            # wait = self._wait(overtime=overtime)
        # 2. element can be clicked
            el = self._getting_element_method(pos_value,element,pos_by)
        # 3. do
            if isinstance(el,WebElement):
                time.sleep(0.5)
                self.action_double_click(el) 
        except:
            raise
        finally:
            pass

    def element_child_send_keys(self,parent:WebElement,input_text:str,pos_value:str,pos_by=By.XPATH)->None:
        
        # 子元素
        el = parent.find_element(pos_by,pos_value) 
        if isinstance(el,WebElement):
            el.send_keys(input_text)
        time.sleep(0.5)