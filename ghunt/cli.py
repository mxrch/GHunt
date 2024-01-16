import argparse
from typing import *
import sys


def parse_and_run():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="module")

    ### Login module
    parser_login = subparsers.add_parser('login', help="Authenticate GHunt to Google.")
    parser_login.add_argument('--clean', action='store_true', help="Clear credentials local file.")

    ### Email module
    parser_email = subparsers.add_parser('email', help="Get information on an email address.")
    parser_email.add_argument("email_address")
    parser_email.add_argument('--json', type=str, help="File to write the JSON output to.")

    ### Gaia module
    parser_gaia = subparsers.add_parser('gaia', help="Get information on a Gaia ID.")
    parser_gaia.add_argument("gaia_id")
    parser_gaia.add_argument('--json', type=str, help="File to write the JSON output to.")

    ### Drive module
    parser_drive = subparsers.add_parser('drive', help="Get information on a Drive file or folder.")
    parser_drive.add_argument("file_id", help="Example: 1N__vVu4c9fCt4EHxfthUNzVOs_tp8l6tHcMBnpOZv_M")
    parser_drive.add_argument('--json', type=str, help="File to write the JSON output to.")

    ### Parsing
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
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