# Import the json library so that we can handle json
import json

data = json.load(open("network_devices.json","r",encoding = "utf-8"))

# Create a variable that holds our whole text report
report = ""

# loop through the location list
for location in data["locations"]:
    # print the site/name of the location
    report += location["site"] + "\n"
    
    print(location["site"])

with open('report.txt', 'w', encoding='utf-8') as f:
    f.write("Rubrik\n")