from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))

url="https://www.google.com/travel/flights?tfs=CBwQARoPag0IAhIJL20vMDFkODhjQAFIAXABggELCP___________wGYAQI&tfu=KgIIAw"

driver.get(url)
from_city = driver.find_element(By.XPATH, '//*[@id="ow64"]/div[1]/div/div/input')
to_city = driver.find_element(By.XPATH, '//*[@id="i23"]/div[4]/div/div/div[1]/div/div/input')
from_city.send_keys('Ahmedabad')
from_city.send_keys('Jaipur')
