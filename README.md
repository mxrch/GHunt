![screenshot](https://files.catbox.moe/8a5nzs.png)

![Python minimum version](https://img.shields.io/badge/Python-3.7%2B-brightgreen)

![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/mxrch/ghunt) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/mxrch/ghunt/CodeQL?label=CodeQL)
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
- Public photos (P)
- Phones models (P)
- Phones firmwares (P)
- Installed softwares (P)
- Google Maps reviews (M)
- Possible physical location (M)
- Events from Google Calendar (C)

The features marked with a **(P)** require the target account to have the default setting of `Allow the people you share content with to download your photos and videos` on the Google AlbumArchive, or if the target has ever used Picasa linked to their Google account.\
More info [here](https://github.com/mxrch/GHunt#%EF%B8%8F-protecting-yourself).

Those marked with a **(M)** require the Google Maps reviews of the target to be public (they are by default).

Those marked with a **(C)** requires user to have Google Calendar set on public (default it is closed) 

# Screenshots
<p align="center">
  <img src="https://files.catbox.moe/2zb1z9.png">
</p>

## 📰 Latest news
- **02/10/2020** : Since few days ago, Google return a 404 when we try to access someone's Google Photos public albums, we can only access it if we have a link of one of his albums.\
Either this is a bug and this will be fixed, either it's a protection that we need to find how to bypass.
- **03/10/2020** : Successfully bypassed. 🕺 (commit 01dc016)\
It requires the "Profile photos" album to be public (it is by default)
- **20/10/2020** : Google WebArchive now returns a 404 even when coming from the "Profile photos" album, so **the photos scraping is temporary (or permanently) disabled.** (commit e762543)

# Installation

## Docker
The Docker image is automatically built and push on Dockerhub after each push on this repo.\
You can pull the Docker image with:

```
docker pull mxrch/ghunt
```

Then, any of the scripts can be invoked through:

```
docker run -v ghunt-resources:/usr/src/app/resources -ti mxrch/ghunt check_and_gen.py
docker run -v ghunt-resources:/usr/src/app/resources -ti mxrch/ghunt hunt.py <email_address>
```

## Manual installation
- Make sure you have Python 3.7+ installed. (I developed it with Python 3.8.1)
- Some Python modules are required which are contained in `requirements.txt` and will be installed below.

### 1. Chromedriver & Google Chrome
This project uses Selenium and automatically downloads the correct driver for your Chrome version. \
⚠️ So just make sure to have Google Chrome installed.

### 2. Requirements
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
Regarding the collection of metadata from your Google Photos account:

Given that Google shows **"X require access"** on [your Google Account Dashboard](https://myaccount.google.com/intro/dashboard), you might imagine that you had to explicitly authorize another account in order for it to access your pictures; but this is not the case.\
Any account can access your AlbumArchive (by default):

![account-dashboard](https://files.catbox.moe/ufqc9g.jpg)

Here's how to check and fix the fact that you're vulnerable (which you most likely are):\
Go to https://get.google.com/albumarchive/ while logged in with your Google account. You will be **automatically** redirected to your correct albumarchive URL (`https://get.google.com/albumarchive/YOUR-GOOGLE-ID-HERE`). After that, click the three dots on the top left corner, and click on **setting** 

![three-dots-setting](https://files.catbox.moe/ru6kci.jpg)

Then, un-check the only option there:

![setting](https://files.catbox.moe/b8879l.jpg)


On another note, the target account will **also** be vulnerable if they have ever used **Picasa** linked to their Google account in any way, shape or form. For more details on this, read PinkDev1's comment on [issue #10](https://github.com/mxrch/GHunt/issues/10).\
For now, the only (known) solution to this is to delete the Picasa albums from your AlbumArchive. 

# Thanks
This tool is based on [Sector's research on Google IDs](https://sector035.nl/articles/getting-a-grasp-on-google-ids) and completed by my own as well.\
If I have the motivation to write a blog post about it, I'll add the link here !
