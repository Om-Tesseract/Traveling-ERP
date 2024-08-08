from django.db import transaction
from bs4 import BeautifulSoup
import os
import requests
import json
import django
import sys
from io import BytesIO
from django.core.files import File
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travellingagent.settings')
django.setup()
from api.models import Hotel, HotelImages, RoomCategory, RoomsImg, RoomType, Cities
cookies = {
    "_vaS19id": "fc90857221fa2af74c70d54dad10ea3f",
    "_vaTS3us": "MCRyYWpqYW5pQHRlc3NlcmFjdHRlY2hub2xhYnMuY29t",
    "_vaH43pd": "NkwyM0FTMEZmQVV3NVVkOXhsNUFHaDNQQ093bHlwR2JwWTZUdmZqeldQSTRIR1B2ZTBlUEpOU2xSbFVnQkdjVzBpVkVOcHU0MGlnSQ0KbmZkOTl0Y0tmZz09",
    "_vaSk7dk": "NTA4NTM1NQ==",
    "JSESSIONID": "E043F01468ADE59155CE92A8C245530C",
    "ssid": "t8"
}


def ensure_url_scheme(url):
    """Ensure the URL has a valid scheme."""
    if not url.startswith(('http://', 'https://')):
        print("adding scheme =======>",'https:' + url  )
        return 'https:' + url  # Assuming https as default
    print(url)
    return url


def file_object(img_url, image_name):
    img_url = ensure_url_scheme(img_url)
    response = requests.get(img_url)

    if response.status_code == 200:
        image_file = BytesIO(response.content)
        django_file = File(image_file, name=image_name)
        return django_file
    return None


# old code
city_hotels = []
with open('./scraping/city_list.json', 'r', encoding="utf-8") as f:
    city_json = json.loads(f.read())
    for city in city_json:
        city_id = city.get('data').get('id')
        state = city.get('state')
        full_city_name = city.get('value',"img").replace(' ','-').replace(',','')
        print(city_id)
        url = "https://www.nexusdmc.com/hotels/search-x"
        payload = {
            "cityId": city_id,
            "state": state,
          
            "checkinDate": "14/08/2024",
            "checkoutDate": "19/08/2024",
            "roomspax": {"rooms": [{"ad": 2, "ch": 0, "chAge": []}]},
            "prHtl": True,
            "__xreq__": True,
        }
        r = requests.post(url, payload, cookies=cookies)
        print(r.text)
        try:
            if r.status_code == 200:
                raw = r.text
                raw = raw.replace('&quot;', '"').replace(
                    '</Success>', '').replace('<Success>', '')
                hotel_json = json.loads(str(raw))
                nationality_id = hotel_json.get('srchO').get('ntn')
                city_name = hotel_json.get('srchO').get('cnm')
                # print(hotel_json)
                main_hotel_dic = {
                    "nationality_id": nationality_id,
                    "city_id": city_id,
                    "city_name": city_name,
                    "nationality": hotel_json.get('srchO').get('ntnD'),

                }
                city_obj = Cities.objects.filter(name=city_name).first()
                if city_obj:
                    hotel_list = hotel_json.get('rsltA')
                    hotels_main_list = []
                    for hotel in hotel_list[:10]:
                        area = hotel.get('area')
                        address = hotel.get('loc')
                        image_url = hotel.get('img')
                        roomtype = hotel.get('rnm')
                        name = hotel.get('nm')
                        star = hotel.get('st')
                        rate = hotel.get('urtO').get(
                            'rt') if hotel.get('urtO') else None
                        numRt = hotel.get('urtO').get(
                            'numRt') if hotel.get('urtO') else None
                        price = hotel.get('pr')
                        meal_plan = hotel.get('mpN')
                        ln = hotel.get('ln') if hotel.get('ln') else None
                        lt = hotel.get('lt') if hotel.get('lt') else None

                        hotel_detail = {
                            "name": name,
                            "address": address,
                            "area": area,
                            "city": city_name,
                            "star_rating": star,
                            "rate": rate,
                            "review_count": numRt,
                            "desc": "",
                            "image_url": image_url,
                            "ln": ln,
                            "lt": lt,
                            "amenities": {},
                            "cleaniless_rate": 0,
                            "service_rate": 0,
                            "comfort_rate": 0,
                            "images": [],
                            "amenities_rate": 0,
                            "rooms_list": []
                        }

                        print('name===>', name)
                        hotel_url = f"https://www.nexusdmc.com{hotel.get('url')}"
                        data = payload
                        amenities_data = {}
                        image_sources = []
                        cleaniless_rate = 0
                        service_rate = 0
                        comfort_rate = 0
                        amenities_rate = 0
                        data.update(
                            {"isConciseLoad": True, "nationality": nationality_id})
                        req = requests.get(
                            hotel_url, data=data, cookies=cookies)
                        if req.status_code == 200:
                            soup = BeautifulSoup(req.content, 'html.parser')
                            address = soup.find('div', class_='address').text if soup.find(
                                'div', class_='address') else None
                            desc = soup.find(
                                'div', class_='htl--dsc').text if soup.find('div', class_='htl--dsc') else None

                            image_divs = soup.find_all(
                                'div', class_='mnImgItm')

                            image_sources = [
                                div.find('img')['src'] for div in image_divs[:7]]
                            amenities = soup.find_all(
                                'div', class_='htl-cnt-subsec')

                            # Iterate through each amenity section
                            for amenity in amenities:
                                # Get the section header
                                header = amenity.find(
                                    'div', class_='htl-cnt-subsec-hd').text.strip()
                                # Get the list of items in this section
                                items = [li.text.strip()
                                         for li in amenity.find_all('li')]
                                # Add to the parsed data dictionary
                                amenities_data[header] = items
                            # print(amenities_data)

                            for rate in soup.find_all('div', class_='rtBarTxt'):

                                label = rate.find('div', class_='barLbl').text if rate.find(
                                    'div', class_='barLbl') else None
                                val = rate.find('div', class_='barVal').text.split(
                                    '/')[0] if rate.find('div', class_='barVal') else None
                                # print("=====>",label, val)
                                if label == "Comfort":
                                    comfort_rate = val
                                if label == "Cleaniless":
                                    cleaniless_rate = val
                                if label == "Amenities":
                                    amenities_rate = val
                                if label == "Service":
                                    service_rate = val

                             # update dir hotel main
                            hotel_detail['address'] = address
                            hotel_detail['desc'] = desc
                            hotel_detail['images'] = image_sources
                            hotel_detail['amenities'] = amenities_data
                            hotel_detail['amenities_rate'] = amenities_rate
                            hotel_detail['cleaniless_rate'] = cleaniless_rate
                            hotel_detail['comfort_rate'] = comfort_rate
                            hotel_detail['service_rate'] = service_rate

                        req = requests.post(
                            hotel_url, data=data, cookies=cookies)
                        with transaction.atomic():
                            if not Hotel.objects.filter(name=hotel_detail.get('name'), city=city_obj).exists():
                                hotel_obj = Hotel.objects.create(
                                    name=hotel_detail.get('name'),
                                    address=hotel_detail.get('address'),
                                    area=hotel_detail.get('area'),
                                    city=city_obj,
                                    star_rating=hotel_detail.get(
                                        'star_rating'),
                                    rate=hotel_detail.get('rate'),
                                    review_count=hotel_detail.get(
                                        'review_count'),
                                    desc=hotel_detail.get('desc'),
                                    img=file_object(hotel_detail.get(
                                        'image_url'), f'{name}.jpg'),
                                    image_url=hotel_detail.get('image_url'),
                                    ln=hotel_detail.get('ln'),
                                    lt=hotel_detail.get('lt'),
                                    amenities=hotel_detail.get(
                                        'amenities', {}),
                                    cleaniless_rate=cleaniless_rate,
                                    service_rate=service_rate,
                                    comfort_rate=comfort_rate,
                                    amenities_rate=amenities_rate,

                                )
                                
                                count = 0
                                for img in hotel_detail.get('images', [])[:7]:
                                    count = count + 1
                                    HotelImages.objects.create(hotel=hotel_obj,
                                                               image=file_object(img, f"{name}_{count}.jpg"),img_url=img)
                                if req.status_code == 200:
                                    raw_txt = req.text
                                    raw_txt = raw_txt.replace('&quot;', '"').replace(
                                        '</Success>', '').replace('<Success>', '')
                                    hotel_detail_json = json.loads(
                                        str(raw_txt))
                                    # print(hotel_detail_json)
                                    room_list = hotel_detail_json.get('rmA')
                                    room_main = []
                                    for room in room_list:
                                        amenities_room = room.get('amA')
                                        room_category = room.get('nm')
                                        bed_type = room.get('bedD')
                                        room_size = room.get('szD')
                                        view_name = room.get('vwN')
                                        rooms = room.get('roptA')
                                        desc = room.get('dsc')
                                        imgs = room.get('imgA', [])
                                        room_cate = RoomCategory.objects.create(
                                            hotel=hotel_obj,
                                            name=room_category,
                                            desc=desc,
                                            view_name=view_name,
                                            room_size=room_size,
                                            bed_type=bed_type,

                                        )
                                        if imgs:
                                            count_room = 0
                                            for rm_img in imgs[:5]:
                                                count_room = count_room + 1
                                                RoomsImg.objects.create(
                                                    room_category=room_cate,
                                                    img=file_object(
                                                        rm_img, f"{room_category}_{count_room}.jpg"),
                                                        img_url=rm_img
                                                )
                                        room_data_list = []
                                        for rm in rooms:

                                            rm_name = rm.get('name')
                                            meal_plan = rm.get('mpN')
                                            price = rm.get('absPrc')
                                            meal_includes = rm.get('mlD')
                                            cur = rm.get('cur')
                                            key = {'key': rm.get('key')}
                                            room_amen = {
                                                "amentiy_room": amenities_room}
                                            RoomType.objects.create(
                                                hotel=hotel_obj,
                                                rnm=rm_name,
                                                cur=cur,
                                                meal_plan=meal_plan,
                                                price=price,
                                                amenity=room_amen,
                                                key=key,
                                                meal_includes=meal_includes,
                                                category=room_cate
                                            )
                                            room_data_list.append({
                                                "rnm": rm_name,
                                                "cur": cur,
                                                "meal_plan": meal_plan,
                                                "price": price,
                                                "amenity": room_amen,
                                                "key": key,
                                                "meal_includes": meal_includes,
                                            })
                                        room_cate_dict = {
                                            "name": room_category,
                                            "desc": desc,
                                            "view_name": view_name,
                                            "room_size": room_size,
                                            "bed_type": bed_type,
                                            "rooms": room_data_list,
                                            'imgs': imgs
                                        }
                                        room_main.append(room_cate_dict)

                                    hotel_detail['rooms_list'] = room_main
                                hotels_main_list.append(hotel_detail)
                                main_hotel_dic["hotels"] = hotels_main_list
                                city_hotels.append(main_hotel_dic)
                                print('url==>', hotel.get('url'))
                            else:
                                print("==> already exists",name)
        except Exception as e:
            print("Error======>", e)

        with open('scraping/results.json', '+w', encoding='utf-8') as f:
            json.dump(city_hotels, f, indent=4)
