import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
chromedriver_path = r'./chromedriver/chromedriver.exe'

# Set up Chrome options if needed (e.g., headless mode, specific settings)
chrome_options = webdriver.ChromeOptions()
# Uncomment the next line if you want to run Chrome in headless mode
# chrome_options.add_argument("--headless")
# chrome_options.add_experimental_option('detach',True)
# Set up the Chrome WebDriver using the webdriver_manager
# service = ChromeService(ChromeDriverManager().install())
service = ChromeService(chromedriver_path)

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)
url = "https://www.google.com/travel/flights?tfs=CBwQARoPag0IAhIJL20vMDFkODhjQAFIAXABggELCP___________wGYAQI&tfu=KgIIAw"
driver.get(url)



from_city = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="i23"]/div[1]/div/div/div[1]/div/div/input[@aria-label="Where from?"]'))
)

from_city.clear()
from_city.send_keys('Delhi')
time.sleep(1)
select_from_city=driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]')
select_from_city.click()

# Wait for the "To" input field to be present and find it uniquely by its placeholder text
to_city = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="i23"]/div[4]/div/div/div[1]/div/div/input[@aria-label="Where to? "]'))
)
to_city.clear()
to_city.send_keys('San Francisco')
time.sleep(1)
select_to_city=driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]')
select_to_city.click()

# Wait for some time to see the results (optional)
time.sleep(2)

# select date
select_departure_date=driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/input[@aria-label="Departure"]')
select_departure_date.send_keys('Wed, Aug 21')
select_departure_date.click()
time.sleep(2)

done_btn=driver.find_element(By.XPATH,'//*[@id="ow79"]/div[2]/div/div[3]/div[3]/div/button[1]')
done_btn.click()

searchbtn=driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[2]/div/button[@aria-label="Search"]') 
searchbtn.click()
time.sleep(2)

# best_flights= driver.find_elements(By.XPATH,'//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul')
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')
flights=soup.find_all('ul',class_='Rk10dc')
# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#         # Build the absolute path to the countries.json file
# file_path = os.path.join(base_dir,'travelling-erp', 'flights.html')
# with open(file_path, encoding='utf-8', mode='w+') as f:
#     f.write(str(flights))
count=0
flights_data = []
for flgt in flights:
    for flgt_li in flgt.find_all('li')[:-1]:
        count+=1
        print(count)

        from_depart=flgt_li.find(class_='G2WY5c sSHqwe ogfYpf tPgKwe').text
        to=flgt_li.find(class_='c8rWCd sSHqwe ogfYpf tPgKwe').text
        dep_time=flgt_li.find(class_='wtdjmc YMlIz ogfYpf tPgKwe').text
        avi_time=flgt_li.find(class_='XWcVob YMlIz ogfYpf tPgKwe').text
        stops=flgt_li.find(class_='VG3hNb').text
        airline=flgt_li.find(class_='h1fkLb').text
        price_div = flgt_li.find(class_='YMlIz FpEdX')
        price = price_div.find('span').text if price_div else "N/A"
        img_div = flgt_li.find(class_='EbY4Pc P2UJoe')
        if img_div:
            style = img_div.get('style')
            # Extract the URL from the style attribute using a regular expression
            img_url_match = re.search(r'url\((.*?)\)', style)
            img_url = img_url_match.group(1) if img_url_match else None
        duration = flgt_li.find(class_='gvkrdb AdWm1c tPgKwe ogfYpf').text
        flight_info = {
            "from_depart": from_depart,
            "to": to,
            "dep_time": dep_time,
            "avi_time": avi_time,
            "stops": stops,
            "airline": airline,
            "price": price,
            "img_url": img_url,
            "duration": duration
        }
        
        flights_data.append(flight_info)

print(flights_data)