from locator import Locator
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC    
import time
     
          
class MySite:
    SELELIUM_WEB_URL = "https://www.selenium.dev/selenium/web/web-form.html"

    def __init__(self):
        self._driver_define()

    def _driver_define(self):
        option = webdriver.EdgeOptions()
        # 指定浏览器驱动路径
        executable_path = r'C:\Users\jhu00\OneDrive - Textron\Documents\code\eam-auto-operation\drive files\msedgedriver.exe'  # 请替换为实际路径
        service = webdriver.EdgeService(executable_path=executable_path)
        self.driver = webdriver.Edge(options= option,service=service)  # 可根据需要更换为其他浏览器驱动
        self.wait = WebDriverWait(self.driver, 10)  # 显式等待，最长等待时间为10秒

    def open_selelium_web(self):
        self.driver.get(self.SELELIUM_WEB_URL)

    def element_write(self,by=By.XPATH, locator='', text='Default Text'):
        element = self.driver.find_element(by, locator)
        element.clear()
        element.send_keys(text)

    def element_click(self, by=By.XPATH, locator=''):
        element = self.driver.find_element(by, locator)
        element.click()

    def element_get_text(self,by=By.XPATH, locator=''):
        element = self.driver.find_element(by, locator)
        return element.text