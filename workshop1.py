# Import the json library so that we can handle json
import json

# Read json from products.json to the variable data
data = json.load(open("network_devices.json","r",encoding = "utf-8"))

# Create a variable that holds our whole text report
report = ""

report += "\nDEVICES WITH PROBLEMS\n"
report += "----------------------\n"
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

# Create a summary of the critical data
summary =""
summary += "--------------------------------------------------------------------------------------------------\n"
summary += "NETWORK REPORT - TechCorp AB\n"
summary += "--------------------------------------------------------------------------------------------------\n"
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