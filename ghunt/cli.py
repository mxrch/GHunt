from rich_argparse import RichHelpFormatter

import argparse
from typing import *
import sys
from pathlib import Path


def parse_and_run():
    RichHelpFormatter.styles["argparse.groups"] = "misty_rose1"
    RichHelpFormatter.styles["argparse.metavar"] = "light_cyan1"
    RichHelpFormatter.styles["argparse.args"] = "light_steel_blue1"
    RichHelpFormatter.styles["argparse.prog"] = "light_pink1 bold italic"


    parser = argparse.ArgumentParser(formatter_class=RichHelpFormatter)
    subparsers = parser.add_subparsers(dest="module")

    ### Login module
    parser_login = subparsers.add_parser('login', help="Authenticate GHunt to Google.", formatter_class=RichHelpFormatter)
    parser_login.add_argument('--clean', action='store_true', help="Clear credentials local file.")

    ### Email module
    parser_email = subparsers.add_parser('email', help="Get information on an email address.", formatter_class=RichHelpFormatter)
    parser_email.add_argument("email_address")
    parser_email.add_argument('--json', type=Path, help="File to write the JSON output to.")

    ### Gaia module
    parser_gaia = subparsers.add_parser('gaia', help="Get information on a Gaia ID.", formatter_class=RichHelpFormatter)
    parser_gaia.add_argument("gaia_id")
    parser_gaia.add_argument('--json', type=Path, help="File to write the JSON output to.")

    ### Drive module
    parser_drive = subparsers.add_parser('drive', help="Get information on a Drive file or folder.", formatter_class=RichHelpFormatter)
    parser_drive.add_argument("file_id", help="Example: 1N__vVu4c9fCt4EHxfthUNzVOs_tp8l6tHcMBnpOZv_M")
    parser_drive.add_argument('--json', type=Path, help="File to write the JSON output to.")

    ### Geolocate module
    parser_geolocate = subparsers.add_parser('geolocate', help="Geolocate a BSSID.", formatter_class=RichHelpFormatter)
    geolocate_group = parser_geolocate.add_mutually_exclusive_group(required=True)
    geolocate_group.add_argument("-b", "--bssid", help="Example: 30:86:2d:c4:29:d0")
    geolocate_group.add_argument("-f", "--file", type=Path,  help="File containing a raw request body, useful to put many BSSIDs. ([italic light_steel_blue1][link=https://developers.google.com/maps/documentation/geolocation/requests-geolocation?#sample-requests]Reference format[/link][/italic light_steel_blue1])")
    parser_geolocate.add_argument('--json', type=Path, help="File to write the JSON output to.")

    ### Parsing
    args = None
    if not sys.argv[1:]:
        parser.parse_args(["--help"])
    else:
        for mod in ["email", "gaia", "drive", "geolocate"]:
            if sys.argv[1] == mod and not sys.argv[2:]:
                parser.parse_args([mod, "--help"])

    args = parser.parse_args(args)
    process_args(args)

def process_args(args: argparse.Namespace):
    import asyncio
    match args.module:
        case "login":
            from ghunt.modules import login
            asyncio.run(login.check_and_login(None, args.clean))
        case "email":
            from ghunt.modules import email
            asyncio.run(email.hunt(None, args.email_address, args.json))
        case "gaia":
            from ghunt.modules import gaia
            asyncio.run(gaia.hunt(None, args.gaia_id, args.json))
        case "drive":
            from ghunt.modules import drive
            asyncio.run(drive.hunt(None, args.file_id, args.json))
        case "geolocate":
            from ghunt.modules import geolocate
            asyncio.run(geolocate.main(None, args.bssid, args.file, args.json))