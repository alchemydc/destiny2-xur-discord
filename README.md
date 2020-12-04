# destiny2-xur-discord

## Overview
Xur is an NPC in Bungie's MMO shooter [Destiny2](https://www.bungie.net/7/en/Destiny/BeyondLight])
which is a space magic infused descendant of Halo.  
Xur visits only for a few days a week, landing on Fridays and 
selling different exotic weapons and armor from a random location.

This script Post Xur's location and inventory to a Discord webhook,
and is designed to be run from cron or as a cloud function.

![alt text](https://alchemydc-public.s3-us-west-1.amazonaws.com/xur.png)

## Requirements
* Python3
* Discord server with an activated [webhook integration](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
* [Bungie API key](https://github.com/Bungie-net/api/wiki/Bungie.net-Application-Portal)

## Installation (Linux or OSX)
1. Create a separate user named 'xur'
```console
sudo adduser xur
```
2. Change to the 'xur' user
```console
sudo su - xur
```

3. Clone the repo
```console
git clone https://github.com/alchemydc/destiny2-xur-discord.git
```

4. Create and activate a python virtual environment
(recommended to keep deps separate from system python)
```console
python -m virtualenv . && ./bin/activate
```

5. Install python dependencies
(requests for making the https API calls, python-dotenv for keeping secrets out of the source)
 ```console
 python -m pip install -r requirements.txt
 ```

## Configuration
1. Copy the environment template
```console
cp .env-template .env
```

2. Populate the .env file with your Bungie API key and Discord webhook URL


## Test run
```console
python3 xur.py
```

## Schedule it to run automatically
Xur comes on Fridays after the daily reset, so it's convenient to have this script run right after that. If Xur has something you don't, then go see him!

1. Make xur wrapper bash script and python script executable
```console
chmod u+x xur.sh xur.py
```
2. Install crontab to run script automatically
```console
/usr/bin/crontab xur.crontab
```

## Troubleshooting
If things aren't working as expected, ensure that your Bungie API key and Discord webhook are set correctly.

If the script works when run directly, but fails when run by cron, check to ensure your home directory is correct in xur.sh,
and that env vars are being properly imported by python-dotenv.

