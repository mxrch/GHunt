import httpx
import sys
import json
from geopy.geocoders import Nominatim
from PIL import Image
from pprint import pprint
from lib.utils import *
import lib.youtube as ytb
from io import BytesIO
from datetime import datetime
from lib.photos import gpics
import lib.gmaps as gmaps
from config import cfg
from os.path import isfile

if len(sys.argv) <= 1:
	exit("Please put an email address.")

query = sys.argv[1]

if not isfile(cfg['data_path']):
	exit("Please generate cookies and tokens first.")

cookies = ""
auth = ""
key = ""
with open(cfg['data_path'], 'r') as f:
	out = json.loads(f.read())
	auth = out["auth"]
	hangouts_token = out["keys"]["hangouts"]
	cookies = out["cookies"]

client = httpx.Client(cookies=cookies)

host = "https://people-pa.clients6.google.com"

url = "/v2/people/lookup?key={}".format(hangouts_token)
body = """id={}&type=EMAIL&matchType=EXACT&extensionSet.extensionNames=HANGOUTS_ADDITIONAL_DATA&extensionSet.extensionNames=HANGOUTS_OFF_NETWORK_GAIA_LOOKUP&extensionSet.extensionNames=HANGOUTS_PHONE_DATA&coreIdParams.useRealtimeNotificationExpandedAcls=true&requestMask.includeField.paths=person.email&requestMask.includeField.paths=person.gender&requestMask.includeField.paths=person.in_app_reachability&requestMask.includeField.paths=person.metadata&requestMask.includeField.paths=person.name&requestMask.includeField.paths=person.phone&requestMask.includeField.paths=person.photo&requestMask.includeField.paths=person.read_only_profile_info&requestMask.includeContainer=AFFINITY&requestMask.includeContainer=PROFILE&requestMask.includeContainer=DOMAIN_PROFILE&requestMask.includeContainer=ACCOUNT&requestMask.includeContainer=EXTERNAL_ACCOUNT&requestMask.includeContainer=CIRCLE&requestMask.includeContainer=DOMAIN_CONTACT&requestMask.includeContainer=DEVICE_CONTACT&requestMask.includeContainer=GOOGLE_GROUP&requestMask.includeContainer=CONTACT"""

headers = {
"X-HTTP-Method-Override": "GET",
"Authorization": auth,
"Content-Type": "application/x-www-form-urlencoded",
"Origin": "https://hangouts.google.com"
}

req = client.post(host + url, data=body.format(query), headers=headers, cookies=cookies)
data = json.loads(req.text)
if not "matches" in data:
	exit("[-] This email address does not belong to a Google Account.")
	
#print(data)
geolocator = Nominatim(user_agent="nominatim")
print(f"[+] {len(data['matches'])} account found !")

for user in data["matches"]:
	print("\n------------------------------\n")
	
	
	gaiaID = user["personId"][0]
	email = user["lookupId"]
	infos = data["people"][gaiaID]

	timestamp = int(infos["metadata"]["lastUpdateTimeMicros"][:-3])
	last_edit = datetime.utcfromtimestamp(timestamp).strftime("%Y/%m/%d %H:%M:%S (UTC)")
	
	req = client.get("https://www.google.com/maps/contrib/{}".format(gaiaID))
	gmaps_source = req.text
	
	name = gmaps_source.split("Contributions by")[1].split('"')[0].strip()
	if name :
		print(f"Name: {name}")
	else:
		print("[-] The name can't be found.")
	
	print("\nLast profile edit : {}\n\nEmail : {}\nGoogle ID : {}\n".format(last_edit, email, gaiaID))
	
	profil_pic = infos["photo"][0]["url"]
	isBot = infos["extendedData"]["hangoutsExtendedData"]["isBot"]
	if isBot:
		print("Hangouts Bot : Yes !\n")
	else:
		print("Hangouts Bot : No")
	
	ytb_hunt = False
	if name :
		try:
			services = [x["appType"].lower() if x["appType"].lower() != "babel" else "hangouts" for x in infos["inAppReachability"]]
			if "youtube" in services:
				ytb_hunt = True
			print("\nActivated Google services :")
			print('\n'.join(["- "+x.capitalize() for x in services]))
		except KeyError:
			ytb_hunt = True
			print("\nUnable to fetch connected Google services.")

	if ytb_hunt or cfg["ytb_hunt_always"]:
		req = client.get(profil_pic)
		img = Image.open(BytesIO(req.content))
		hash = image_hash(img)
		data = ytb.get_channels(client, name, cfg)
		if not data:
			print("\nYoutube channel not found.")
		else:
			confidence, channels = ytb.get_confidence(data, name, hash)
			if confidence:
				print(f"\nYoutube channel (confidence => {confidence}%) :")
				for channel in channels:
					print(f"- [{channel['name']}] {channel['profil_url']}")
				possible_usernames = ytb.extract_usernames(channels)
				if possible_usernames:
					print("\nPossible usernames found :")
					for username in possible_usernames:
						print(f"- {username}")
			else:
				print("\nYoutube channel not found.")

	gpics(gaiaID, client, cookies, cfg)
	reviews = gmaps.scrape(gaiaID, client, cookies, cfg)
	if reviews:
		confidence, locations = gmaps.get_confidence(reviews, cfg)
		print(f"\nProbable location (confidence => {confidence}) :")
		loc_names = []
		for loc in locations:
			loc_names.append(f"- {loc['avg']['town']}, {loc['avg']['country']}")
		loc_names = set(loc_names) # We delete duplicates
		for loc in loc_names:
			print(loc)