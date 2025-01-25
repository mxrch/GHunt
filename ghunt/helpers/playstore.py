import httpx


async def app_exists(as_client: httpx.AsyncClient, package: str) -> bool:
    params = {
        "id": package
    }
    req = await as_client.head(f"https://play.google.com/store/apps/details", params=params)
    return req.status_code == 200
