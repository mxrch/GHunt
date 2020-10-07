![screenshot](https://files.catbox.moe/8a5nzs.png)

# Description
GHunt is an OSINT tool to extract information from any Google Account using an email.

It can currently extract:
- Owner's name
- Last time the profile was edited
- Google ID
- If the account is a Hangouts Bot
- Activated Google services (YouTube, Photos, Maps, News360, Hangouts, etc.)
- Possible YouTube channel
- Possible other usernames
- Public photos (T)
- Phones models (T)
- Phones firmwares (T)
- Installed softwares (T)
- Google Maps reviews
- Possible physical location

The features marked with a **(T)** requiere the target account to have the default setting of `"allow the people you share content with to download your photos and videos. People may still be able to download photos and videos that you've shared with google photos"`, OR, have used **Picasa™** linked to their Google™ account.

# Screenshots
<p align="center">
  <img src="https://files.catbox.moe/2zb1z9.png">
</p>

## 📰 Latest news
- **02/10/2020** : Since few days ago, Google return a 404 when we try to access someone's Google Photos public albums, we can only access it if we have a link of one of his albums.\
Either this is a bug and this will be fixed, either it's a protection that we need to find how to bypass.
- **03/10/2020** : Successfully bypassed. 🕺 (commit 01dc016)\
It requires the "Profile photos" album to be public (it is by default)

# Installation

## Docker

You can build the Docker image with:

```
docker build -t ghunt .
```

Any of the scripts can be invoked through:

```
docker run -v $(pwd)/resources:/usr/src/app/resources -ti ghunt check_and_gen.py
docker run -v $(pwd)/resources:/usr/src/app/resources -ti ghunt hunt.py <email_address>
```

## Manual installation
- Make sure you have Python 3.6.1+ installed. (I developed it with Python 3.8.1)
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
⚠️ Be sure to have Google Chrome installed, and that Google Chrome and chromedriver have the same version.

## 2. Requirements
In the GHunt folder, run:
```bash
python -m pip install -r requirements.txt
```
Adapt the command to your operating system if needed.

# Usage
For the first run and sometimes after, you'll need to check the validity of your cookies.\
To do this, run `check_and_gen.py`. \
If you don't have cookies stored (ex: first launch), you will be asked for the 4 required cookies. If they are valid, it will generate the Authentication token and the Google Docs & Hangouts tokens.

Then, you can run the tool like this:
```bash
python hunt.py myemail@gmail.com
```

⚠️ I suggest you make an empty account just for this or use an account where you never login because depending on your browser/location, re-logging in into the Google Account used for the cookies can deauthorize them.

# Where I find these 4 cookies ?
1. Log in to accounts.google.com
2. After that, open the Dev Tools window and navigate to the Storage tab (Shift + F9 on Firefox) (It's called "Application" on Chrome)\
If you don't know how to open it, just right-click anywhere and click "Inspect Element".
3. Then you'll find every cookie you need, including the 4 ones.

![cookies](https://files.catbox.moe/9jy200.png)

# 🛡️ Protecting yourself
Regarding the collection of metadata from your Google Photos™ account:

Even for a tech-savy person this setting is hard to find, because of how buried it is, and how much Google™ tried to hide the fact that some albums can be collected regardless of what the account dashboard says:

![0-public_bullshit](https://files.catbox.moe/ufqc9g.jpg)

Here's how to _check if_/_fix the fact that_ you're vulnerable (wich you most likely are):
Go to https://get.google.com/albumarchive/ while logged in with your Google™ account. You will be **automatically** redirected to your correct albumarchive URL (https://get.google.com/albumarchive/<YOUR-GOOGLE-ID-HERE>). After that, click the three dots on the top left corner, and click on **setting** 

![how2.jpg](https://files.catbox.moe/ru6kci.jpg)

Then, un-check the only option there:

![setting.jpg](https://files.catbox.moe/b8879l.jpg)


The target account will also be vulnerable if they have ever used **Picasa™** linked to their Google™ account in any way, shape or form. For more details on this, read my comment on issue #10.
Sadly, there doesn't seem to be any option to turn this off, except for begging the support staff for help (un-tested).

# Thanks
This tool is based on [Sector's research on Google IDs](https://sector035.nl/articles/getting-a-grasp-on-google-ids) and completed by my own as well.\
If I have the motivation to write a blog post about it, I'll add the link here!
