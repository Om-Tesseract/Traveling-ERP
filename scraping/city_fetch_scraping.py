import requests
import json
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
city_list=[]
for city in top_100_tourist_cities_in_india:    
    r = requests.get(f"https://www.nexusdmc.com/gen/msc/hotel-dest-suggest?q={city}&__xreq__=true&incCStAr=true&flrHC=true", cookies=cookies)
    r_json=r.json()
    if r_json[0].get('data').get('st') is None:
        city_list.append(r_json[0])
with open('./scraping/city_list.json','w',encoding='utf-8') as f:
    json.dump(city_list, f, indent=4)
