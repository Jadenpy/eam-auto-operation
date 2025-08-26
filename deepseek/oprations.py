# 动作封装

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
import time

def switch_to_new_tab(driver, original_handles=None, timeout=30):
    """
    切换到最新打开的标签页
    
    参数:
    - driver: WebDriver 实例
    - original_handles: 原始窗口句柄列表，如果不提供则使用当前所有窗口句柄
    - timeout: 等待新标签页打开的超时时间（秒）
    
    返回:
    - 新标签页的句柄，如果失败则返回 None
    """
    if original_handles is None:
        original_handles = driver.window_handles
    
    # 等待新标签页打开
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.window_handles) > len(original_handles)
        )
    except TimeoutException:
        print(f"在 {timeout} 秒内未检测到新标签页打开")
        return None
    
    # 获取所有窗口句柄
    all_handles = driver.window_handles
    
    # 找出新打开的标签页（最后一个通常是新打开的）
    new_handles = [handle for handle in all_handles if handle not in original_handles]
    
    if not new_handles:
        print("未找到新标签页")
        return None
    
    # 切换到新标签页
    new_handle = new_handles[-1]  # 通常最新打开的是最后一个
    
    try:
        driver.switch_to.window(new_handle)
        print(f"已切换到新标签页: {new_handle}")
        return new_handle
    except NoSuchWindowException:
        print(f"无法切换到标签页 {new_handle}，可能已关闭")
        return None

def click_and_switch_to_new_tab(driver, element_locator, locator_type=By.CSS_SELECTOR, timeout=30):
    """
    点击元素并切换到新打开的标签页
    
    参数:
    - driver: WebDriver 实例
    - element_locator: 元素定位器
    - locator_type: 定位器类型（默认为 CSS_SELECTOR）
    - timeout: 超时时间（秒）
    
    返回:
    - 新标签页的句柄，如果失败则返回 None
    """
    # 获取当前所有窗口句柄
    original_handles = driver.window_handles
    
    try:
        # 等待元素可点击并点击
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((locator_type, element_locator))
        )
        element.click()
        print(f"已点击元素: {element_locator}")
    except Exception as e:
        print(f"点击元素失败: {e}")
        return None
    
    # 切换到新标签页
    return switch_to_new_tab(driver, original_handles, timeout)

# 使用示例
def example_usage(driver, url):
    """
    使用示例：打开页面，点击链接，切换到新标签页
    """
    try:
        # 打开页面
        driver.get(url)
        
        # 点击一个会打开新标签页的链接
        # 这里使用 CSS 选择器示例，您可以根据实际情况修改
        new_tab_handle = click_and_switch_to_new_tab(
            driver, 
            "a.new-tab-link",  # 替换为您的实际选择器
            By.CSS_SELECTOR,
            timeout=30
        )
        
        if new_tab_handle:
            print("成功切换到新标签页")
            # 在这里执行您在新标签页中需要的操作
            
            # 示例：等待新页面加载完成（等待某个元素出现）
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print("新页面已加载完成")
            except TimeoutException:
                print("新页面加载超时")
            
            # 操作完成后，可以选择关闭新标签页并切换回原标签页
            # driver.close()  # 关闭当前标签页
            # driver.switch_to.window(original_handles[0])  # 切换回原标签页
            
            return True
        else:
            print("切换到新标签页失败")
            return False
            
    except Exception as e:
        print(f"操作过程中发生错误: {e}")
        return False

# 完整的标签页管理类
class TabManager:
    def __init__(self, driver):
        self.driver = driver
        self.original_tab = None
    
    def open_new_tab(self, element_locator, locator_type=By.CSS_SELECTOR, timeout=30):
        """打开新标签页并切换到它"""
        if self.original_tab is None:
            self.original_tab = self.driver.current_window_handle
        
        result = click_and_switch_to_new_tab(
            self.driver, element_locator, locator_type, timeout
        )
        return result is not None
    
    def switch_to_original_tab(self):
        """切换回原始标签页"""
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
        """关闭当前标签页并切换回原始标签页"""
        if len(self.driver.window_handles) <= 1:
            print("只有一个标签页，无法关闭")
            return False
        
        current_handle = self.driver.current_window_handle
        self.driver.close()
        
        # 如果关闭的是原始标签页，需要更新原始标签页引用
        if current_handle == self.original_tab:
            self.original_tab = None
        
        return self.switch_to_original_tab()

# 使用 TabManager 的示例
def example_with_tab_manager(driver, url):
    """
    使用 TabManager 管理标签页的示例
    """
    tab_manager = TabManager(driver)
    
    try:
        # 打开页面
        driver.get(url)
        
        # 点击链接打开新标签页
        if tab_manager.open_new_tab("a.new-tab-link", By.CSS_SELECTOR, 30):
            print("成功打开并切换到新标签页")
            
            # 在新标签页中执行操作
            # ...
            
            # 关闭新标签页并返回原始标签页
            tab_manager.close_current_tab_and_switch_back()
            
            return True
        else:
            print("打开新标签页失败")
            return False
            
    except Exception as e:
        print(f"操作过程中发生错误: {e}")
        return False
    

