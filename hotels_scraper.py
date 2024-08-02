import json
import os
import django
import requests
from bs4 import BeautifulSoup
from django.db.models import Q
from lxml import etree 
# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travellingagent.settings')
from io import BytesIO
from django.core.files import File

# Initialize the Django environment
django.setup()
from api.models import Hotel,HotelDetails,HotelImages
from api.models import Cities

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
query = Q()
i=0
for city in top_100_tourist_cities_in_india:
    query |= Q(name=city)
    # cities = Cities.objects.filter(name=city).values('name','state__name','country__name')
    # print("==========>",city)
    # for city in cities:
    #     i=i+1

    #     city_name=f"{city.get('name')} {city.get('state__name')} {city.get('country__name')}"
    #     print(i,city_name)
cities = Cities.objects.filter(query).values('name','state__name','country__name','id')

for city in cities:
        try:
            i=i+1
    
            city_name=f"{city.get('name')} {city.get('state__name')} {city.get('country__name')}"
            print(i,city_name)
            # url=F"https://www.google.com/travel/search?q={city_name}&ts=CAESCgoCCAMKAggDEAAqCwoFOgNJTlIaACgH&ved=0CAAQ5JsGahgKEwi4o87Cx9CHAxUAAAAAHQAAAAAQ5QM&ictx=3&qs=CAAgACgA&ap=MAA"
            # url=F"https://www.google.com/travel/search?q={city_name}&ts=CAESCgoCCAMKAggDEAAqDAoICgEjOgNJTlIoCA&ictx=3&qs=CAAgACgA&ap=KigKEgmA4sIsebU3QBHiiSB-GM1WQBISCW296UBN_jdAEeKJIB5v1lZAMAA&ved=0CAAQ8IAIahgKEwi4o87Cx9CHAxUAAAAAHQAAAAAQ6xA"
            # url=F"https://www.google.com/travel/search?q=hotels%20in%20{city_name}&ts=CAESCgoCCAMKAggDEAAaUwo1EjEyJTB4Mzc1M2Y0MGRjOTQxMjNhNzoweGQwYTEyNjNjNmM0MGM4Yzc6CEFnYXJ0YWxhGgASGhIUCgcI6A8QCBgQEgcI6A8QCBgRGAEyAggCKhMKDQoBIxIDAwQFOgNJTlIaACgI&ictx=3&qs=CAEgACgAOA1IAA&ap=KigKEgmA4sIsebU3QBHiiSB-GM1WQBISCW296UBN_jdAEeKJIB5v1lZAMAE&ved=0CAAQ5JsGahgKEwi4o87Cx9CHAxUAAAAAHQAAAAAQ_xA"
            url=F"https://www.google.com/travel/search?q=hotels%20in%20{city_name}&ts=CAESCgoCCAMKAggDEAAqEwoNCgEjEgMDBAU6A0lOUhoAKAg&ictx=3&qs=CAAgACgASAA&ap=KigKEgmnviNSSiQ7QBHQ4owBhH9TQBISCZUcSfj_NTtAEdDijMEYhVNAMAC6AQhvdmVydmlldw&ved=0CAAQ5JsGahgKEwj4n6D1_dKHAxUAAAAAHQAAAAAQ9gI"
            r= requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            # dom = etree.HTML(str(soup)) 
            hotels=[]
            main_element=soup.findAll('div',class_='uaTTDe BcKagd bLc2Te Xr6b1e')
            for me in main_element:
                hotel_name=me.find('h2',class_='BgYkof ogfYpf ykx2he').text
                if not Hotel.objects.filter(name=hotel_name).exists():
                    img_elements=me.findAll('img',class_='x7VXS wnGtLb q5P4L')
                    pics=[]
                    # review_star_label=me.find('span',class_='ta47le').get('aria-label')
                    review_count_text=None
                    review_star_text=None

                    if me.find('span',class_='ta47le'):
                        review_star_elem=me.find('span',class_='ta47le').find('span',class_='KFi5wf lA0BZ')
                        review_star_text=review_star_elem.text.strip() if review_star_elem else None

                        review_count_elem=me.find('span',class_='ta47le').find('span',class_='jdzyld XLC8M')
                        review_count_text=review_count_elem.text.strip() if review_count_elem else None
                    price_elem=me.find('span',class_='qQOQpe prxS3d')
                    price_txt=price_elem.text.strip() if price_elem else None
                    amenities_ele=me.findAll('li',class_='XX3dkb bX73z lh4a3')
                    amenities=[]
                    for amti in amenities_ele:
                         amenities.append(amti.text)
                    print(hotel_name,amenities)

                    for img in img_elements:
                        src = img.get('data-src')
                        pics.append(src)

                    link_ele=me.find('a',class_='PVOOXe')
                    if link_ele:
                        link=f"https://www.google.com{link_ele.get('href')}"
                        # print(link)
                        req= requests.get(link)
                        detail = BeautifulSoup(req.content, 'html.parser')
                        hotel_desc_ele=detail.findAll('p',class_='GtAk2e')

                        hotel_descriptions = []
                        hotel_star=detail.findAll('span',class_='CFH2De')
                        star_rating = None
                        for detail in hotel_star:
                            text = detail.get_text()
                            if 'star hotel' in text:
                                # Extract the number before '-star hotel'
                                star_rating = int(text.split('-')[0])
                                break
                        print("Star",star_rating)
                        for hot_desc in hotel_desc_ele:
                            cleaned_text = hot_desc.get_text().replace('… More', '').strip()  # Remove '… More' and any extra whitespace
                            hotel_descriptions.append(cleaned_text)

                        full_description = '<br/>'.join(hotel_descriptions)
                        hotel_detail_el=detail.findAll('span',class_='XGa8fd')
                        address_txt = ""
                        phone_no_txt = ""

                        # Check if the hotel_detail_el list contains enough elements before accessing them
                        if len(hotel_detail_el) > 0:
                            address_txt = hotel_detail_el[0].get_text()

                        if len(hotel_detail_el) > 1:
                            phone_no_txt = hotel_detail_el[1].get_text()

                        amenities_detail_el =detail.find('div',class_="eFfcqe G8T82")
                        amenities_dict={}
                        if amenities_detail_el:
                            print("=========>",)
                            for el in amenities_detail_el.find_all('div',class_="IYmE3e"):
                            
                                        main_amenities=el.find('h4',class_="rSPaxb YMlIz")
                                        sub_amenities=el.find_all('li',class_="IXICF")
                                        if main_amenities.get_text():
                                            amenities_dict[main_amenities.get_text()]=[]
                                            # print(main_amenities.get_text())
                                            for sa in sub_amenities:
                                                amenities_dict[main_amenities.get_text()].append(sa.get_text())
                                                # print(sa.get_text())
                            # print(amenities_dict)
                        context={
                             "name":hotel_name,
                             "pics":pics,
                             "review_star":review_star_text,
                             "review_count":review_count_text,
                             "amenities_short":amenities,
                             "link":link,
                             "description":full_description,
                             "address":address_txt,
                             "phone":phone_no_txt,
                            "amenities":amenities_dict                     

                        }

                        contact_info={
                           "address": context.get('address'),
                           'phone': context.get('phone'),
                        }
                        if not Hotel.objects.filter(name=hotel_name).exists(): 
                            hotel_obj=Hotel.objects.create(
                                name=context.get('name'),
                                address=context.get('address'),
                                city_id=city.get('id'),
                                desc=context.get('description'),
                                 contact_info=contact_info,
                                 link=link,
                                 review_count=review_count_text,
                                 rate=review_star_text,
                                 amenities=amenities_dict,
                                 image_url=pics[0] if len(pics) >0 else None,
                                star_rating=star_rating   
                            )
                            count=1
                            for img_url in pics: 
                                # if img_url.startswith('https://lh5.googleusercontent.com'):
                                    response = requests.get(img_url)
                                    print(img_url)

                                    image_name = f"{hotel_name}_{count}.jpg"
                                    count=count+1
                                    if response.status_code == 200:
                                        image_file = BytesIO(response.content)
                                        # image_name = img_url.split("/")[-1]  # Use the image's filename from the URL

                                        # Create a Django File object
                                        django_file = File(image_file, name=image_name)
                                        print(django_file)
                        #             # Save the image to the HotelImages model
                                        HotelImages.objects.create(hotel=hotel_obj, image=django_file)
                            # hotels.append(context)
                            print("success added ",hotel_name)
        except Exception as e:
             print("error adding ",e)
        # print(hotels)

        
        

#                             #     print(main_amenities.get_text()) 
#                 # print(amenities_detail_el)
#                 # hotel_desc_text=hotel_desc_ele.text if hotel_desc_ele else None
#                 # print(hotel_desc_text)
#             # print(hotel_name,'======>',pics)
#         filename = f"hotels.json"
#         with open(filename, 'w', encoding='utf-8') as file:
#             json.dump(hotels,file,indent=4)
#     # main_ele=dom.xpath('//*[@id="id"]/c-wiz/c-wiz[3]')
#     # print(main_ele)