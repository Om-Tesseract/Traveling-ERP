import json
import os
import django
import requests
from bs4 import BeautifulSoup
# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travellingagent.settings')

# Initialize the Django environment
django.setup()

from api.models import Hotel  # Import the model after setting up Django

if __name__ == '__main__':
  
    contact=[]

    # # Fetch all records from the Hotel model
    hotels = Hotel.objects.all()[:4]
    for ht in hotels:
        hotel_name=F"{ht.name} {ht.city.name}".replace(' ','+')
        url=F"https://www.google.com/search?q={hotel_name}&sca_esv=fdfd3cadaaa7fb2f&sca_upv=1&sxsrf=ADLYWIJdWx5Xc6G9Syh2ID46_0kEGQGLTQ%3A1721303194818&source=hp&ei=mgCZZoy3L9Pg4-EPrN7wsAE&iflsig=AL9hbdgAAAAAZpkOquWNRREPValiJDH6VJrRTq-HRQj4&ved=0ahUKEwiM7OaLwrCHAxVT8DgGHSwvHBYQ4dUDCBU&uact=5&oq=The+Highland+Park+Manali&gs_lp=Egdnd3Mtd2l6IhhUaGUgSGlnaGxhbmQgUGFyayBNYW5hbGkyChAjGIAEGCcYigUyFhAuGIAEGEMYxwEYmAUYigUYmgUYrwEyBRAAGIAEMgoQABiABBgUGIcCMggQABiABBiiBDIIEAAYgAQYogRI0QpQsQRYsQRwAXgAkAEAmAGoAaABqAGqAQMwLjG4AQPIAQD4AQL4AQGYAgKgAsUBqAIKwgIHECMYJxjqApgDF5IHAzEuMaAHjgg&sclient=gws-wiz"
        r= requests.get(url)
        print(str(hotel_name))
        soup = BeautifulSoup(r.content, 'html.parser')
        try:
            address=soup.find('span',class_="BNeawe tAd8D AP7Wnd").text
            print(address)
        except Exception as e:
            address=None
            print(hotel_name," address Couldn't find")
        
        try:
            phone=soup.find('div',class_="AVsepf u2x1Od")
            phone_txt=phone.find_all('span',class_="BNeawe tAd8D AP7Wnd")[0].get_text()
            phone_txt=",".join(phone_txt.split('⋅'))
            
        except:
            phone_txt=None
            print(hotel_name," phone Couldn't find")
        if phone_txt is not None or address is not None:
            contact.append({
                "phone":phone_txt if phone_txt else None,
                "address":address,
                "hotel":ht.id,
                "name":ht.name,
                "city":ht.city.id,
                "city_name":ht.city.name,

            })
    print(contact)
    #                 # Define the filename
    # filename = f"contact_hotels.json"
        
    # with open(filename, 'w', encoding='utf-8') as file:
    #       json.dump(contact, file, indent=3)
      
    
    # try:
    #     # Get the current directory of this file
    #     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #     # Build the absolute path to the countries.json file
    #     json_file_path = os.path.join(base_dir,'travelling-erp', 'contact_hotels.json')

        

    #     with open(json_file_path.replace('\\\\','\\'), encoding='utf-8') as f:
    #         htc = json.load(f)
    #         for ht in htc:
    #            contact_info={
    #                "address": ht.get('address'),
    #                'phone': ht.get('phone'),
    #            }
    #            Hotel.objects.filter(id=ht.get('hotel')).update(contact_info=contact_info)
    #            print("ok")
    # except Exception as e:
    #     print(e)
    
   
