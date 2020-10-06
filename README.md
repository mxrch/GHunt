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
- Public photos (T)
- Phones models (T)
- Phones firmwares (T)
- Installed softwares (T)
- Google Maps reviews
- Possible physical location

The features marked with a **(T)** requiere the target account to have the default setting of `"allow the people you share content with to download your photos and videos. People may still be able to download photos and videos that you've shared with google photos"`. 

Even for a tech-savy person this setting is hard to find, bc of how buried it is, and how much google tried to hide the fact that some albums can be collected regardless of what the account dashboard says:

![0-public_bullshit](https://files.catbox.moe/ufqc9g.jpg)

Here's how to _check if_/_fix the fact that_ you're vulnerable (wich you most likely are):
Go to https://get.google.com/albumarchive/ while logged in with your google account. You will be **automatically** redirected to your correct albumarchive url (https://get.google.com/albumarchive/<YOUR-GOOGLE-ID-HERE>). After that, click the three dots on the top left corner, and click on **setting** 

![how2.jpg](https://files.catbox.moe/ru6kci.jpg)

Then, un-check the only option there:

![setting.jpg](https://files.catbox.moe/b8879l.jpg)


The target account will also be vulnerable if they have ever used **Picasa** linked to their google account in any way, shape or form. For more details on this, read my big-ass comment on issue #10.
Sadly, there doesn't seem to be any option to turn this off, except for begging to the support staff for help.

# Screenshots
<p align="center">
  <img src="https://files.catbox.moe/2zb1z9.png">
</p>

## ⚠️ Warning
- **02/10/2020** : Since few days ago, Google return a 404 when we try to access someone's Google Photos public albums, we can only access it if we have a link of one of his albums.\
Either this is a bug and this will be fixed, either it's a protection that we need to find how to bypass.\
**So, currently, the photos & metadata module will always return "No albums" even if there is one.**
- **02/10/2020** : I found a bypass, I'm working on the patch right now.
- **03/10/2020** : Successfully bypassed. 🕺 (commit 01dc016)

# Installation
- Python 3.6.1+ would be ok. (I developed it with Python 3.8.1)
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
⚠️ If you login to the Google Account from a **different IP** than the one where the cookies were extracted: it will break their validity, so I highly suggest you to make an empty account just for that, or use an account where you never login.

# Ok but where I find these 4 cookies ?
1. Login to accounts.google.com
2. Once connected, open the Dev Tools window and goes to the Storage tab (Shift + F9 on Firefox) (looks like it's called "Application" on Chrome)\
If you don't know how to open it, just right-click somewhere and "Inspect Element"
3. Then you'll find every cookie you need, including the 4 ones.

![cookies](https://files.catbox.moe/9jy200.png)

# Thanks
This tool is based on the Sector's researches on the Google IDs : https://sector035.nl/articles/getting-a-grasp-on-google-ids \
And completed by my own researches.\
If I have the motivation to write a blog post about it, I'll add the link here !
