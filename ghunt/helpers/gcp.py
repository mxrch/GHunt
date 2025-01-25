import dns.message
import dns.asyncquery
import httpx

from ghunt.objects.base import GHuntCreds
from ghunt.apis.identitytoolkit import IdentityToolkitHttp


async def is_cloud_functions_panel_existing(project_id: str):
    q = dns.message.make_query(f"endpoints.{project_id}.cloud.goog", "A")
    r = await dns.asyncquery.tcp(q, "8.8.8.8")
    return bool(r.answer)

async def project_nb_from_key(as_client: httpx.AsyncClient, ghunt_creds: GHuntCreds, api_key: str, fallback=True) -> str|None:
    identitytoolkit_api = IdentityToolkitHttp(ghunt_creds)
    found, project_config = await identitytoolkit_api.get_project_config(as_client, api_key)
    if found:
        return project_config.project_id
    if fallback:
        # Fallback on fetching the project number by producing an error
        import json
        import re
        req = await as_client.get("https://blobcomments-pa.clients6.google.com/$discovery/rest", params={"key": api_key})
        try:
            data = json.loads(req.text)
            return re.findall(r'\d{12}', data["error"]["message"])[0]
        except Exception:
            pass
    return None