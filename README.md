![](assets/long_banner.png)

<br>

#### 🌐 GHunt Online version : https://osint.industries
#### 🐍 Now Python 3.13 compatible !

<br>

![Python minimum version](https://img.shields.io/badge/Python-3.10%2B-brightgreen)

# 😊 Description

GHunt (v2) is an offensive Google framework, designed to evolve efficiently.\
It's currently focused on OSINT, but any use related with Google is possible.

Features :
- CLI usage and modules
- Python library usage
- Fully async
- JSON export
- Browser extension to ease login

# ✔️ Requirements
- Python >= 3.10

# ⚙️ Installation

```bash
$ pip3 install pipx
$ pipx ensurepath
$ pipx install ghunt
```
It will automatically use venvs to avoid dependency conflicts with other projects.

# 💃 Usage

## Login

First, launch the listener by doing `ghunt login` and choose between 1 of the 2 first methods :
```bash
$ ghunt login

[1] (Companion) Put GHunt on listening mode (currently not compatible with docker)
[2] (Companion) Paste base64-encoded cookies
[3] Enter manually all cookies

Choice =>
```

Then, use GHunt Companion to complete the login.

The extension is available on the following stores :\
\
[![Firefox](https://files.catbox.moe/5g2ld5.png)](https://addons.mozilla.org/en-US/firefox/addon/ghunt-companion/)&nbsp;&nbsp;&nbsp;[![Chrome](https://storage.googleapis.com/web-dev-uploads/image/WlD8wC6g8khYWPJUsQceQkhXSlv1/UV4C4ybeBTsZt43U4xis.png)](https://chrome.google.com/webstore/detail/ghunt-companion/dpdcofblfbmmnikcbmmiakkclocadjab)

## Modules

Then, profit :
```bash
Usage: ghunt [-h] {login,email,gaia,drive,geolocate} ...

Positional Arguments:
  {login,email,gaia,drive,geolocate}
    login               Authenticate GHunt to Google.
    email               Get information on an email address.
    gaia                Get information on a Gaia ID.
    drive               Get information on a Drive file or folder.
    geolocate           Geolocate a BSSID.
    spiderdal           Find assets using Digital Assets Links.

Options:
  -h, --help            show this help message and exit
```

📄 You can also use --json with email, gaia, drive and geolocate modules to export in JSON ! Example :

```bash
$ ghunt email <email_address> --json user_data.json
```

**Have fun 🥰💞**

# 🧑‍💻 Developers

📕 I started writing some docs [here](https://github.com/mxrch/GHunt/wiki) and examples [here](https://github.com/mxrch/GHunt/tree/master/examples), feel free to contribute !

To use GHunt as a lib, you can't use pipx because it uses a venv.\
So you should install GHunt with pip :
```bash
$ pip3 install ghunt
```

And now, you should be able to `import ghunt` in your projects !\
You can right now play with the [examples](https://github.com/mxrch/GHunt/tree/master/examples).

# 📮 Details

## Obvious disclaimer

This tool is for educational purposes only, I am not responsible for its use.

## Less obvious disclaimer

This project is under [AGPL Licence](https://choosealicense.com/licenses/agpl-3.0/), and you have to respect it.\
**Use it only in personal, criminal investigations, pentesting, or open-source projects.**

## Thanks

- [novitae](https://github.com/novitae) for being my Python colleague
- All the people on [Malfrats Industries](https://discord.gg/sg2YcrC6x9) and elsewhere for the beta test !
- The HideAndSec team 💗 (blog : https://hideandsec.sh)
- [Med Amine Jouini](https://dribbble.com/jouiniamine) for his beautiful rework of the Google logo, which I was inspired by *a lot*.

## Sponsors

Thanks to these awesome people for supporting me !

<!-- sponsors --><a href="https://github.com/BlWasp"><img src="https://github.com/BlWasp.png" width="50px" alt="BlWasp" /></a>&nbsp;&nbsp;<a href="https://github.com/gingeleski"><img src="https://github.com/gingeleski.png" width="50px" alt="gingeleski" /></a>&nbsp;&nbsp;<!-- sponsors -->

\
You like my work ?\
[Sponsor me](https://github.com/sponsors/mxrch) on GitHub ! 🤗
