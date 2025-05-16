"""
Methods for fetching external api data for use on the project
"""

try:
    import json, requests, os, time
    import psutil
    import subprocess
    import speedtest
    from siegeapi import Auth
    import asyncio
    import contextlib
    import re
    from bs4 import BeautifulSoup
    import datetime
    from collections import defaultdict
    from playwright.async_api import async_playwright
    from playwright.sync_api import sync_playwright
except:
    import os

    os.system("pip install psutil speedtest siegeapi bs4 playwright")
    os.system("playwright install chromium")


async def monkeyType(username):
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


async def statsFM(username, userid):
    res = {"statsFM": {"link": f"https://stats.fm/user/{username}"}}

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.7",
        "origin": "https://stats.fm",
        "priority": "u=1, i",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    }

    res["statsFM"].update(
        {
            "lifetime": requests.get(
                f"https://api.stats.fm/api/v1/users/{userid}/streams/stats?range=lifetime",
                headers=headers,
            ).json()
        }
    )

    res["statsFM"].update(
        {
            "4week": {
                "tracks": requests.get(
                    f"https://api.stats.fm/api/v1/users/{username}/top/tracks?range=weeks&limit=10",
                    headers=headers,
                ).json(),
                "artists": requests.get(
                    f"https://api.stats.fm/api/v1/users/{username}/top/artists?range=weeks&limit=10",
                    headers=headers,
                ).json(),
                "albums": requests.get(
                    f"https://api.stats.fm/api/v1/users/{username}/top/albums?range=weeks&limit=11",
                    headers=headers,
                ).json(),
            }
        }
    )

    current_date = datetime.date.today()
    days_to_saturday = (current_date.weekday() - 5) % 7
    start_of_week = current_date - datetime.timedelta(days=days_to_saturday)
    start_of_saturday = datetime.datetime.combine(start_of_week, datetime.time(0, 0, 0))

    start_of_saturday_timestamp = int(start_of_saturday.timestamp() + 60 * 60 * 24)
    res["statsFM"].update(
        {
            "thisweek": {
                "tracks": requests.get(
                    f"https://api.stats.fm/api/v1/users/{userid}/top/tracks?after={start_of_saturday_timestamp}000&before={int(start_of_saturday_timestamp + 60 * 60 * 24 * 7 - 1)}999&limit=10",
                    headers=headers,
                ).json(),
                "artists": requests.get(
                    f"https://api.stats.fm/api/v1/users/{userid}/top/artists?after={start_of_saturday_timestamp}000&before={int(start_of_saturday_timestamp + 60 * 60 * 24 * 7 - 1)}999&limit=10",
                    headers=headers,
                ).json(),
                "albums": requests.get(
                    f"https://api.stats.fm/api/v1/users/{userid}/top/albums?after={start_of_saturday_timestamp}000&before={int(start_of_saturday_timestamp + 60 * 60 * 24 * 7 - 1)}999&limit=11",
                    headers=headers,
                ).json(),
            }
        }
    )

    res["statsFM"].update(
        {
            "6months": {
                "tracks": requests.get(
                    f"https://api.stats.fm/api/v1/users/{username}/top/tracks?range=months&limit=10",
                    headers=headers,
                ).json(),
                "artists": requests.get(
                    f"https://api.stats.fm/api/v1/users/{username}/top/artists?range=months&limit=10",
                    headers=headers,
                ).json(),
                "albums": requests.get(
                    f"https://api.stats.fm/api/v1/users/{username}/top/albums?range=months&limit=10",
                    headers=headers,
                ).json(),
            }
        }
    )

    res["statsFM"] = json.loads(
        json.dumps(res["statsFM"]).replace("768x768bb.jpg", "75x75bb.webp")
    )

    return res


async def localtime():
    return {"localtime": int(time.time())}


async def computerStorage():
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


async def get_cpu_info():
    # Get CPU info
    cpu_info = {
        "CPUInfo": {
            "CPU Usage": psutil.cpu_percent(interval=1),
            "CPU Frequency": f"{psutil.cpu_freq().current:.2f} MHz",
            "CPU Cores": psutil.cpu_count(logical=False),
            "Logical CPUs": psutil.cpu_count(logical=True),
        }
    }
    return cpu_info


async def get_ram_info():
    # Get RAM info
    ram = psutil.virtual_memory()
    ram_info = {
        "RAMInfo": {
            "Total RAM": ram.total / (1024**2),
            "Used RAM": ram.used / (1024**2),
            "Free RAM": ram.free / (1024**2),
            "RAM Usage": ram.percent,
        }
    }
    return ram_info


async def wifiSpeed():
    st = speedtest.Speedtest()
    st.get_best_server()

    download_speed = st.download() / 1_000_000  # Convert from bits to megabits
    upload_speed = st.upload() / 1_000_000  # Convert from bits to megabits

    ping = st.results.ping

    return {
        "wifiSpeed": {
            "down": download_speed,
            "up": upload_speed,
            "Ping (ms)": ping,
        }
    }


async def getBrave(user):
    with open(
        f"C:/Users/{user}/AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Preferences"
    ) as f:
        data = json.loads(f.read())
    data = data["brave"]["stats"]
    return {
        "brave": {
            "ads_blocked": data["ads_blocked"],
            "bandwidth_saved_bytes": data["bandwidth_saved_bytes"],
            "time_saved": int(data["ads_blocked"]) * 50,
        }
    }


async def getLeetcode(username):
    data = requests.get(
        f"https://alfa-leetcode-api.onrender.com/userProfile/{username}"
    ).json()
    return {
        "LeetCode": {
            "easySolved": data["easySolved"],
            "totalEasy": data["totalEasy"],
            "mediumSolved": data["mediumSolved"],
            "totalMedium": data["totalMedium"],
            "hardSolved": data["hardSolved"],
            "totalHard": data["totalHard"],
            "ranking": data["ranking"],
        }
    }


# old, unused
async def siege(username, email, pw):
    auth = Auth(email, pw)
    player = await auth.get_player(name=username)
    res = {}

    res.update({"name": player.name, "profilePic": player.profile_pic_url})

    await player.load_playtime()
    res.update({"playtime": player.total_time_played, "level": player.level})

    await player.load_ranked_v2()
    res.update(
        {
            "currentRankedPoints": player.ranked_profile.rank_points,
            "currentRank": player.ranked_profile.rank,
            "maxRankedPoints": player.ranked_profile.max_rank_points,
            "maxRank": player.ranked_profile.max_rank,
            "season_code": player.ranked_profile.season_code,
        }
    )

    await player.load_progress()
    res.update({"totalXP": player.total_xp})

    await auth.close()
    return {"Siege": res}


async def getUbiPlaytime():
    auth = Auth(
        os.getenv("UBI_EMAIL"), os.getenv("UBI_PW"), creds_path="creds/creds.json"
    )
    player = await auth.get_player(
        name="itscosmatic"
    )  # player doesn't matter, we are only doing this for the api key anyhow

    with open("creds/creds.json") as f:
        creds = json.loads(f.read())

    # predefined list of games, there *may* be a way to automate but am yet to find a solution
    ubiGames = {
        "Trackmania": [
            "5d20614c-234d-4cc8-934d-11ff07c2de69",
            "fdd1afb7-39e7-455d-85eb-bd84a123fd50",
        ],
        "Tom Clancy's Rainbow Six Siege": [
            "0d2ae42d-4c27-4cb7-af6c-2099062302bb",
            "fdd1afb7-39e7-455d-85eb-bd84a123fd50",
        ],
        "Steep": [
            "a20f75db-9175-4df6-b1b3-ba42e291166c",
            "fdd1afb7-39e7-455d-85eb-bd84a123fd50",
        ],
        "Riders Republic": [
            "969de8e2-77f6-4a42-a1a8-5d82d64f0e8d",
            "fdd1afb7-39e7-455d-85eb-bd84a123fd50",
        ],
        "The Crew 2": [
            "90c0ddf3-64c2-40d1-ac53-85ebeccd96eb",  # gameid
            "fdd1afb7-39e7-455d-85eb-bd84a123fd50",  # pc userid
        ],
        "Steep": [
            "fbb6144d-09f9-412f-a2e5-721fdf975702",  # gameid is different for xbox version
            "97dd0d2a-e377-4ee1-80f8-b2d1093d93fa",  # specify the xbox userid instead of pc
        ],
    }

    playtime = {}

    for i in range(len(ubiGames)):
        url = f"https://public-ubiservices.ubi.com/v1/profiles/{ubiGames[list(ubiGames.keys())[i]][1]}/stats?spaceId={ubiGames[list(ubiGames.keys())[i]][0]}"

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.8",
            "Authorization": f"Ubi_v1 t={creds['key']}",
            "origin": "https://account.ubisoft.com",
            "priority": "u=1, i",
            "referer": "https://account.ubisoft.com/",
            "sec-ch-ua": '"Not(A:Brand)";v="99", "Brave";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "sec-gpc": "1",
            "ubi-appid": "c5393f10-7ac7-4b4f-90fa-21f8f3451a04",
            "ubi-sessionid": creds["sessionid"],
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        }

        response = requests.get(url, headers=headers).json()
        playtime.update({list(ubiGames.keys())[i]: response["stats"]["Playtime"]})

    print("Got Ubisoft playtime")
    return {"Ubisoft": playtime}


async def getXboxGamePlaytime():
    games = {"gamescore": 0}
    gamescore = 0
    page = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        )

        await context.add_cookies(
            [
                {
                    "name": "GamerID",
                    "value": os.getenv("TA_GAMERID"),
                    "domain": "www.trueachievements.com",
                    "path": "/",
                },
                {
                    "name": "HashKey",
                    "value": os.getenv("TA_GAMERTOKEN").split("_")[0],
                    "domain": "www.trueachievements.com",
                    "path": "/",
                },
                {
                    "name": "GamerToken",
                    "value": os.getenv("TA_GAMERTOKEN"),
                    "domain": "www.trueachievements.com",
                    "path": "/",
                },
                {
                    "name": "TrueGamingIdentity",
                    "value": os.getenv("TA_TRUE_GAMING_IDENTITY"),
                    "domain": "www.trueachievements.com",
                    "path": "/",
                },
            ]
        )

        while page < 30:
            page_obj = await context.new_page()

            url = (
                f"https://www.trueachievements.com/gamer/{os.getenv('TA_USERNAME')}/gamecollection?"
                f"executeformfunction&function=AjaxList&params=oGameCollection%7C"
                f"%26ddlSortBy%3DLastunlock%26ddlDLCInclusionSetting%3DDLCIOwn"
                f"%26ddlPlatformIDs%3D%26sddOwnerShipStatusIDs%3D%26sddPlayStatusIDs%3D"
                f"%26ddlContestStatus%3DAny%20status%26ddlGenreIDs%3D%26sddGameMediaID%3D"
                f"%20%26ddlGameNotes%3D%20%26ddlStartedStatus%3D0%26ddlCompletionStatus%3D%20"
                f"%26asdGamePropertyID%3D%20%26ddlTitleType%3D%20%26GameView%3DoptListView"
                f"%26chkExcludeNotOwned%3DTrue%26MultiEditMode%3DoptSingleEdit"
                f"%26chkColTitleimage%3DTrue%26chkColTitlename%3DTrue%26chkColPlatform%3DTrue"
                f"%26chkColSiteScore%3DTrue%26chkColOfficialScore%3DTrue%26chkColItems%3DTrue"
                f"%26chkColCompletionpercentage%3DTrue%26chkColMyrating%3DTrue%26chkColTimeplayed%3DTrue"
                f"%26chkColDatestarted%3DTrue%26chkColDatecompleted%3DTrue%26chkColLastunlock%3DTrue"
                f"%26chkColOwnershipstatus%3DTrue%26chkColPlaystatus%3DTrue%26chkColNotforcontests%3DTrue"
                f"%26chkColGamenotes%3DTrue%26txtBaseComparisonGamerID%3D{os.getenv('TA_GAMERID')}%26oGameCollection_Order%3DLastunlock"
                f"%26oGameCollection_Page%3D{page}%26oGameCollection_ItemsPerPage%3D60"
                f"%26oGameCollection_TimeZone%3DPacific%20Standard%20Time%26oGameCollection_ShowAll%3DFalse"
                f"%26txtGamerID%3D{os.getenv('TA_GAMERID')}%26txtGameRegionID%3D1%26txtUseAchievementsForProgress%3DTrue"
                f"%26txtContestID%3D0"
            )

            await page_obj.goto(url)
            content = await page_obj.content()

            if "Sorry there are no matching titles" in content:
                print(f"Final trueachievements page reached at page {str(page)}")
                break

            soup = BeautifulSoup(content, "html.parser")

            for row in soup.find_all("tr"):
                thumbnail = row.find("td", class_="gamethumb")
                if thumbnail:
                    img = thumbnail.find("img")
                    img_url = img["src"] if img else None

                    game_name = row.find("td", class_="smallgame")
                    game_name = game_name.text.strip() if game_name else None

                    time_played = row.find("td", class_="date")
                    if time_played:
                        time_text = time_played.text.strip()
                        match = re.match(r"(\d+)\s*hrs?\s*(\d+)\s*mins?", time_text)
                        if match:
                            hours, minutes = match.groups()
                        else:
                            match = re.match(r"(\d+)\s*mins?", time_text)
                            if match:
                                hours, minutes = 0, match.group(1)
                            else:
                                hours, minutes = None, None
                    else:
                        hours, minutes = None, None

                    scores = row.find_all("td", class_="score")
                    if len(scores) >= 3:
                        score_x_y = [score.text.strip() for score in scores[:3]]

                    # lets save some space by not saving the zero playtime games
                    if game_name not in games and (
                        (hours != None) or (minutes != None)
                    ):
                        games.update(
                            {
                                game_name: {
                                    "name": game_name,
                                    "thumbnail_url": img_url,
                                    "hours": hours,
                                    "minutes": minutes,
                                    "scores": score_x_y,
                                }
                            }
                        )
                        gamescore += int(score_x_y[1].split(" / ")[0].replace(",", ""))
            page += 1
            print(f"finished loading trueachievements page {page}")

        await browser.close()

        if page >= 30:
            print(
                "Xbox scrape loop shut down because safety wall was hit, emergency shutting down."
            )
            exit()

    games["gamescore"] = gamescore
    await downloadXboxThumbnails(games)

    print("Got xbox playtime from trueachievements")
    return {"XboxPlaytime": games}


async def downloadXboxThumbnails(data):
    for i in data:
        if i != "gamescore":
            if not os.path.exists(
                f"static/images/xboxThumbnails/{(data[i]['thumbnail_url']).split('/thumbs/')[1].replace('/', '-')}"
            ):
                try:
                    image_url = (
                        f"https://www.trueachievements.com{data[i]['thumbnail_url']}"
                    )
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        with open(
                            f"static/images/xboxThumbnails/{(data[i]['thumbnail_url']).split('/thumbs/')[1].replace('/', '-')}",
                            "wb",
                        ) as file:
                            file.write(response.content)
                        print(f"{data[i]['name']} image downloaded successfully.")
                    else:
                        print("Failed to retrieve the image.")
                except:
                    continue


async def getSteamPlaytime():
    key = os.getenv("STEAM_API_KEY")
    steamid = int(os.getenv("STEAM_USER_ID"))
    link = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={key}&steamid={steamid}&format=json&include_appinfo=true"
    data = requests.get(link)

    if data.status_code == 200:
        data = data.json()["response"]["games"]
    else:
        print(str(data.status_code) + " error occured fetching steam playtime!")
        return {"steam": {}}

    data = sorted(data, key=lambda x: x["playtime_forever"], reverse=True)

    with open("steam_app_list.json") as f:
        z = json.loads(f.read())

    z = {
        str(app["appid"]): app["name"]
        for app in sorted(z["applist"]["apps"], key=lambda x: str(x["appid"]))
    }

    for i in range(len(data) - 1):
        try:
            data[i].update({"title": z[str(data[i]["appid"])]})
        except:
            continue

    await downloadSteamThumbnails(data)  # get all the images for the games

    print("Got steam playtime")
    return {"steam": data}


async def downloadSteamThumbnails(data):
    for i in data:
        if not os.path.exists(
            f"static/images/steamThumbnails/{(i['img_icon_url'])}.jpg"
        ):
            image_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{i['appid']}/{i['img_icon_url']}.jpg"
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(
                    f"static/images/steamThumbnails/{(i['img_icon_url'])}.jpg",
                    "wb",
                ) as file:
                    file.write(response.content)
                print(f"{'title'} image downloaded successfully.")
            else:
                print("Failed to retrieve the image.")


async def getRobloxPlaytime():
    with open("static/data/roblox.json") as f:
        return {"Roblox": json.loads(f.read())}


async def getSpotifyStatus():
    data = requests.get(
        f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={os.getenv('LASTFM_USERNAME')}&api_key={os.getenv('LASTFM_AUTH')}&format=json&limit=1"
    ).json()

    return {"Spotify": data["recenttracks"]["track"][0]}


async def getBrawl():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"https://brawlace.com/players/{os.getenv('BRAWL_STARS_TAG')}")
        content = await page.content()
        await browser.close()
        html = content

    soup = BeautifulSoup(html, "html.parser")
    data = {}
    rows = soup.select("table.table tbody tr")

    rows = rows[:8]

    for row in rows:
        header = row.find("th").get_text(strip=True)
        value_cell = row.find("td")

        images = value_cell.find_all("img")
        if images:
            value_text = value_cell.get_text(strip=True)
            img_info = [
                {
                    "src": img.get("src"),
                    "title": img.get("title"),
                    "alt_text": img.get("alt") or "",
                }
                for img in images
            ]
            value = {"text": value_text, "images": img_info}
        else:
            value = value_cell.get_text(strip=True)

        data[header] = value

    return {"brawl_stars": data}


async def getValorant():
    url = f"https://api.tracker.gg/api/v2/valorant/standard/profile/riot/{os.getenv('VAL_USERNAME')}?"

    headers = {
        "sec-ch-ua-platform": '"Windows"',
        "Referer": "https://tracker.gg/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(extra_http_headers=headers)
        page = await context.new_page()
        response = await page.goto(url)

        time.sleep(5)

        if response.ok:
            json_data = await response.json()
            print("Fetched Valorant data")
            return {
                "valorant": json_data["data"]["segments"][1]["stats"]["peakRating"][
                    "metadata"
                ]
            }
        else:
            print("Valorant fetch failed")
            return {"valorant": {}}


async def getSiege():
    url = f"https://api.tracker.gg/api/v2/r6siege/standard/profile/ubi/{os.getenv('SIEGE_USERNAME')}?"

    headers = {
        "sec-ch-ua-platform": '"Windows"',
        "Referer": "https://tracker.gg/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(extra_http_headers=headers)
        page = await context.new_page()
        response = await page.goto(url)

        time.sleep(5)

        if response.ok:
            json_data = await response.json()
            print("Fetched Siege data")
            return {"siege": json_data["data"]["segments"][5]["stats"]["maxRankPoints"]}
        else:
            print("Siege fetch failed")
            return {"siege": {}}


async def getRocketLeague():
    url = f"https://api.tracker.gg/api/v2/rocket-league/standard/profile/xbl/{os.getenv('RL_USERNAME')}?"

    headers = {
        "sec-ch-ua-platform": '"Windows"',
        "Referer": "https://tracker.gg/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(extra_http_headers=headers)
        page = await context.new_page()
        response = await page.goto(url)

        time.sleep(5)

        if response.ok:
            json_data = await response.json()

            print("Fetched Rocket League data")
            return {
                "rocket_league": max(
                    json_data["data"]["segments"][
                        len(json_data["data"]["segments"])
                        - 5 : len(json_data["data"]["segments"])
                        - 2
                    ],
                    key=lambda x: x["stats"]["peakRating"]["value"],
                )
            }
        else:
            print("Rocket League fetch failed")
            return {"rocket_league": {}}
