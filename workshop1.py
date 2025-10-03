# Import the json library so that we can handle json
import json
from datetime import datetime

# Read json from products.json to the variable data
data = json.load(open("network_devices.json","r",encoding = "utf-8"))

time = datetime.now()
t_format = time.strftime('%Y-%m-%d %H:%M:%S') 

if "last_updated" in data:
    time = datetime.fromisoformat(data["last_updated"])
    t_format2 = time.strftime('%Y-%m-%d %H:%M:%S')

# Create a variable that holds our whole text report
report = ""

report += "\nDEVICES WITH PROBLEMS\n"
report += "--------------------------\n"
report += "Status: OFFLINE\n"

for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "offline":
            report += (" "
                    + device["hostname"].ljust(18)
                    + device["ip_address"].ljust(20)
                    + device["type"].ljust(15)
                    + location["site"].ljust(15)+ "\n"
                    )
            
report += "\nStatus: WARNING\n"

for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "warning":
            line = (" "
                    + device["hostname"].ljust(18)
                    + device["ip_address"].ljust(20)
                    + device["type"].ljust(15)
                    + location["site"].ljust(15)
        )
            
            warning = ""
            if "uptime_days" in device and device["uptime_days"] < 6:
                warning += "Uptime days: " + str(device["uptime_days"]).ljust(3)
            if "connected_clients" in device and device["connected_clients"] > 40:
                warning += "Connected clients: " + str(device["connected_clients"]).ljust(10)

            report += line + warning + "\n"


report += "\nDEVICES WITH LOW UPTIME (<30 days)\n"
report += "----------------------------------------\n"
report += "Hostname".ljust(18) + "Uptime".ljust(12) + "Site".ljust(18) + "Status\n"

for location in data["locations"]:

    sorted_devices = sorted(
        location["devices"],
        key=lambda d: int(d.get("uptime_days", 9999))
    )

    for device in sorted_devices:
        if "uptime_days" in device and int(device["uptime_days"]) < 31:
            hostname = device["hostname"].ljust(18)
            uptime = (str(device["uptime_days"]) + " days").ljust(12)
            site = location["site"].ljust(18)
            status = "⚠ WARNING" if device.get("status") == "warning" else ""
            report += hostname + uptime + site + status + "\n"

# Create a summary of the critical data
summary =""
summary += "--------------------------------------------------------------------------------------------------\n"
summary += "NETWORK REPORT: "
for company in data["company"]:
    summary += company
summary += "\n--------------------------------------------------------------------------------------------------\n"
summary += f"Report Date: {t_format}\n"
summary += f"Data Update: {t_format2}\n"
summary += "\n"
summary += "SUMMARY\n"
summary += "--------------------------------------------------------------------------------------------------\n"

offline = 0
for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "offline":
            offline += 1

summary += f"⚠ Critical: {offline} devices is offline\n"

warning = 0
for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "warning":
            warning += 1

summary += f"⚠ Warning: {warning} devices with warnings\n"

uptime = 0
for location in data["locations"]:
    for device in location["devices"]:
        if device["uptime_days"] < 31:
            uptime += 1

summary += f"⚠ {uptime} devices with low uptime (<30 days)\n"

port_usage = 0
for location in data["locations"]:
    for device in location["devices"]:
        if "ports" in device:
            total_ports = device["ports"]["total"]
            used_ports = device["ports"]["used"]
            usage_percent = (used_ports / total_ports) * 100
        
            if usage_percent > 80:
                port_usage += 1

summary += f"⚠ {port_usage} switches with high port usage (>80%)\n"
                        
# Add summary before main report
report = summary + report

# write the report to text file
with open('report.txt', 'w', encoding='utf-8') as f:
    f.write(report)