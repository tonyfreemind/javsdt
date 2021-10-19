# 尝试使用selenium通过cf但并未成功

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

options = webdriver.ChromeOptions()
options.binary_location = "D:/MySoftware/360family/360Chrome/Chrome/Application/360chrome.exe"

# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# options.add_argument("--disable-blink-features=AutomationControlled")
ua = 'cat'
options.add_argument('--user-agent=%s' % ua)

# driver = webdriver.Chrome(options=options, executable_path="D:/MyIDE/driver/chromedriver.exe")
driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
# driver = webdriver.Chrome(options=options)
driver.get("http://www.n53i.com")
# WebDriverWait(driver, 30, 0.5)
# time.sleep(10)
print(driver.get_cookies())
driver.close()