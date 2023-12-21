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

    ### Web module
    parser_drive = subparsers.add_parser('web', help="Launch web app.")
    parser_drive.add_argument('--host', type=str, help="Host. Defaults to 0.0.0.0.", default='0.0.0.0')
    parser_drive.add_argument('--port', type=int, help="Port. Defaults to 8080.", default=8080)
    parser_drive.add_argument('--api', action='store_true', help="API only. No front-end.")

    ### Parsing
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    process_args(args)

def process_args(args: argparse.Namespace):
    import anyio
    match args.module:
        case "login":
            from ghunt.modules import login
            anyio.run(login.check_and_login, None, args.clean)
        case "email":
            from ghunt.modules import email
            anyio.run(email.hunt, None, args.email_address, args.json)
        case "gaia":
            from ghunt.modules import gaia
            anyio.run(gaia.hunt, None, args.gaia_id, args.json)
        case "drive":
            from ghunt.modules import drive
            anyio.run(drive.hunt, None, args.file_id, args.json)
        case "web":
            from ghunt.modules import web
            anyio.run(web.hunt, None, args.host, args.port, args.api)
