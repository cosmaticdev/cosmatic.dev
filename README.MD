<div align="center">
  <img src="https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg">
  <img src="https://forthebadge.com/images/badges/works-on-my-machine.svg">
  <img src="https://forthebadge.com/images/badges/powered-by-energy-drinks.svg">
</div>

There's no more API keys or passwords in the source code, so you know what that means...
# GOING PUBLIC!

Heya hi and welcome to the source code for my personal website [cosmatic.dev](https://cosmatic.dev)

This project pulls data from xbox, steam, roblox, ubisoft, spotify, and more, the whole shebang

Look at the code if you must, if it causes a heart attack I plead the 5th

This project is designed to be run on a stand-alone linux raspberry pi, and may need to be changed to work elsewhere

Please note that this project is not finished, there is still more stuff in the works:
- mobile view supported
- fix ubisoft tracking
- epic games tracking (if possible?)
- & maybe more?

## Rundown on data collected:
- Steam playtime (& game icons)
- Xbox playtime and achievements (& game icons)
- Ubisoft playtime for specified games
- Tracks Roblox playtime live
- Tracks Spotify top streamed songs (via stats.fm)
- Tracks live Spotify streams (via last.fm)
- Monkeytype profile data
- Local server conditions (storage, ram, cpu, wifi speed, etc)
- Current discord profile status
- Current roblox activity status
- Tracks ranks for VALORANT, R6, Brawl Stars, and Rocket League
- & maybe more if im forgetting

## Functionality that exists but is not used:
- Leetcode profile tracking
- Brave stats tracking (ads blocked, time saved, etc)
- Live R6 profile info via ubisoft

# The Processes:
Heres what happpens in the main server file; basically everything it runs

1.) Main uvicorn server
- hosts the website
- used for returning all pages, api's, images, etc

2.) Live update websocket
- Updates all clients whenever needed
- Allows for clients to reflect data in real time

3.) Discord bot
- allows for the server to be updated and restarted remotely
- reads user discord status and activity

4.) Roblox Tracker
- watches a roblox profile to record what games they are playing
- records playtime for a user across roblox

5.) Last.fm Tracker (for live spotify tracking)
- live data for what song a user is streaming

6.) All data collection threads
- each data collection process is launched in a looping asyncio task
- allows for different types of data to be collected at different time intervals and without conflicting with each other

And the stuff that runs in the background of the RPI:

1.) Cloudflared tunnel
- tunnels traffic from the internet to our pi and vice verse

2.) Auto updater scripts
- launches all the processes and updates on boot or command

# Hosting this yourself on a RPI
### While you can run this on a different setup, you will need to figure out any potential flaws on your own
This is quite long, so I will segment it for yall you make it a bit easier:
- [Preparing your domain](#preparing-your-domain)
- [Preparing your secrets file](#preparing-your-secrets-file)
- [Preparing your RPI](#preparing-your-rpi)
- [Setting up the cloudflared tunnels](#setting-up-the-cloudflare-tunnels)
- [Enabling autostart](#enabling-autostart)

What you need:
- A Raspberry Pi (I used a 4b, although most should work fine)
- A storage device (to save the RPI's OS to)
- A wifi or ethernet connection, depending on what your RPI supports
- A connector to mount your storage device on your computer

# Preparing your domain
Step one, you need to have a domain. Anything works, grab a fancy one or a cheap one, it doesn't matter.
I'd recomend steering clear of godaddy, but otherwise go ham on finding a registrar (although porkbun and namecheap are my favs)

Once you have a domain, go [add your site to cloudflare](https://developers.cloudflare.com/fundamentals/setup/manage-domains/add-site/).
- While you don't *need* to, it's always really beneficial to explore the cloudflare settings for your site and enabling all the awesome features they have to speed stuff up and to keep everything protected and safe
- Basically every page in the domain manager has something cool to check out so just click through the whole sidebar to see it all

Once your domain is on cloudflare and is ready to go then you can head on over to the next section

# Preparing your RPI
Before you start, make sure to grab a copy of the RPI Imager from [raspberrypi.com/software/](https://www.raspberrypi.com/software/) if you don't have it already

Once you have the imager, open it, and select your device from the "choose device" button (I used a RPI 4, but most should work)

Then, click choose OS, then navigate to "other". You will need to find the "Raspberry Pi OS Lite (64 Bit)" option and click it
- other distros might (/probably) would work, but this guide may not satisfy them completely

Finally, mount the storage device you intend to use for your RPI (SD Card, hard drive, etc) and select that as the storage option.
- PLEASE BE VERY CAREFUL, SELECTING THE WRONG DRIVE MAY WIPE YOUR DATA BY INSTALLING THE OS IN THE WRONG PLACE

Hit next, but do NOT continue further, there is some quality of life OS Customization we can do here.

Click to edit the os customization, and change the following:
- hostname; set it to something memorable and representative of the pi
- username and password; something you can remember easily
- your wireless network details (if using wifi)
- your local timezone and keyboard layout
- click services at the top and enable SSH (I recommend password authentication, but you can do you)

Click save, click yes, and start the installation. This might take a while.

Once your installation is done, plug your storage device into your raspberry pi and plug the pi in to power. At this point there are two ways you can interact with your pi:
- Over a HDMI display; you can plug a keyboard and display into your pi and use it like a normal pc if you'd like
- Over SSH (aka interact with the pi using your own pc)
    - Use your router to find the ip of your pi, then connect to it by typing "ssh ```[your pi username]```@```[pi local ip]```" (you may be asked to fingerprint, type yes)
    - enter your password and once confirmed you should be able to write to the pi's terminal

Please note that since it is the first boot it might be quite a while before your pi is set up and ready to be interacted with it. Just plug it in and go watch a show then come back in like thirty minutes or something to be sure its good.

Once you are in to your pi's terminal, we can start doing stuff. 

Starting off with updates & needed installs, enter these line by line in to your pi, there may be confirmations or time delays between each one, be patient.
```
sudo apt update
sudo apt upgrade
sudo apt install curl lsb-release
sudo apt install python3
sudo apt install git-all
```
Then, we need to do some stuff with a headless chromium browser so we can grab the dependencies for that like so:
```
(paste the following in one chunk, do not split it up line by line)
sudo apt install -y \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgtk-3-0
```
Awesome, stuff should be updated and installed. We can grab the code now
```
git clone https://github.com/cosmaticdev/cosmatic.dev
```
And then make a python venv and opening it
```
cd cosmatic.dev
python3 -m venv .venv
source .venv/bin/activate
```
Then finally giving the code a trial run. This is going to crash, we havn't installed packages yet, but it should prompt us to install automatically!
```
python3 server.py
```
When it asks you to install packages please click enter and it should do it automatically.

Once we have our packages we need to add all our private data to use with the apis

# Preparing your secrets file
While you are still in your project folder, please type the following into the terminal
```touch .env```
This will create a secrets file which you can edit by typing
```sudo nano .env```
Please edit the contents of this file to contain the following:

```py
# DISCORD
DISCORD_TOKEN=""
DISCORD_ID=
DISCORD_CHANNEL=""
# Getting a discord bot token- https://www.writebots.com/discord-bot-token/
# Getting a discord user id- https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID#h_01HRSTXPS5H5D7JBY2QKKPVKNA
# Getting a discord channel id- https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID#h_01HRSTXPS5FMK2A5SMVSX4JW4E


# UBISOFT
UBI_EMAIL=""
UBI_PW=""
# it's okay if your account has 2fa enabled, this will still work (lol?)

# STEAM
STEAM_API_KEY=""
STEAM_USER_ID=
# Get steam api key- https://steamcommunity.com/dev/apikey
# Steam SteamID can be found on your steam page or find your profile on https://steamdb.info/calculator/
# The SteamID is an integer

# ROBLOX
ROBLOX_USER_ID=""
ROBLOX_TOKEN=""
# Your roblox user id is the number found in your profile url
# You will need to use the network tab or a cookie manager to find your token. It will be named ".ROBLOSECURITY"
# ***PLEASE DO NOT USE YOUR MAIN ACCOUNT, USE AN ALT'S COOKIE***

# MONKEYTYPE
MT_UNAME=""

# STATS.FM
STATSFM_UNAME=""
STATSFM_UID=""
# you will need to lurk through the chrome dev tools network tab to find the stats.fm UID

# LAST.FM
LASTFM_AUTH=""
LASTFM_USERNAME=""
# getting a last.fm auth key- https://www.last.fm/api#getting-started

# BRAWL STARS
BRAWL_STARS_TAG=""
# this is the string found under your profile pic on your profile (please include the # in the string)

# TRACKER.GG
RL_USERNAME=""
SIEGE_USERNAME=""
VAL_USERNAME=""
# go to tracker.gg and make sure your profile comes up under the names you write here

# TRUE ACHIEVEMENTS
TA_USERNAME=""
TA_GAMERID=""
TA_GAMERTOKEN=""
TA_TRUE_GAMING_IDENTITY=""
# you will need to look trough the network tab to find these details
```

Once everything is entered please save, write, and exit the file.

Run the start command one more time and the server should run as intented.

To visit the site, navigate to http://[```YOUR_DEVICE_IP```]:4115 on a device on the same network as the rpi

# Setting up the cloudflare tunnels
Your site is only local right now, that's not ideal! Here's how to get it online on the domain you got earlier:

Open a second terminal window on your pc. Please SSH in to the pi again, *without shutting down the server on the first window*

The run the following commands one-by-one to set up the tunnel:
```
curl -L https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-archive-keyring.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee  /etc/apt/sources.list.d/cloudflared.list
sudo apt update
sudo apt install cloudflared
cloudflared tunnel login
```

Running the last command will prompt you to long into your cloudflare account. Please do so, and if prompted please select the domain you plan to use to host this site

More commands to run now:

Make ```TUNNELNAME``` what you want your tunnel to be called locally. Don't forget this name
```
cloudflared tunnel create TUNNELNAME
```
A new tunnel id will be retuned. Copy this and paste it somewhere safe.

Run the following, where ```TUNNELNAME``` is your tunnels name and ```DOMAINNAME``` is the domain you wish to use (without https:// or http://)
```
cloudflared tunnel route dns TUNNELNAME DOMAINNAME
```

Then, run the tunnel using
```
cloudflared tunnel run --url localhost:4115 TUNNELNAME
```
If you have manually changed the port from 4115 within the code you will need to change this. If you haven't touched anything you should be good to go

Head to your website and see if your site loads. If you get an error then something is wrong and you need to backtrack. Make sure that the python server is still running in the other window, if not then go back and run it again.

If it works, hit ```CONTROL+C``` to stop the tunnel. You can do the same for the python server if you'd like.

# Enabling autostart
So it runs, that's cool, but it's manual and boring, lame. If you would like your server to update and run automatically here's how you can make that happen:

Head to the root directoy of your pi, and enter the following command
```
sudo nano ~/.cloudflared/config.yml
```
You will need to enter the following, and fill in some of your own info:
```
tunnel: [TUNNELNAME]
credentials-file: /home/[USERNAME]/.cloudflared/[UUID].json

ingress:
    - hostname: [HOSTNAME]
      service: [PROTOCOL]://localhost:[PORT]
    - service: http_status:404
```
- ```[TUNNELNAME]``` = whatever name you set earlier
- ```[USERNAME]``` = the username of your local pi user, probably whatever you used to login with
- ```[UUID]``` = the long tunnel id you got earlier that I told you to save
- ```[PROTOCOL]``` = "http" or "https" (you should probably do https)
- ```[PORT]``` = port your python server runs on; its 4115 by default but if you changed it please set it to whatever you changed it to

Hit CONTROL+X and then Y and then ENTER to save and write the file

Enter the following commands line-by-line:
```
sudo cloudflared --config ~/.cloudflared/config.yml service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

Cloudflared should now start automatically whenever your pi is booted!

Now, we need to make it so the python server runs automatically (and pulls the latest data from git!)

Enter the following command to create a new service
```
sudo nano /etc/systemd/system/server.service
```
Paste the following into the file, filling in any data when needed
```
[Unit]
Description=Server Runner
After=network-online.target
Wants=network-online.target


[Service]
Type=simple
User=YOUR_LOCAL_USER_NAME
WorkingDirectory=/home/YOUR_LOCAL_USER_NAME/cosmatic.dev
ExecStartPre=/bin/sleep 15
ExecStart=/home/YOUR_LOCAL_USER_NAME/cosmatic.dev/.venv/bin/python /home/YOUR_LOCAL_USER_NAME/cosmatic.dev/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```


Then enable it to start on boot:
```
sudo systemctl daemon-reexec
sudo systemctl enable server.service
```

Lets give it a little test run. We are going to start the service and then watch the logs in real time.
```
sudo systemctl start server.service
journalctl -u server.service -f
```
If you see some errors then you might have a problem and need to backtrack.

If not then you should be good to go! When your device boots it will pull the lastest data and then start the server automatically so you won't need to manually update it.

Type '''sudo reboot''' and give your pi some time to start back up. Check and see if the website populates automatically
- if it *doesn't*, you can use the following commands to open the logs to see what errors might be occuring
```
journalctl -u server.service
```

And thats about it! Thanks for reading, I hope you find some cool uses for my project :)

If you ever need help and want to reach out I'm available every day on my discord @cosmatic_ 
