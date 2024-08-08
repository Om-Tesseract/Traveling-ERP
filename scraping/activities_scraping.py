import os
import re
import requests
import json
import django
import sys
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travellingagent.settings')

django.setup()
from io import BytesIO
from django.core.files import File
from api.models import Cities,Activity
popular_cities_in_india = [
    # {"state": "Andhra Pradesh", "cities": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Araku Valley"]},
    # {"state": "Arunachal Pradesh", "cities": ["Itanagar", "Tawang", "Ziro", "Pasighat"]},
    # {"state": "Assam", "cities": ["Guwahati", "Dibrugarh", "Silchar", "Kaziranga", "Jorhat"]},
    # {"state": "Bihar", "cities": ["Patna", "Gaya", "Bhagalpur", "Bodh Gaya", "Nalanda"]},
    # {"state": "Chhattisgarh", "cities": ["Raipur", "Bilaspur", "Durg", "Jagdalpur"]},
    {"state": "Goa", "cities": ["Goa"]},
    # {"state": "Goa", "cities": ["Panaji", "Margao", "Vasco da Gama", "Calangute", "Anjuna"]},
    # {"state": "Gujarat", "cities": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Dwarka", "Gir"]},
    # {"state": "Haryana", "cities": ["Gurgaon", "Faridabad", "Panipat", "Kurukshetra"]},
    # {"state": "Himachal Pradesh", "cities": ["Shimla", "Manali", "Dharamshala", "Kullu", "Kasol"]},
    # {"state": "Jharkhand", "cities": ["Ranchi", "Jamshedpur", "Dhanbad", "Deoghar"]},
    # {"state": "Karnataka", "cities": ["Bangalore", "Mysore", "Mangalore", "Hubli-Dharwad", "Hampi", "Coorg"]},
    # {"state": "Kerala", "cities": ["Thiruvananthapuram", "Cochin", "Kozhikode", "Alappuzha ", "Munnar"]},
    # {"state": "Madhya Pradesh", "cities": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Khajuraho", "Ujjain"]},
    # {"state": "Maharashtra", "cities": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Lonavala"]},
    # {"state": "Manipur", "cities": ["Imphal", "Churachandpur", "Ukhrul"]},
    # {"state": "Meghalaya", "cities": ["Shillong", "Tura", "Cherrapunji"]},
    # {"state": "Mizoram", "cities": ["Aizawl", "Lunglei", "Champhai"]},
    # {"state": "Nagaland", "cities": ["Kohima", "Dimapur", "Mokokchung"]},
    # {"state": "Odisha", "cities": ["Bhubaneswar", "Cuttack", "Rourkela", "Puri", "Konark"]},
    # {"state": "Punjab", "cities": ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala"]},
    # {"state": "Rajasthan", "cities": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Jaisalmer", "Pushkar"]},
    # {"state": "Sikkim", "cities": ["Gangtok", "Namchi", "Pelling"]},
    # {"state": "Tamil Nadu", "cities": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Ooty", "Kanyakumari"]},
    # {"state": "Telangana", "cities": ["Hyderabad", "Warangal", "Nizamabad", "Khammam"]},
    # {"state": "Tripura", "cities": ["Agartala", "Udaipur", "Dharmanagar"]},
    # {"state": "Uttar Pradesh", "cities": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Mathura", "Allahabad"]},
    # {"state": "Uttarakhand", "cities": ["Dehradun", "Haridwar", "Nainital", "Rishikesh", "Mussoorie"]},
    # {"state": "West Bengal", "cities": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Darjeeling", "Sundarbans"]}
]
def ensure_url_scheme(url):
    """Ensure the URL has a valid scheme."""
    if not url.startswith(('http://', 'https://')):
        print("adding scheme =======>",'https:' + url  )
        return 'https://www.holidify.com' + url  # Assuming https as default
    # print(url)
    return url
def file_object(img_url, image_name):
    if img_url:
        response = requests.get(img_url)
    
        if response.status_code == 200:
            image_file = BytesIO(response.content)
            django_file = File(image_file, name=image_name)
            return django_file
    return None


city_list=[]
city_not_found=[]

for data in popular_cities_in_india:
    for city in data["cities"]: 
        url=f"https://www.holidify.com/places/{city.lower()}/sightseeing-and-things-to-do.html"
        r=requests.get(url)  
        print(r.status_code,url)
        if r.status_code == 200:
            if Cities.objects.filter(name=city).exists():
                city_obj=Cities.objects.filter(name=city).first()
                print(city_obj)
                soup= BeautifulSoup(r.content,'html.parser')

                div_card=soup.find_all('div',class_='card content-card')
                div_img=soup.find('div',class_='swipe-gallery')
                if div_img:
                    # Extract the style attribute
                    style_attr = div_img.get('style', '')
                    # Use a regular expression to extract the URL from the style attribute
                    url_match = re.search(r"url\('(.*?)'\)", style_attr)
                    if url_match:
                        url = url_match.group(1)
                        city_obj.img=file_object(url,f"{city}.jpg")
                        city_obj.img_url=url
                        city_obj.save()
                        print("City Img URL:", url)
                    else:
                        print("URL not found")

                for card in div_card[:10]:
                    link = card.find('a')
                    
                    if link:
                    
                        detail_url = link.get('href')
                        detail_response = requests.get(ensure_url_scheme(detail_url))
                        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                        img_div=detail_soup.find('div',class_='swipe-gallery')
                        img_url=None
                        if img_div:
                            # Extract the style attribute
                            style_attr = img_div.get('style', '')

                            # Use a regular expression to extract the URL from the style attribute
                            url_match = re.search(r"url\('(.*?)'\)", style_attr)
                            if url_match:
                                img_url = url_match.group(1)
                                print("Extracted URL:", img_url)
                            else:
                                print("URL not found")

                        # print(detail_soup.find('div',class_='lazyBG swipe-image'))
                        # Extracting the title
                        title = card.find('h3', class_='card-heading').text.split('.')[1].strip() if card.find('h3', class_='card-heading') else None
                        sequence = card.find('h3', class_='card-heading').text.split('.')[0].strip() if card.find('h3', class_='card-heading') else None

                        # Extracting the highlight
                        highlight = card.find('div', class_='readMoreSmall').text if card.find('div', class_='readMoreSmall') else None

                        # Extracting the description
                        desc = card.find('p', class_='card-text').text if card.find('p', class_='card-text') else None

                        # Extracting "Time Required" from the detail page
                        time_required_tag = detail_soup.find('b', string='Time Required :')
                        if time_required_tag:
                            time_required = time_required_tag.next_sibling.strip()
                        else:
                            time_required = None
                        tag = detail_soup.find('b', string='Tags :')
                        if tag:
                            tag_name = tag.next_sibling.strip()
                        else:
                            tag_name= None
                        
                       
                        # Extracting "Entry Fee" from the detail page
                        entry_fee_tag = detail_soup.find('b', string='Entry Fee :')
                        if entry_fee_tag:
                            entry_fee = entry_fee_tag.parent.get_text(strip=True).replace('Entry Fee :', '').strip()
                        else:
                            entry_fee = None
                        print(sequence,title)
                        # print(f'Time Required: {time_required}')
                        # print(f'Entry Fee: {entry_fee}')
                        if title:
                            if not Activity.objects.filter(activity_name=title,activity_city=city_obj).exists():
                               Activity.objects.create(
                                   activity_name=title,
                                   entry_fee=entry_fee,
                                   duration=time_required,
                                   activity_desc=desc,
                                   sequence=sequence,
                                   activity_img=file_object(img_url,f'{title}.jpg'),
                                   activity_city=city_obj,
                                   category=tag_name.lower() if tag_name else None
                               ) 
                            else:
                                print("already exists==>",title)

        else:
             print("not found ===>",city)
        
             city_not_found.append(city)

print(city_not_found)
