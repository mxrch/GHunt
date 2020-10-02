![screenshot](https://files.catbox.moe/8a5nzs.png)

# Description
GHunt is an OSINT tool to extract a lot of informations of someone's Google Account email.

It can currently extract :
- Owner's name
- Last time the profile was edited
- Google ID
- If the account is an Hangouts Bot
- Activated Google services (Youtube, Photos, Maps, News360, Hangouts, etc.)
- Possible Youtube channel
- Possible other usernames
- Public photos
- Phones models
- Phones firmwares
- Installed softwares
- Google Maps reviews
- Possible physical location

# Screenshots
<p align="center">
  <img src="https://files.catbox.moe/2zb1z9.png">
</p>

## ⚠️ Warning
**02/10/2020** : Since few days ago, Google return a 404 when we try to access someone's Google Photos public albums, we can only access it if we have a link of one of his albums.\
Either this is a bug and this will be fixed, either it's a protection that we need to find how to bypass.\
**So, currently, the photos & metadata module will always return "No albums" even if there is one.**

# Installation
- Python 3.6+ would be ok. (I developed it with Python 3.8.1)
- These Python modules are required (we'll install them after):
```
geopy
httpx
selenium-wire
selenium
imagehash
pillow
python-dateutil
```

## 1. Chromedriver & Google Chrome
This project uses Selenium, so you'll need to download the chromedriver here : https://chromedriver.chromium.org/downloads \
And put it in the GHunt folder. Be sure it's called "chromedriver.exe" or "chromedriver".\
Also, be sure to have Google Chrome installed.

## 2. Requirements
In the GHunt folder, do this:
```bash
python -m pip install -r requirements.txt
```
Adapt the command with your operating system if needed.

# Usage
For the first usage and sometimes after, you'll need to check the validity of your cookies.\
To do this, launch `check_and_gen.py`.\
If you don't have cookies stored (ex: first launch) it will ask you the 4 needed cookies, enter them and if they are valid, it will generate the Authentification token, and the Google Docs & Hangouts tokens.

Then, you can run the tool like this :
```bash
python hunt.py myemail@gmail.com
```
⚠️ Every time you re-login to the Google Account used for the cookies, it will break their validity, so I highly suggest you to make an empty account just for that, or use an account where you never login.

# Ok but where I find these 4 cookies ?
1. Login to accounts.google.com
2. Once connected, open the Developer pop-up and goes to the Storage tab (Shift + F9) (looks like it's called "Application" on Chrome)\
If you don't know how to open it, just right-click somewhere and "Inspect Element"
3. Then you'll find every cookie you need, including the 4 ones.

![cookies](https://files.catbox.moe/9jy200.png)

# Thanks
This tool is based on the Sector's researches on the Google IDs : https://sector035.nl/articles/getting-a-grasp-on-google-ids \
And completed by my own researches.\
If I have the motivation to write a blog post about it, I'll add the link here !
