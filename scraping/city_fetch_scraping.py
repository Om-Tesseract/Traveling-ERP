import os
import requests
import json
import django
import sys
cookies = {
    "_vaS19id": "fc90857221fa2af74c70d54dad10ea3f",
    "_vaTS3us": "MCRyYWpqYW5pQHRlc3NlcmFjdHRlY2hub2xhYnMuY29t",
    "_vaH43pd": "NkwyM0FTMEZmQVV3NVVkOXhsNUFHaDNQQ093bHlwR2JwWTZUdmZqeldQSTRIR1B2ZTBlUEpOU2xSbFVnQkdjVzBpVkVOcHU0MGlnSQ0KbmZkOTl0Y0tmZz09",
    "_vaSk7dk": "NTA4NTM1NQ==",
    "JSESSIONID": "E043F01468ADE59155CE92A8C245530C",
    "ssid": "t8"
}
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travellingagent.settings')

django.setup()
from api.models import Cities,States,Country,Hotel

# top_100_tourist_cities_in_india = [
#     "Agra", "Delhi", "Jaipur", "Mumbai", "Chennai", "Kolkata", "Bangalore", "Hyderabad", "Pune", "Ahmedabad",
#     "Goa", "Udaipur", "Jaisalmer", "Jodhpur", "Varanasi", "Rishikesh", "Haridwar", "Amritsar", "Shimla", "Manali",
#     "Dharamshala", "Mysuru", "Madikeri", "Ooty", "Munnar", "Alappuzha", "Cochin", "Thiruvananthapuram", "Madurai", "Puducherry",
#     "Mahabalipuram", "Tirupati", "Hampi", 
#     "Badami", "Bijapur", "Chikmagalur", "Gulmarg", "Leh", "Srinagar", "Pahalgam",
#     "Abu", "Bikaner", "Pushkar", "Khajuraho", "Bhopal", "Indore", "Nagpur", "Aurangabad",
#     "Nashik", "Shirdi", "Lonavala", "Mahabaleshwar", "Panchgani", "Puri", "Bhubaneswar", "Konark", "Gaya",
#     "Patna", "Darjeeling", "Gangtok", "Kalimpong", "Shillong", "Tawang", "Kaziranga", "Majuli", "Guwahati",
#     "Imphal", "Kohima", "Aizawl", "Agartala",  "Ranchi", "Jamshedpur", "Bodh Gaya", 
#     "Jabalpur", "Raipur", "Bilaspur", "Jagdalpur", "Durgapur", "Siliguri", "Digha", "Kharagpur", "Asansol",
#     "Diu", "Daman", "Silvassa", "Lakshadweep", "Port Blair", "Matheran", "Khandala",
#     "Nainital", "Mussoorie", "Ranikhet", "Jim Corbett National Park", "Badrinath", "Kedarnath", "Gangotri", "Yamunotri"
# ]
popular_cities_in_india = [
    {"state": "Andhra Pradesh", "cities": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Araku Valley"]},
    {"state": "Arunachal Pradesh", "cities": ["Itanagar", "Tawang", "Ziro", "Pasighat"]},
    {"state": "Assam", "cities": ["Guwahati", "Dibrugarh", "Silchar", "Kaziranga", "Jorhat"]},
    {"state": "Bihar", "cities": ["Patna", "Gaya", "Bhagalpur", "Bodh Gaya", "Nalanda"]},
    {"state": "Chhattisgarh", "cities": ["Raipur", "Bilaspur", "Durg", "Jagdalpur"]},
    {"state": "Goa", "cities": ["Panaji", "Margao", "Vasco da Gama", "Calangute", "Anjuna"]},
    {"state": "Gujarat", "cities": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Dwarka", "Gir"]},
    {"state": "Haryana", "cities": ["Gurgaon", "Faridabad", "Panipat", "Kurukshetra"]},
    {"state": "Himachal Pradesh", "cities": ["Shimla", "Manali", "Dharamshala", "Kullu", "Kasol"]},
    {"state": "Jharkhand", "cities": ["Ranchi", "Jamshedpur", "Dhanbad", "Deoghar"]},
    {"state": "Karnataka", "cities": ["Bangalore", "Mysore", "Mangalore", "Hubli-Dharwad", "Hampi", "Coorg"]},
    {"state": "Kerala", "cities": ["Thiruvananthapuram", "Cochin", "Kozhikode", "Alappuzha ", "Munnar"]},
    {"state": "Madhya Pradesh", "cities": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Khajuraho", "Ujjain"]},
    {"state": "Maharashtra", "cities": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Lonavala"]},
    {"state": "Manipur", "cities": ["Imphal", "Churachandpur", "Ukhrul"]},
    {"state": "Meghalaya", "cities": ["Shillong", "Tura", "Cherrapunji"]},
    {"state": "Mizoram", "cities": ["Aizawl", "Lunglei", "Champhai"]},
    {"state": "Nagaland", "cities": ["Kohima", "Dimapur", "Mokokchung"]},
    {"state": "Odisha", "cities": ["Bhubaneswar", "Cuttack", "Rourkela", "Puri", "Konark"]},
    {"state": "Punjab", "cities": ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala"]},
    {"state": "Rajasthan", "cities": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Jaisalmer", "Pushkar"]},
    {"state": "Sikkim", "cities": ["Gangtok", "Namchi", "Pelling"]},
    {"state": "Tamil Nadu", "cities": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Ooty", "Kanyakumari"]},
    {"state": "Telangana", "cities": ["Hyderabad", "Warangal", "Nizamabad", "Khammam"]},
    {"state": "Tripura", "cities": ["Agartala", "Udaipur", "Dharmanagar"]},
    {"state": "Uttar Pradesh", "cities": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Mathura", "Allahabad"]},
    {"state": "Uttarakhand", "cities": ["Dehradun", "Haridwar", "Nainital", "Rishikesh", "Mussoorie"]},
    {"state": "West Bengal", "cities": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Darjeeling", "Sundarbans"]}
]

city_list=[]
for data in popular_cities_in_india:
    for city in data["cities"]:   
        r = requests.get(f"https://www.nexusdmc.com/gen/msc/hotel-dest-suggest?q={city}&__xreq__=true&incCStAr=true&flrHC=true", cookies=cookies)
        r_json=r.json()

        if r_json[0].get('data').get('st') is None:
            city_dict=r_json[0]
            city_dict["state"]=data.get('state')
            # print(city_dict.get('data').get('nm'),"=====>",Cities.objects.filter(name=city_dict.get('data').get('nm')).exists())
            if not Cities.objects.filter(name=city_dict.get('data').get('nm')).exists():
                states=States.objects.filter(name=data.get('state')).first()
                if states:
                    Cities.objects.create(name=city_dict.get('data').get('nm'),state=states,country=states.country)
                # print(states.name)
            city_list.append(city_dict)
with open('./scraping/city_list.json','w',encoding='utf-8') as f:
    json.dump(city_list, f, indent=4)
