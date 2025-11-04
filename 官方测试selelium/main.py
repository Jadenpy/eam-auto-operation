
from class_define import MySite
from selenium.webdriver.common.by import By
from locator import Locator
import time

if __name__ == "__main__":
    mySite = MySite()
    mySite.open_selelium_web()
    
    # mySite.element_write(By.ID,Locator.TEXT_INPUT.value, "Hello Selenium")
    # mySite.element_write(Locator.PASSWORD_INPUT.value, "MySecretPassword")
    # mySite.element_click(Locator.SUBMIT_BUTTON.value)
    time.sleep(15)  # 等待5秒以便查看结果
    mySite.driver.quit()