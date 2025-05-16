import asyncio
import requests
import json


async def run_command(command):
    # Run the command asynchronously
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"Success: {stdout.decode()}")
    else:
        print(f"Error: {stderr.decode()}")


async def main():
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v0002/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        with open("steam_app_list.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print("Downloaded steam app list successfully")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

    await run_command(
        "/usr/bin/git stash push -u -- static/images"
    )  # stash any images that might have been downloaded during runtime and could conflict with images bundled in repo
    await run_command("/usr/bin/git pull")
    await run_command("/usr/bin/sudo reboot")


# Running the async function
asyncio.run(main())
