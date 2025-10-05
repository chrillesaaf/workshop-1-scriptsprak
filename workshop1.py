# Import the json library so that we can handle json
import json
from datetime import datetime

# Read json from products.json to the variable data
data = json.load(open("network_devices.json","r",encoding = "utf-8"))

# Import from internet to get date and time for today

time = datetime.now()
t_format = time.strftime('%Y-%m-%d %H:%M:%S') 

# Import date and time from Json-file to get the reportdate

if "last_updated" in data:
    time = datetime.fromisoformat(data["last_updated"])
    t_format2 = time.strftime('%Y-%m-%d %H:%M:%S')

# Create a variable that holds our whole text report
report = ""

# Import devices with problems from Json-file

report += "\nDEVICES WITH PROBLEMS\n"
report += "--------------------------------------------------------------------------\n"
report += "Status: OFFLINE\n"

for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "offline":
            report += (" "
                    + device["hostname"].ljust(18)
                    + device["ip_address"].ljust(20)
                    + device["type"].capitalize().ljust(15)
                    + location["site"].ljust(15)+ "\n"
                    )

# Import devices with warnings from Json-file

report += "\nStatus: WARNING\n"

for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "warning":
            line = (" "
                    + device["hostname"].ljust(18)
                    + device["ip_address"].ljust(20)
                    + device["type"].capitalize().ljust(15)
                    + location["site"].ljust(15)
        )
            
            warning = ""
            if "uptime_days" in device and device["uptime_days"] < 6:
                warning += "Uptime days: " + str(device["uptime_days"]).ljust(3)
            if "connected_clients" in device and device["connected_clients"] > 40:
                warning += "Connected clients: " + str(device["connected_clients"]).ljust(10)

            report += line + warning + "\n"

# Import devices with low uptime from Json-file
# Need to fix it, sort uptimedays low to high

report += "\nDEVICES WITH LOW UPTIME (<30 days)\n"
report += "----------------------------------------------------------------\n"
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

stats = {}

# Search all devices in all locations
for location in data["locations"]:
    for device in location["devices"]:
        dev_type = device.get("type", "unknown")
        status = device.get("status", "unknown")

# if not found
        if dev_type not in stats:
            stats[dev_type] = {"total": 0, "offline": 0}

# total
        stats[dev_type]["total"] += 1

        # räkna upp offline om status är "offline"
        if status.lower() == "offline":
            stats[dev_type]["offline"] += 1

# Calculate total
total_devices = sum(v["total"] for v in stats.values())
total_offline = sum(v["offline"] for v in stats.values())
offline_percent = round(total_offline / total_devices * 100, 1)

# Build report
report += "\nSTATISTICS BY DEVICE TYPE\n"
report += "-------------------------------------------------------------\n"

custom_names = {
    "switch": "Switch",
    "router": "Router",
    "access_point": "Access Point",
    "firewall": "Firewall",
    "load_balancer": "Load Balancer"
}

for dev_type, value in stats.items():
    display_name = custom_names.get(dev_type.lower(), dev_type)
    name = (display_name + ":").ljust(18)
    total = str(value["total"]).rjust(3)
    offline = f"({value['offline']} offline)"
    report += f"{name}{total} st {offline}\n"

report += "-------------------------------------------------------------\n"
report += f"TOTAL:{str(total_devices).rjust(15)} devices ({total_offline} offline = {offline_percent}% offline)\n"

report += "\nPORT USAGE ON SWITCHES\n"
report += "-------------------------------------------------------------\n"
report += "Site".ljust(15) + "Switches".ljust(10) + "Used/Total".ljust(15) + "Usage\n"

total_used_ports = 0
total_ports = 0

for location in data["locations"]:
    switches = [d for d in location["devices"] if d.get("type", "").lower() == "switch"]
    if not switches:
        continue  # skip sites with no switches

    num_switches = len(switches)
    used_ports = sum(d["ports"]["used"] for d in switches)
    total_ports_site = sum(d["ports"]["total"] for d in switches)
    usage_percent = (used_ports / total_ports_site) * 100 if total_ports_site > 0 else 0

# Warning levels
    if usage_percent >= 95:
        status = "⚠ CRITICAL!"
    elif usage_percent >= 85:
        status = "⚠"
    else:
        status = ""

# Add line to report
    report += (
        location["site"].ljust(15)
        + f"{num_switches} st".ljust(10)
        + f"{used_ports}/{total_ports_site}".ljust(15)
        + f"{usage_percent:.1f}% {status}".rstrip()  # remove extra spaces
        + "\n"
    )

# accumulate totals
    total_used_ports += used_ports
    total_ports += total_ports_site

# Totals
total_usage_percent = (total_used_ports / total_ports) * 100 if total_ports > 0 else 0
report += f"\nTotal: {total_used_ports}/{total_ports} ports used ({total_usage_percent:.1f}%)\n"


# Create a summary of the critical data
summary =""
summary += "----------------------------------------------------------------------------\n"
summary += f"NETWORK REPORT: {data['company']}\n"
summary += "--------------------------------------------------------------------------\n"
summary += f"Report Date: {t_format}\n"
summary += f"Data Update: {t_format2}\n"
summary += "\n"
summary += "SUMMARY\n"
summary += "----------------------------------------------------------------------------\n"

# Import devices with offline-status from Json-file

offline = 0
for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "offline":
            offline += 1

summary += f"⚠ Critical: {offline} devices is offline\n"

# Import devices with warning-status from Json-file

warning = 0
for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "warning":
            warning += 1

summary += f"⚠ Warning: {warning} devices with warnings\n"

# Import devices with low uptime from Json-file

uptime = 0
for location in data["locations"]:
    for device in location["devices"]:
        if device["uptime_days"] < 31:
            uptime += 1

summary += f"⚠ {uptime} devices with low uptime (<30 days)\n"

# Import devices with high port usage from Json-file

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