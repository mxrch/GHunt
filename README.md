![screenshot](https://files.catbox.moe/8a5nzs.png)

# Description
GHunt is an OSINT tool to extract information from a Google Account using an email.

It can currently extract:
- Owner's name
- Last time the profile was edited
- Google ID
- If the account is a Hangouts Bot
- Activated Google services (YouTube, Photos, Maps, News360, Hangouts, etc.)
- Possible YouTube channel
- Possible other usernames
- Public photos
- Associated phone models
- Associated phone firmwares
- Installed software
- Google Maps reviews
- Possible physical location

# Screenshots
<p align="center">
  <img src="https://files.catbox.moe/2zb1z9.png">
</p>

# Installation
- Make sure you have Python 3.6.1+ installed. Version 3.8.1 is preferred, however.
- These Python modules are required (we'll install them later):
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
This project uses Selenium, so you'll need to download [chromedriver](https://chromedriver.chromium.org/downloads). \
After you do that, put it in the GHunt folder. Make sure it's called "chromedriver.exe" or "chromedriver".\
Also, be sure to have Google Chrome installed.

## 2. Requirements
In the GHunt folder, run:
```bash
python -m pip install -r requirements.txt
```
Adapt the command to your operating system if needed.

# Usage
For the first run and sometimes after, you'll need to check the validity of your cookies.\
To do this, run `check_and_gen.py`. \
If you don't have cookies stored (ex: first launch), you will be asked for the four required cookies. If they are valid, it will generate the Authentication token and the Google Docs & Hangouts tokens.

Then, you can run the tool like this:
```bash
python hunt.py myemail@gmail.com
```
⚠️ Every time you log in to the Google Account used for the cookies, it will deauthorize them. So, I highly suggest you to make an empty account just for that, or use an account where you never log in.

# Where I find these four cookies?
1. Log in to accounts.google.com
2. After that, open the Dev Tools window and navigate to the Storage tab (Shift + F9 on Firefox) (It's called "Application" on Chrome)\
If you don't know how to open it, just right-click anywhere and click "Inspect Element".
3. Then you'll find every cookie you need, including the four.

![cookies](https://files.catbox.moe/9jy200.png)

# Thanks
This tool is based on [Sector's research on Google IDs](https://sector035.nl/articles/getting-a-grasp-on-google-ids) and completed by my own as well.\
If I have the motivation to write a blog post about it, I'll add the link here!
