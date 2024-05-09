import sys


def main():
    version = sys.version_info
    if version < (3, 10):
        print("error, wrong Python version")
        sys.exit(1)

    from ghunt.cli import parse_and_run

    # from ghunt.helpers.banner import show_banner
    # from ghunt.helpers.utils import show_version

    # show_banner()
    # show_version()
    parse_and_run()

