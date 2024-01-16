import httpx

class AsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _merge_cookies(self, cookies: dict):
        """Don't save the cookies in the client."""
        return cookies