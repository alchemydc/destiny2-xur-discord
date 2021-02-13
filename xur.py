#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# invoke with python3 -O xur.py to omit debug output

# constants
xurAPIuri = 'https://paracausal.science/xur/current.json'   # props to @nev_rtheless for this fine endpoint :)
bungoAPIbaseURI = 'https://www.bungie.net/Platform/Destiny2/'
bungoXurURI = 'Vendors/?components=402'
bungoItemURI = 'Manifest/DestinyInventoryItemDefinition/'
iconBaseURI = 'https://www.bungie.net/'
itemSearchPath = 'https://www.light.gg/db/search/'
BANNED_HASHES=[3875551374,2125848607]
XUR_AVATAR = 'https://cdn.vox-cdn.com/uploads/chorus_image/image/59217189/Xur_Destiny_2_.0.jpg'

import requests
import json
import urllib.parse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# create a custom requests object, modifying the global module throws an error
http = requests.Session()
assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
http.hooks["response"] = [assert_status_hook]

# read secrets from env vars
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
bungoAPIkey = os.getenv('BUNGIE-API-KEY')
discordWebhookURI = os.getenv('DISCORD-WEBHOOK')


def getData(url, http_headers={}):
  response = http.get(url, headers = http_headers)
  #print(response)
  return(response.json())
  
def parseLocationData(data):
  if data == None:
      print("Xur is nowhere to be found. Try again tomorrow!")
      return("not_here")
  else:
      #print("got data from the API")
      location = { 
          'planet': data['placeName'],
          'place' : data['locationName']
      }
      return(location)

def discordAlert(data, uri):
    #print("Sending alert data %s to discord at %s" % (data, uri))
    http_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        "username": 'Xur, Agent of the Nine',
        "avatar_url": XUR_AVATAR,
        "content": data
    }
    response = http.post(uri, headers=http_headers, json=payload)
    #print(response)

def discordEmbed(itemName, itemTypeAndTier, itemIcon, itemScreenshot, itemFlavor, itemType, uri):
    #print("Sending embed to discord at %s with params \nitemName = %s\n, itemTypeAndTier = %s\n, itemIcon = %s\n, itemScreenshot = %s, itemFlavor = %s\n, itemType = %s\n" % (uri, itemName, itemTypeAndTier, itemIcon, itemScreenshot, itemFlavor, itemType))
    searchURI = (itemSearchPath + "?q=%s" % urllib.parse.quote_plus(itemName))
    http_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        "username": 'Xur, Agent of the Nine',
        "avatar_url": XUR_AVATAR,

        "embeds": [
            {
                "author": {
                    "name": itemName,
                    "url": searchURI,
                    "icon_url": itemIcon,
                },            
                "title": itemTypeAndTier,
                "url": searchURI,
                "description": itemFlavor,
                "color":  15258703,
                "thumbnail": {
                    "url": itemIcon
                },
            }
        ]
    }
    response = http.post(uri, headers=http_headers, json=payload)
    #print(response.content)

def getInventory(uri):
    http_headers = {
      'x-api-key': bungoAPIkey
    }
    xurInventory = getData(uri, http_headers)
    saleItems = xurInventory['Response']['sales']['data']['2190858386']['saleItems']
    itemHashes = []
    for item in saleItems.values():
        itemHash = item['itemHash']
        if itemHash not in BANNED_HASHES: # exotic cipher & engrams have bogus data.
            itemHashes.append(itemHash)
    return(itemHashes)

def getManifestData(basePath, itemHashes):
    http_headers = {
      'x-api-key': bungoAPIkey
    }
    manifestData = []
    for hash in itemHashes:
        #print(hash)
        uri = basePath +str(hash)
        #print(uri)
        itemData = getData(uri, http_headers)
        #print(itemData)
        manifestData.append(itemData)
    return(manifestData)

def parseItemData(itemData):
    parsedItemData = []
    for item in itemData:
        #print(item)
        parsedItem = {
            'name'       : item['Response']['displayProperties']['name'],
            'flavor'     : item['Response']['flavorText'],
            'icon'       : iconBaseURI + item['Response']['displayProperties']['icon'],
            'typeAndTier': item['Response']['itemTypeAndTierDisplayName'],
            'screenshot' : iconBaseURI + item['Response']['screenshot'],
            'type'       : 'weapon' if item['Response']['itemType'] == 3 else 'armor'
        }
        parsedItemData.append(parsedItem)
    return(parsedItemData)

def main():
    print("Contacting Xur location API")
    data = getData(xurAPIuri)
    print("Parsing results") if __debug__ else Null
    location = parseLocationData(data)
    if location == "not_here":
        print("Xur isn't here, skipping the alert") 
        sys.exit(0)
    else:
        alertMsg = f"I am on {location['planet']} in {location['place']}."
        print(alertMsg)
        discordAlert(alertMsg, discordWebhookURI)
    print("Contacting Xur inventory API")
    itemHashes = getInventory(bungoAPIbaseURI+bungoXurURI)
    #print(itemHashes)
    itemData = getManifestData(bungoAPIbaseURI+bungoItemURI,itemHashes)
    #print(itemData)
    parsedItemData = parseItemData(itemData)
    #print(parsedItemData)
    print("Sending inventory to Discord")
    for item in parsedItemData:
        #print(item)
        discordEmbed(item['name'], item['typeAndTier'], item['icon'], item['screenshot'], item['flavor'], item['type'], discordWebhookURI)

if __name__ == "__main__":
    main()