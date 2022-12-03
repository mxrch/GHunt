import httpx


async def is_email_registered(as_client: httpx.AsyncClient, email: str) -> bool:
    """
        Abuse the gxlu endpoint to check if any email address
        is registered on Google. (not only gmail accounts)
    """
    req = await as_client.get(f"https://mail.google.com/mail/gxlu", params={"email": email})
    return "Set-Cookie" in req.headers