import json, requests, os, time
import psutil
import subprocess
import speedtest

if not os.path.exists("static/data.json"):
    with open("static/data.json", "w") as f:
        f.write("{}")

if not os.path.exists("params.json"):
    print("Couldn't find params file")
    exit()


def monkeyType(username):
    res = json.loads(
        requests.get(
            f"https://api.monkeytype.com/users/{username}/profile?isUid=false"
        ).text
    )

    return {
        "monkeyType": {
            "link": f"https://monkeytype.com/profile/{username}",
            "typingStats": res["data"]["typingStats"],
            "personalBests": res["data"]["personalBests"],
        }
    }


def statsFM(username):
    res = {"statsFM": {"link": f"https://stats.fm/user/{username}"}}

    res["statsFM"].update(
        json.loads(
            requests.get(
                f"https://api.stats.fm/api/v1/users/{username}/top/artists?range=weeks&limit=5",
            ).text
        )
    )
    temp = (
        json.loads(
            requests.get(
                f"https://api.stats.fm/api/v1/users/{username}/streams/stats?range=weeks",
                headers={
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "accept-language": "en-US,en;q=0.7",
                    "priority": "u=0, i",
                    "sec-ch-ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                    "sec-fetch-user": "?1",
                    "sec-gpc": "1",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                },
            ).text
        )
    )["items"]
    res["statsFM"].update(
        {
            "duration": temp["durationMs"],
            "count": temp["playedMs"]["count"],
            "count": temp["playedMs"]["min"],
            "count": temp["playedMs"]["max"],
        }
    )
    return res


def brawlStars(id):
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "if-modified-since": "Fri, 03 Jan 2025 03:53:20 GMT",
        "origin": "https://sltbot.com",
        "priority": "u=1, i",
        "referer": "https://sltbot.com/",
        "sec-ch-ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    response = requests.get(
        f"https://img.sltbot.com/player/{id}/ranks?o=h", headers=headers
    )

    if response.status_code == 200:
        with open("files/brawl_ranks.png", "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return {"brawlStars": False}

    response = requests.get(
        f"https://img.sltbot.com/player/{id}/brawlers?o=h", headers=headers
    )

    if response.status_code == 200:
        with open("files/brawl_brawlerInfo.png", "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return {"brawlStars": False}

    response = requests.get(
        f"https://img.sltbot.com/player/{id}/mastery_points?o=h", headers=headers
    )

    if response.status_code == 200:
        with open("files/brawl_mastery.png", "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return {"brawlStars": False}

    return {"brawlStars": True}


def localtime():
    return {"localtime": int(time.time())}


def computerStorage():
    drives = psutil.disk_partitions()
    res = {"storageDrives": []}
    for drive in drives:
        try:
            usage = psutil.disk_usage(drive.mountpoint)
            res["storageDrives"].append(
                {
                    "name": drive.device,
                    "total": usage.total / (1024**3),
                    "used": usage.used / (1024**3),
                    "free": usage.free / (1024**3),
                    "percentageUsed": usage.percent,
                }
            )
        except PermissionError:
            print(f"Drive: {drive.device} (Permission Denied)")
    return res


def get_cpu_info():
    # Get CPU info
    cpu_info = {
        "CPUInfo": {
            "CPU Usage": f"{psutil.cpu_percent(interval=1)}%",
            "CPU Frequency": f"{psutil.cpu_freq().current:.2f} MHz",
            "CPU Cores": psutil.cpu_count(logical=False),
            "Logical CPUs": psutil.cpu_count(logical=True),
        }
    }
    return cpu_info


def get_ram_info():
    # Get RAM info
    ram = psutil.virtual_memory()
    ram_info = {
        "RAMInfo": {
            "Total RAM": f"{ram.total / (1024 ** 2):.2f} MB",
            "Used RAM": f"{ram.used / (1024 ** 2):.2f} MB",
            "Free RAM": f"{ram.free / (1024 ** 2):.2f} MB",
            "RAM Usage": f"{ram.percent}%",
        }
    }
    return ram_info


def wifiSpeed():
    st = speedtest.Speedtest()

    # Get the best server based on ping
    st.get_best_server()

    # Perform download and upload speed tests
    download_speed = st.download() / 1_000_000  # Convert from bits to megabits
    upload_speed = st.upload() / 1_000_000  # Convert from bits to megabits

    # Get ping
    ping = st.results.ping

    return {
        "wifiSpeed": {
            "Download Speed (Mbps)": download_speed,
            "Upload Speed (Mbps)": upload_speed,
            "Ping (ms)": ping,
        }
    }


def getSiegeStats(username):
    res = requests.get(
        "https://api.tracker.gg/api/v2/r6siege/standard/matches/ubi/itscosmatic?"
    ).json()


def getAllData():
    with open("params.json") as f:
        params = json.loads(f.read())

    data = {}

    # add functions to fetch data and add them to list
    data.update(monkeyType(params["monkeyType"]))
    data.update(statsFM(params["statsFM"]))
    data.update(brawlStars(params["brawlStars"]))
    data.update(localtime())
    data.update(computerStorage())
    data.update(get_cpu_info())
    data.update(get_ram_info())
    # data.update(wifiSpeed()) #currently experiencing issues

    with open("static/data.json", "w") as f:
        f.write(json.dumps(data, indent=3))


"""
while True:
    getAllData()
    time.sleep(60*5)
"""
