import os

from ghunt import globals as gb
from ghunt.apis.vision import VisionHttp

import httpx

from base64 import b64encode
import asyncio


async def detect_face(vision_api: VisionHttp, as_client: httpx.AsyncClient, image_url: str) -> None:
    req = await as_client.get(image_url)
    encoded_image = b64encode(req.content).decode()
    
    are_faces_found = False
    faces_results = None

    for retry in range(5):
        rate_limited, are_faces_found, faces_results = await vision_api.detect_faces(as_client, image_content=encoded_image)
        if not rate_limited:
            break
        await asyncio.sleep(0.5)
    else:
        print("\n[-] Vision API keeps rate-limiting.")
        exit(os.EX_UNAVAILABLE)

    if are_faces_found:
        if len(faces_results.face_annotations) > 1:
            gb.rc.print(f"🎭 {len(faces_results.face_annotations)} faces detected !", style="italic")
        else:
            gb.rc.print(f"🎭 [+] Face detected !", style="italic bold")
    else:
        gb.rc.print(f"🎭 No face detected.", style="italic bright_black")

    return faces_results