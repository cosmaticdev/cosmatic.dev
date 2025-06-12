try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse
    from pathlib import Path
    import os, json
    import uvicorn
    from uvicorn import Config, Server
    import api
    import asyncio
    import discord
    import threading
    import requests
    from dotenv import load_dotenv
    import subprocess
    from datetime import datetime
    import pytz
except:
    import os

    input("Missing packages! Click enter to install them?")
    os.system(
        "pip install fastapi uvicorn discord.py requests dotenv pytz 'uvicorn[standard]'"
    )

    import api

    print("Installed missing packages")
    quit()

if not os.path.exists(".env"):
    print(
        "You are missing the .env file!\nPlease create your own or refer to the guide on the git repo detailing the information you need to set this up."
    )
    exit()

if not os.path.exists("static/data/roblox.json"):
    os.makedirs("static/data", exist_ok=True)
    with open("static/data/roblox.json", "w") as f:
        f.write('{"sessions": 0,"playtime": 0,"lastGame": 0,"games": { }}')
    print("No roblox data file found! Wrote a new one.")

if not os.path.exists("steam_app_list.json"):
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v0002/"
    response = requests.get(url)

    if response.status_code == 200:
        x = response.json()
        with open("steam_app_list.json", "w", encoding="utf-8") as file:
            json.dump(x, file, indent=4)

        print("Downloaded steam app list successfully")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

load_dotenv()

app = FastAPI()
static_dir = Path("static")
clients = []


@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    file_location = static_dir / file_path
    if file_location.exists() and file_location.is_file():
        return FileResponse(file_location)
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/")
async def read_index():
    return FileResponse(static_dir / "index.html")


@app.get("/thanks")
async def thanks():
    return FileResponse(static_dir / "thanks.html")


@app.get("/games")
async def sendGames():
    return FileResponse(static_dir / "games.html")


@app.get("/data")
async def sendData():
    return data


@app.get("/robots.txt")
async def send_robots():
    return FileResponse(static_dir / "robots.txt")


@app.get("/favicon.ico")
async def send_favicon():
    return FileResponse(static_dir / "images/icons/favicon.ico")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client disconnected")


async def send_to_all_clients(message):
    for client in clients:
        await client.send_text(json.dumps(message))


def gitInfo():
    result_hash = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    commit_hash = result_hash.stdout.strip()

    result_ts = subprocess.run(
        ["git", "log", "-1", "--format=%ct"],
        capture_output=True,
        text=True,
        check=True,
    )
    timestamp = int(result_ts.stdout.strip())

    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    est = pytz.timezone("US/Eastern")
    est_dt = utc_dt.astimezone(est)

    formatted_date = est_dt.strftime("%Y-%m-%d EST")

    return {
        "git_info": {
            "header": f"{commit_hash} on {formatted_date}",
            "url": f"https://github.com/cosmaticdev/cosmatic.dev/commit/{commit_hash}",
        }
    }


TOKEN = os.getenv("DISCORD_TOKEN")
USER_ID = int(os.getenv("DISCORD_ID"))

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

global data
global params
data = {}

data.update(gitInfo())


@client.event
async def on_message(message):
    # Avoid the bot responding to its own messages
    if message.author == client.user:
        return

    if str(message.channel.id) == os.getenv("DISCORD_CHANNEL"):
        if (message.content) == "restart":
            await message.channel.send("Okay, restarting!")
            os.system("python3 loader.py")


async def fetch_presence():
    await client.wait_until_ready()
    while not client.is_closed():
        for guild in client.guilds:
            member = guild.get_member(USER_ID)
            if member:
                b = {}
                if member.activities:
                    for activity in member.activities:
                        if isinstance(activity, discord.Game):
                            b.update({"playing": [activity.name]})
                            data.update({"playing": [activity.name]})
                        else:
                            data.update({"playing": None})

                        if isinstance(activity, discord.Streaming):
                            continue

                        if isinstance(activity, discord.CustomActivity):
                            b.update({"status": activity.name})
                            data.update({"status": activity.name})
                        else:
                            data.update({"status": None})
                break
        else:
            print("User is not in any mutual servers with the bot.")

        spotifyData = await api.getSpotifyStatus()
        b.update(spotifyData)

        await send_to_all_clients(b)

        await asyncio.sleep(30)


async def roblox_presence():
    with open("static/data/roblox.json") as f:
        data = json.loads(f.read())

    currentExperience = None

    print("Roblox thread started")

    while True:

        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.7",
            "content-type": "application/json",
            "origin": "https://www.roblox.com",
            "priority": "u=1, i",
            "referer": "https://www.roblox.com/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        }

        payload = {"userIds": [os.getenv("ROBLOX_USER_ID")]}

        cookies = {
            ".ROBLOSECURITY": os.getenv("ROBLOX_TOKEN"),
        }

        response = requests.post(
            "https://presence.roblox.com/v1/presence/users",
            headers=headers,
            data=json.dumps(payload),
            cookies=cookies,
        ).json()["userPresences"][0]

        """
        userPresenceType:
        1 - online
        2 - in game

        """

        if response["userPresenceType"] == 2:
            print(
                f"[ ROBLOX ] Playing {response['lastLocation']} (id {response['rootPlaceId']})"
            )
            data["playtime"] += 30

            if str(response["rootPlaceId"]) != currentExperience:
                data["sessions"] += 1
                currentExperience = str(response["rootPlaceId"])
                data["lastGame"] = currentExperience
                if currentExperience in data["games"]:
                    data["games"][currentExperience]["sessions"] += 1
                    data["games"][currentExperience][
                        "playtime"
                    ] += 15  # guestimate time for when they joined, because we can only be accurate to 30 seconds
                else:
                    data["games"].update(
                        {currentExperience: {"sessions": 1, "playtime": 15}}
                    )
            else:
                data["games"][currentExperience]["playtime"] += 30

        elif response["userPresenceType"] == 1:
            currentExperience = None
        else:
            currentExperience = None

        with open("static/data/roblox.json", "w") as f:
            f.write(json.dumps(data, indent=2))

        await asyncio.sleep(30)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.get_channel(int(os.getenv("DISCORD_CHANNEL"))).send("We are so back")
    asyncio.create_task(fetch_presence())
    asyncio.create_task(roblox_presence())  # bundle roblox bot with discord bot


def run_discord_bot():
    """Runs the Discord bot in a separate thread."""
    asyncio.run(client.start(TOKEN))


def start_discord_thread():
    thread = threading.Thread(target=run_discord_bot, daemon=True)
    thread.start()


async def startServer():
    config = Config(
        app=app,
        host="0.0.0.0",
        port=4115,
        log_level="info",
        loop="asyncio",
        reload=False,
        workers=1,
    )
    server = Server(config)
    await server.serve()
    # uvicorn.run(app, host="0.0.0.0", port=4115)
    # when using tunnels, dont use https, otherwise you should include key and cert files


async def runner(interval_seconds, task, *args):
    while True:
        result = await task(*args)
        data.update(result)
        await asyncio.sleep(interval_seconds)


async def main():
    start_discord_thread()

    tasks = [
        asyncio.create_task(startServer()),
        asyncio.create_task(runner(30, api.getSpotifyStatus)),
        asyncio.create_task(runner(60 * 60, api.getXboxGamePlaytime)),
        asyncio.create_task(runner(60 * 60, api.getSteamPlaytime)),
        # asyncio.create_task(runner(60 * 60, api.getUbiPlaytime)),  # temporarily down
        asyncio.create_task(runner(30, api.getRobloxPlaytime)),
        asyncio.create_task(runner(60 * 60, api.getBrawl)),
        asyncio.create_task(runner(60 * 60, api.getValorant)),
        asyncio.create_task(runner(60 * 60, api.getSiege)),
        asyncio.create_task(runner(60 * 60, api.getRocketLeague)),
        asyncio.create_task(
            runner(60 * 60 * 24, api.monkeyType, os.getenv("MT_UNAME"))
        ),
        asyncio.create_task(
            runner(
                60 * 60,
                api.statsFM,
                os.getenv("STATSFM_UNAME"),
                os.getenv("STATSFM_UID"),
            )
        ),
        asyncio.create_task(runner(60 * 10, api.computerStorage)),
        asyncio.create_task(runner(60, api.get_cpu_info)),
        asyncio.create_task(runner(60, api.get_ram_info)),
    ]

    await asyncio.gather(*tasks)


asyncio.run(main())
