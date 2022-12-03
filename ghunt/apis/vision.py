from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI
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

        self.authentication_mode = None # sapisidhash, cookies_only, oauth or None
        self.require_key = "apis_explorer" # key name, or None
        self.key_origin = "https://content-vision.googleapis.com"

        self._load_api(creds, headers)

    async def detect_faces(self, as_client: httpx.AsyncClient, image_url: str = "", image_content: str = "",
                            params_template="default") -> Tuple[bool, bool, VisionFaceDetection]:
        endpoint_name = inspect.currentframe().f_code.co_name

        # image_url can cause errors with vision_api, so we prefer using image_content
        # See => https://cloud.google.com/vision/docs/detecting-faces?#detect_faces_in_a_remote_image

        verb = "POST"
        base_url = "/v1/images:annotate"
        data_type = "json" # json, data or None
        params_templates = {
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

        if not params_templates.get(params_template):
            raise GHuntParamsTemplateError(f"The asked template {params_template} for the endpoint {endpoint_name} wasn't recognized by GHunt.")

        # Inputs checks
        if image_url and image_content:
            raise GHuntParamsInputError("[Vision API faces detection] image_url and image_content can't be both put at the same time.")
        elif not image_url and not image_content:
            raise GHuntParamsInputError("[Vision API faces detection] Please choose at least one parameter between image_url and image_content.")

        if image_url:
            params_templates["default"]["requests"][0]["image"] = {
                "source": {
                    "imageUri": image_url
                }
            }
        elif image_content:
            params_templates["default"]["requests"][0]["image"] = {
                "content": image_content
            }

        self._load_endpoint(endpoint_name)
        req = await self._query(as_client, verb, endpoint_name, base_url, None, params_templates[params_template], data_type)
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