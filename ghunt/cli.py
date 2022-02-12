import argparse

import trio


def parse_and_run():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="module")

    ### Login module
    parser_login = subparsers.add_parser('login')

    ### Email module
    parser_email = subparsers.add_parser('email')
    parser_email.add_argument("email_address")

    ### Gaia module
    parser_gaia = subparsers.add_parser('gaia')
    parser_gaia.add_argument("gaia_id")

    ### Parsing
    args = parser.parse_args()
    process_args(args)

def process_args(args: argparse.Namespace):
    if args.module == "login":
        from ghunt.modules import login
        login.check_and_login()

    if args.module == "email":
        from ghunt.modules import email
        trio.run(email.hunt, None, args.email_address)

    if args.module == "gaia":
        from ghunt.modules import gaia
        trio.run(gaia.hunt, None, args.gaia_id)