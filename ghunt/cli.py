import argparse


def parse_and_run():
    parser = argparse.ArgumentParser()

    parser.add_argument("module")

    args = parser.parse_args()
    process_args(args)

def process_args(args: argparse.Namespace):
    if args.module == "login":
        from ghunt.modules import login
        login.check_and_login()