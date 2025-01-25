from typing import *

import httpx
from ghunt.helpers.utils import get_httpx_client
from ghunt.helpers import auth
from ghunt.objects.base import GHuntCreds, SmartObj


# class Session(SmartObj):
#     def __init__(self, client: httpx.AsyncClient = None) -> None:
#         self.creds: GHuntCreds = None
#         self.client: httpx.AsyncClient = client or get_httpx_client()

#     @staticmethod
#     async def new(client: httpx.AsyncClient = None, authentify=False) -> "Session":
#         cls = Session(client=client)

#         if authentify:
#             cls.creds = await auth.load_and_auth(client)
#         return cls