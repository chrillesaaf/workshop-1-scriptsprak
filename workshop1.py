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

    if usage_percent >= 95:
        status = "⚠ CRITICAL!"
    elif usage_percent >= 85:
        status = "⚠"
    else:
        status = ""

    report += (
        location["site"].ljust(15)
        + f"{num_switches} st".ljust(10)
        + f"{used_ports}/{total_ports_site}".ljust(15)
        + f"{usage_percent:.1f}% {status}".rstrip()
        + "\n"
    )

    total_used_ports += used_ports
    total_ports += total_ports_site

total_usage_percent = (total_used_ports / total_ports) * 100 if total_ports > 0 else 0
report += f"\nTotal: {total_used_ports}/{total_ports} ports used ({total_usage_percent:.1f}%)\n"

report += "\nSWITCHES WITH HIGH PORT USAGE (>80%)\n"
report += "-------------------------------------------------------------\n"

for location in data ["locations"]:
    for device in location ["devices"]:
        if device.get("type", "").lower() == "switch":
            used = device["ports"]["used"]
            total = device["ports"]["total"]
            if total == 0:
                continue

            usage_percent = (used / total) * 100

            if usage_percent > 80:
                hostname = device["hostname"].ljust(18)
                ports = f"{used}/{total}".ljust(10)
                usage = f"{usage_percent:.1f}%".rjust(8)

            if usage_percent == 100:
                status = "⚠ FULL!".rjust(8)
            else:
                status = " ⚠ "

            report += hostname + ports + usage + status + "\n"

report += "\nVLAN OVERVIEW\n"
report += "-------------------------------------------------------------"

vlans_found = set()

for location in data["locations"]:
    for device in location["devices"]:
        for vlan in device.get("vlans", []):
            vlans_found.add(vlan)

report += f"\nTotal unique VLANs in the network: {len(vlans_found)}\n"
report += "VLANs: "
report += ", ".join(str(vlan) for vlan in sorted(vlans_found)) + "\n"

report += "\nSTATISTICS PER SITE\n"
report += "-------------------------------------------------------------\n"

for location in data["locations"]:
    site = location["site"]
    city = location["city"]
    contact = location["contact"]

    total_devices = len(location["devices"])
    online = sum (1 for device in location["devices"] if device["status"] == "online")
    offline = sum (1 for device in location["devices"] if device["status"] == "offline")
    warning = sum (1 for device in location["devices"] if device["status"] == "warning")

    report += f"{site} ({city}):\n"
    report += f" Devices: {total_devices} ({online} online, {offline} offline, {warning} warning)\n"
    report += f" Contact: {contact}\n"

report += "\nACCESS POINTS - CLIENT OVERVIEW\n"
report += "---------------------------------------------\n"
report += "Highest load:\n"

AP = []

for location in data["locations"]:
    for device in location["devices"]:
        if device.get("type", "").lower() == "access_point":
            clients = device.get("connected_clients", 0)
            AP.append({
                "hostname": device["hostname"],
                "clients": clients
            })

AP.sort(key=lambda x: x["clients"], reverse=True)

for ap in AP:
    if ap["clients"] > 20:
        warning = " ⚠ Overloaded" if ap["clients"] > 40 else ""
        report += f" {ap['hostname'].ljust(16)} {str(ap['clients']).rjust(3)} clients{warning}\n"

report += "\nRECOMMENDATIONS\n"
report += "----------------\n"

# Count offline devices
offline_count = 0
for location in data["locations"]:
    for device in location["devices"]:
        if device.get("status") == "offline":
            offline_count += 1

# Find site with highest port usage
highest_site = ""
highest_usage = 0

for location in data["locations"]:
    total_ports = 0
    used_ports = 0

    for device in location["devices"]:
        if "ports" in device:
            total_ports += device["ports"].get("total", 0)
            used_ports += device["ports"].get("used", 0)

    if total_ports > 0:
        usage_percent = (used_ports / total_ports) * 100
        if usage_percent > highest_usage:
            highest_usage = usage_percent
            highest_site = location["site"]

# Find AP with most clients
most_loaded_ap = ""
most_clients = 0

for location in data["locations"]:
    for device in location["devices"]:
        if device.get("type") == "access_point":
            clients = device.get("connected_clients", 0)
            if clients > most_clients:
                most_clients = clients
                most_loaded_ap = device["hostname"]

# Write report
report += f". URGENT: Investigate offline devices immediately ({offline_count} total)\n"

if highest_usage > 90:
    report += f". CRITICAL: {highest_site} has extremely high port utilization ({highest_usage:.1f}%) - plan for expansion\n"

report += ". Check devices with low uptime, especially those <5 days\n"

if most_clients > 20:
    warning = " (Warning)" if most_clients > 40 else ""
    report += f". {most_loaded_ap} has {most_clients} connected clients{warning} - consider load balancing\n"

report += ". Consider standardizing vendors per site for easier maintenance\n"

# Footer
report += "\n---------------------------------------------------------------------------------------\n"
report += "END OF REPORT".center(80) + "\n"
report += "---------------------------------------------------------------------------------------\n"

# Create a summary of the critical data
summary =""
summary += "--------------------------------------------------------------------------------------\n"
summary += (f"NETWORK REPORT: {data.get('company', 'Unknown')}").center(80) + "\n"
summary += "--------------------------------------------------------------------------------------\n"
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