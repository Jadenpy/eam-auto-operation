from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import TimeoutException
import time
import os
from path import ERIC

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
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
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
                self.wait_for_extjs_ready(120)
                
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

# 使用示例
if __name__ == "__main__":
    edge_driveFile_path = r"C:\Users\jhu00\OneDrive - Textron\Documents\code\eam-auto-operation\drive files\msedgedriver.exe"

    eam_helper = ExtJSSeleniumHelper(headless=False,executable_path=edge_driveFile_path)  # 设置为 True 可启用无头模式
    
    try:
        # 加载页面并等待特定组件
        success = eam_helper.load_extjs_page(
            ERIC, 
            max_retries=3,
            # component_query='grid[title="用户列表"]'  # 等待用户列表网格加载
        )
        
        if success:
            # 页面加载成功，可以进行操作
            print("可以开始操作页面")
            """
            # 例如，获取网格的存储对象
            store = eam_helper.execute_extjs_method('grid[title="用户列表"]', 'getStore')
            if store:
                print("成功获取存储对象")
                
            # 这里可以添加更多的页面操作代码
            """
    finally:
        time.sleep(5)
        eam_helper.quit()
        # pass