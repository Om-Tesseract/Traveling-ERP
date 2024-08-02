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
import requests
chromedriver_path = r'./chromedriver/chromedriver.exe'

# Set up Chrome options if needed (e.g., headless mode, specific settings)
chrome_options = webdriver.ChromeOptions()
# Uncomment the next line if you want to run Chrome in headless mode
# chrome_options.add_argument("--headless")
# chrome_options.add_experimental_option('detach',True)
chrome_options.add_argument(r"user-data-dir=C:\\Users\\omadr\\AppData\\Local\\Google\\Chrome\\User Data")
# name of the directory - change this directory name as per your system
chrome_options.add_argument("--profile-directory=Default")
# Set up the Chrome WebDriver using the webdriver_manager
# service = ChromeService(ChromeDriverManager().install())
service = ChromeService(chromedriver_path)

# Initialize the Chrome WebDriver
# driver = webdriver.Chrome(service=service, options=chrome_options)
url = "https://www.nexusdmc.com/hotels/search?&checkinDate=03%2F08%2F2024&checkoutDate=06%2F08%2F2024&nationality=2597&roomspax=%7B%22rooms%22%3A%5B%7B%22ad%22%3A2%2C%22ch%22%3A0%7D%5D%7D"
# driver.get(url)


# hotel = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@id="htlSltrCtr"]/div[1]/div[2]/div/div/div/div[1]/dl/dd/span/input[@placeholder="City or hotel name"]'))
# )
# hotel.clear()
# hotel.clear()
# time.sleep(1)

# hotel.send_keys('Delhi')
# time.sleep(1)
# hotel.send_keys(Keys.ENTER)


# searchbtn=WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@id="htlSltrCtr"]/div[1]/div[2]/div/div/div/div[6]/dl/dd/a'))
# )
# searchbtn.click()
# time.sleep(10)

cookies = {
    "_vaS19id": "fc90857221fa2af74c70d54dad10ea3f",
    "_vaTS3us": "MCRyYWpqYW5pQHRlc3NlcmFjdHRlY2hub2xhYnMuY29t",
    "_vaH43pd": "NkwyM0FTMEZmQVV3NVVkOXhsNUFHaDNQQ093bHlwR2JwWTZUdmZqeldQSTRIR1B2ZTBlUEpOU2xSbFVnQkdjVzBpVkVOcHU0MGlnSQ0KbmZkOTl0Y0tmZz09",
    "_vaSk7dk": "NTA4NTM1NQ==",
    "JSESSIONID": "E043F01468ADE59155CE92A8C245530C",
    "ssid": "t8"
}

top_100_tourist_cities_in_india = [
    "Agra", "Delhi", "Jaipur", "Mumbai", "Chennai", "Kolkata", "Bangalore", "Hyderabad", "Pune", "Ahmedabad",
    "Goa", "Udaipur", "Jaisalmer", "Jodhpur", "Varanasi", "Rishikesh", "Haridwar", "Amritsar", "Shimla", "Manali",
    "Dharamshala", "Mysuru", "Madikeri", "Ooty", "Munnar", "Alappuzha", "Cochin", "Thiruvananthapuram", "Madurai", "Puducherry",
    "Mahabalipuram", "Tirupati", "Hampi", 
    "Badami", "Bijapur", "Chikmagalur", "Gulmarg", "Leh", "Srinagar", "Pahalgam",
    "Abu", "Bikaner", "Pushkar", "Khajuraho", "Bhopal", "Indore", "Nagpur", "Aurangabad",
    "Nashik", "Shirdi", "Lonavala", "Mahabaleshwar", "Panchgani", "Puri", "Bhubaneswar", "Konark", "Gaya",
    "Patna", "Darjeeling", "Gangtok", "Kalimpong", "Shillong", "Tawang", "Kaziranga", "Majuli", "Guwahati",
    "Imphal", "Kohima", "Aizawl", "Agartala",  "Ranchi", "Jamshedpur", "Bodh Gaya", 
    "Jabalpur", "Raipur", "Bilaspur", "Jagdalpur", "Durgapur", "Siliguri", "Digha", "Kharagpur", "Asansol",
    "Diu", "Daman", "Silvassa", "Lakshadweep", "Port Blair", "Matheran", "Khandala",
    "Nainital", "Mussoorie", "Ranikhet", "Jim Corbett National Park", "Badrinath", "Kedarnath", "Gangotri", "Yamunotri"
]

for city in top_100_tourist_cities_in_india:    
    r = requests.get(f"https://www.nexusdmc.com/gen/msc/hotel-dest-suggest?q={city}&__xreq__=true&incCStAr=true&flrHC=true", cookies=cookies)
    r_json=r.json()
    print("===>",r_json[0])
  
# with open('test.html', 'w', encoding='utf-8') as file:
#         file.write(str(soup))