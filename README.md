![screenshot](https://files.catbox.moe/8a5nzs.png)

![Python minimum version](https://img.shields.io/badge/Python-3.8%2B-brightgreen)

![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/mxrch/ghunt) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/mxrch/ghunt/CodeQL?label=CodeQL)
# Description
GHunt is a modulable OSINT tool designed to evolve over the years, and incorporates many techniques to investigate Google accounts, or objects.\
It currently has **email**, **document**, **youtube** and **gaia** modules.

🔥 **_GHunt is being completely refactored_**, to allow use as a Python library, removing Selenium and Google Chrome dependencies, using definition types and async, to prepare for v2.\
You can track the progress on this project here: https://github.com/mxrch/GHunt/projects/1 \
And on this branch : https://github.com/mxrch/GHunt/tree/refactor \
Please understand that the activity of the master branch will now be reduced, and therefore the pull requests too.

## What can GHunt find ?

🗺️ **Email** module:
- Owner's name
- Gaia ID
- Last time the profile was edited
- Profile picture (+ detect custom picture)
- If the account is a Hangouts Bot
- Activated Google services (YouTube, Photos, Maps, News360, Hangouts, etc.)
- Possible YouTube channel
- Possible other usernames
- Google Maps reviews (M)
- Possible physical location (M)
- Events from Google Calendar (C)
- Organizations (work & education) (A)
- Contact emails (A)
- Contact phones (A)
- Addresses (A)
- ~~Public photos (P)~~
- ~~Phones models (P)~~
- ~~Phones firmwares (P)~~
- ~~Installed softwares (P)~~

🗺️ **Document** module:
- Owner's name
- Owner's Gaia ID
- Owner's profile picture (+ detect custom picture)
- Creation date
- Last time the document was edited
- Public permissions
- Your permissions

🗺️ **Youtube** module:
- Owner's Gaia ID (through Wayback Machine)
- Detect if the email is visible
- Country
- Description
- Total views
- Joined date
- Primary links (social networks)
- All infos accessible by the Gaia module

🗺️ **Gaia** module:
- Owner's name
- Profile picture (+ detect custom picture)
- Possible YouTube channel
- Possible other usernames
- Google Maps reviews (M)
- Possible physical location (M)
- Organizations (work & education) (A)
- Contact emails (A)
- Contact phones (A)
- Addresses (A)

The features marked with a **(P)** require the target account to have the default setting of `Allow the people you share content with to download your photos and videos` on the Google AlbumArchive, or if the target has ever used Picasa linked to their Google account.\
More info [here](https://github.com/mxrch/GHunt#%EF%B8%8F-protecting-yourself).

Those marked with a **(M)** require the Google Maps reviews of the target to be public (they are by default).

Those marked with a **(C)** require user to have Google Calendar set on public (default it is closed).

Those marked with a **(A)** require user to have the additional info set [on profile](https://myaccount.google.com/profile) with privacy option "Anyone" enabled.

# Screenshots
<p align="center">
  <img src="https://files.catbox.moe/2zb1z9.png">
</p>

## 📰 Latest news
- **02/10/2020** : Since a few days ago, Google returns a 404 when we try to access someone's Google Photos public albums, we can only access it if we have a link to one of their albums.\
Either this is a bug and this will be fixed, either it's a protection that we need to find how to bypass.
- **03/10/2020** : Successfully bypassed. 🕺 (commit 01dc016)\
It requires the "Profile photos" album to be public (it is by default)
- **20/10/2020** : Google WebArchive now returns a 404 even when coming from the "Profile photos" album, so **the photos scraping is temporary (or permanently) disabled.** (commit e762543)
- **25/11/2020** : Google now removes the name from the Google Maps profile if the user has 0 reviews (or contributions, even private). I did not find a bypass for the moment, so **all the help in the research of a bypass is appreciated.**
- **20/03/2021** : Successfully bypassed. 🕺 (commit b3b01bc)

# Installation

## Manual installation
- Make sure you have Python 3.8+ installed. (I developed it with Python 3.8.1)
- Some Python modules are required which are contained in `requirements.txt` and will be installed below.

### 1. Chromedriver & Google Chrome
This project uses Selenium and automatically downloads the correct driver for your Chrome version. \
⚠️ So just make sure to have Google Chrome installed.

### 2. Cloning
Open your terminal, and execute the following commands :
```bash
git clone https://github.com/mxrch/ghunt
cd ghunt
```

### 3. Requirements
In the GHunt folder, run:
```bash
python3 -m pip install -r requirements.txt
```
Adapt the command to your operating system if needed.

## Docker
The Docker image is automatically built and pushed to Dockerhub after each push on this repo.\
You can pull the Docker image with:

```
docker pull ghcr.io/mxrch/ghunt
```

Then, you can use the `docker_check_and_gen.sh` and `docker_hunt.sh` to invoke GHunt through Docker, or you can use these commands :

```
docker run -v ghunt-resources:/usr/src/app/resources -ti ghcr.io/mxrch/ghunt check_and_gen.py
docker run -v ghunt-resources:/usr/src/app/resources -ti ghcr.io/mxrch/ghunt ghunt.py
```

# Usage
For the first run and sometime after, you'll need to check the validity of your cookies.\
To do this, run `check_and_gen.py`. \
If you don't have cookies stored (ex: first launch), you will be asked for the required cookies. If they are valid, it will generate the Authentication token and the Google Docs & Hangouts tokens.

Then, you can run the tool like this:
```bash
python3 ghunt.py email larry@google.com
```
```bash
python3 ghunt.py doc https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

⚠️ I suggest you make an empty account just for this or use an account where you never login because depending on your browser/location, re-logging in into the Google Account used for the cookies can deauthorize them.

# Where I get these cookies ?

## Auto (faster)
You can download the GHunt Companion extension that will automate the cookies extraction in 1-click !\
\
[![Firefox](https://ffp4g1ylyit3jdyti1hqcvtb-wpengine.netdna-ssl.com/addons/files/2015/11/get-the-addon.png)](https://addons.mozilla.org/fr/firefox/addon/ghunt-companion/)&nbsp;&nbsp;&nbsp;[![Chrome](https://storage.googleapis.com/web-dev-uploads/image/WlD8wC6g8khYWPJUsQceQkhXSlv1/UV4C4ybeBTsZt43U4xis.png)](https://chrome.google.com/webstore/detail/ghunt-companion/dpdcofblfbmmnikcbmmiakkclocadjab)&nbsp;&nbsp;&nbsp;[![Edge](https://user-images.githubusercontent.com/11660256/111323589-4f4c7c00-866a-11eb-80ff-da7de777d7c0.png)](https://microsoftedge.microsoft.com/addons/detail/ghunt-companion/jhgmpcigklnbjglpipnbnjhdncoihhdj)

You just need to launch the check_and_gen.py file and choose the extraction mode you want to use, between putting GHunt in listening mode, or copy/paste the encoded cookies in base64.

## Manual
1. Be logged-in to myaccount.google.com
2. After that, open the Dev Tools window and navigate to the Network tab\
If you don't know how to open it, just right-click anywhere and click "Inspect Element".
3. Go to myaccount.google.com, and in the browser requests, select the GET on "accounts.google.com" that gives a 302 redirect
4. Then you'll find every cookie you need in the "cookies" section.

![cookies](https://files.catbox.moe/15j8pg.png)

# 🛡️ Protecting yourself
Regarding the collection of metadata from your Google Photos account:

Given that Google shows **"X require access"** on [your Google Account Dashboard](https://myaccount.google.com/intro/dashboard), you might imagine that you had to explicitly authorize another account in order for it to access your pictures; but this is not the case.\
Any account can access your AlbumArchive (by default):

![account-dashboard](https://files.catbox.moe/ufqc9g.jpg)

Here's how to check and fix the fact that you're vulnerable (which you most likely are):\
Go to https://get.google.com/albumarchive/ while logged in with your Google account. You will be **automatically** redirected to your correct albumarchive URL (`https://get.google.com/albumarchive/YOUR-GOOGLE-ID-HERE`). After that, click the three dots on the top left corner, and click on **setting** 

![three-dots-setting](https://files.catbox.moe/ru6kci.jpg)

Then, uncheck the only option there:

![setting](https://files.catbox.moe/b8879l.jpg)


On another note, the target account will **also** be vulnerable if they have ever used **Picasa** linked to their Google account in any way, shape or form. For more details on this, read ItsIgnacioPortal's comment on [issue #10](https://github.com/mxrch/GHunt/issues/10).\
For now, the only (known) solution to this is to delete the Picasa albums from your AlbumArchive. 

# Thanks
This tool is based on [Sector's research on Google IDs](https://sector035.nl/articles/getting-a-grasp-on-google-ids) and completed by my own as well.\
If I have the motivation to write a blog post about it, I'll add the link here !
- Palenath (for the name bypass)
