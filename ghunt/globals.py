from ghunt.objects.utils import TMPrinter
from rich.console import Console
# This file is only intended to serve global variables at a project-wide level.


def init_globals():
    global as_client, config, tmprinter, rc
    as_client = None
    config = None
    tmprinter = TMPrinter()
    rc = Console(highlight=False) # Rich Console