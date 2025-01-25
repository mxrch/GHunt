from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.vision import VisionFaceDetection

import httpx

from typing import *
import inspect
import json

        
class VisionHttp(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers
        
        base_headers = {
            "X-Origin": "https://explorer.apis.google.com"
        }

        headers = {**headers, **base_headers}

        self.hostname = "content-vision.googleapis.com"
        self.scheme = "https"

        self._load_api(creds, headers)

    async def detect_faces(self, as_client: httpx.AsyncClient, image_url: str = "", image_content: str = "",
                            data_template="default") -> Tuple[bool, bool, VisionFaceDetection]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "POST",
            data_type = "json", # json, data or None
            authentication_mode = None, # sapisidhash, cookies_only, oauth or None
            require_key = "apis_explorer", # key name, or None
            key_origin = "https://content-vision.googleapis.com"
        )
        self._load_endpoint(endpoint)

        base_url = "/v1/images:annotate"

        # image_url can cause errors with vision_api, so we prefer using image_content
        # See => https://cloud.google.com/vision/docs/detecting-faces?#detect_faces_in_a_remote_image

        data_templates = {
            "default": {
                "requests":[
                    {
                        "features": [
                            {
                                "maxResults":100,
                                "type":"FACE_DETECTION"
                            }
                        ],
                        "image": {}
                    }
                ]
            }
        }

        if not data_templates.get(data_template):
            raise GHuntParamsTemplateError(f"The asked template {data_template} for the endpoint {endpoint.name} wasn't recognized by GHunt.")

        # Inputs checks
        if image_url and image_content:
            raise GHuntParamsInputError("[Vision API faces detection] image_url and image_content can't be both put at the same time.")
        elif not image_url and not image_content:
            raise GHuntParamsInputError("[Vision API faces detection] Please choose at least one parameter between image_url and image_content.")

        if data_template == "default":
            if image_url:
                data_templates["default"]["requests"][0]["image"] = {
                    "source": {
                        "imageUri": image_url
                    }
                }
            elif image_content:
                data_templates["default"]["requests"][0]["image"] = {
                    "content": image_content
                }

        data = data_templates[data_template]
        req = await self._query(endpoint.name, as_client, base_url, data=data)

        rate_limited = req.status_code == 429 # API Explorer sometimes rate-limit because they set their DefaultRequestsPerMinutePerProject to 1800

        vision_face_detection = VisionFaceDetection()
        if rate_limited:
            return rate_limited, False, vision_face_detection

        # Parsing
        data = json.loads(req.text)
        if not data["responses"][0]:
            return rate_limited, False, vision_face_detection
        
        vision_data = data["responses"][0]
        vision_face_detection._scrape(vision_data)

        return rate_limited, True, vision_face_detection