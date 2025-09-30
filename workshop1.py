# Import the json library so that we can handle json
import json

data = json.load(open("network_devices.json","r",encoding = "utf-8"))

for location in data["locations"]:
    
    print(location["site"])