import os
import sys


def main():
    version = sys.version_info
    if (version < (3, 10)):
        print('[-] GHunt only works with Python 3.10+.')
        print(f'Your current Python version : {version.major}.{version.minor}.{version.micro}')
        sys.exit(os.EX_SOFTWARE)

    from ghunt.cli import parse_and_run
    from ghunt.helpers.banner import show_banner
    from ghunt.helpers.utils import show_version

    show_banner()
    show_version()
    print()
    parse_and_run()