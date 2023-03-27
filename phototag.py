#Python exif image tagger
import os
import piexif
from PIL import Image
from GPSPhoto import gpsphoto
from webdav3.client import Client
import json
from fuzzywuzzy import process
from geopy.geocoders import Nominatim

script_path = str(os.getcwd()).replace(os.path.sep, '/')

with open("{}/{}".format(script_path, "config.json")) as json_data_file:
    data = json.load(json_data_file)
#print(data["host"])
#print(data["fotograph"])
#print(data["social"])

#global var
foto_dir = input("path to image directory:\n")
fotograph = data["fotograph"]
event = input("Event:")
location = input("Event Location:")
title = input("Titel:")
social = data["social"]

#webdav settings
options = {
 'webdav_hostname': data["host"],
 'webdav_login':    data["WebDav"],
 'webdav_password': input("password"),
 'webdav_timeout': 120
}

#strip data
for root, dir, files in os.walk(foto_dir):
  for file in files:
    if file.lower().endswith(".jpg"):
      piexif.remove(os.path.join(root, file))
      
#geolocation
geolocator = Nominatim(user_agent="PhotoTag")
location = geolocator.geocode(location)

lat = location.latitude
long = location.longitude
info = gpsphoto.GPSInfo((long, lat))
#print(info)
#print(long, lat)

#FILES
file_list = [f for f in os.listdir(foto_dir) if f.endswith('.jpg')]

#GPS TAGGING
for i in file_list:
    photo = gpsphoto.GPSPhoto("{}/{}".format(foto_dir, i))
    photo.modGPSData(info, "{}/{}".format(foto_dir, i))

#exif tagging
for i in file_list:
    #print("{}/{}".format(foto_dir, i))
    im = Image.open("{}/{}".format(foto_dir, i))
    
    exif = im.getexif()
    exif[0x013b] = fotograph
    exif[0x010e] = event 
    exif[0x010d] = title
    exif[0x9286] = social
    
    im.save("{}/{}".format(foto_dir, i), exif=exif)
    
#webdav upload
client = Client(options)

#check if event dir exists create if not
webDav = client.list("/Medien/Events")
#for i in range(len(webDav)):
    #print(process.extractOne(event, webDav))
    
if process.extractOne(event, webDav) != 100 :
    client.mkdir("/{}/{}/{}".format("Medien", "Events", event))
        
webDav2 = client.list("/{}/{}/{}".format("Medien", "Events", event))
#for i in range(len(webDav2)):
    #print(process.extractOne(fotograph, webDav2))
    
if process.extractOne(fotograph, webDav) != 100 :
    client.mkdir("/{}/{}/{}/{}".format("Medien", "Events", event, fotograph))
      
client.upload(remote_path="/{}/{}/{}/{}".format("Medien", "Events", event, fotograph), local_path=foto_dir)

print("Done")
