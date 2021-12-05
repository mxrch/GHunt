from ghunt.lib.utils import TMPrinter
# This file is only intended to serve global variables at a project-wide level.


def init_globals():
    global as_client, config, tmprinter
    as_client = None
    config = None
    tmprinter = TMPrinter()