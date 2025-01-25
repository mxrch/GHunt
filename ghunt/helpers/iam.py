import httpx
import asyncio

from ghunt.objects.base import GHuntCreds
from ghunt.apis.mobilesdk import MobileSDKPaHttp
from ghunt.knowledge import iam
from ghunt.helpers.utils import chunkify

from typing import *


async def test_all_permissions(as_client: httpx.AsyncClient, ghunt_creds: GHuntCreds, project_identifier: str):

    async def test_permission(as_client: httpx.AsyncClient, mobilesdk_api: MobileSDKPaHttp, limiter: asyncio.Semaphore,
                                project_identifier: str, permissions: List[str], results: List[str]):
        async with limiter:
            _, perms = await mobilesdk_api.test_iam_permissions(as_client, project_identifier, permissions)
            results.extend(perms)

    mobilesdk_api = MobileSDKPaHttp(ghunt_creds)
    results: List[str] = []
    limiter = asyncio.Semaphore(20)
    tasks = []
    for perms_chunk in chunkify(iam.permissions, 100): # Max 100 permissions per request
        tasks.append(test_permission(as_client, mobilesdk_api, limiter, project_identifier, perms_chunk, results))
    await asyncio.gather(*tasks)

    results = list(set(results))
    print(results)