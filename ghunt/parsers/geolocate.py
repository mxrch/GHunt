from ghunt.objects.apis import Parser
from ghunt.objects.base import Position

from typing import *


class GeolocationResponse(Parser):
    def __init__(self):
        self.accuracy: int = 0
        self.location: Position = Position()

    def _scrape(self, base_model_data: dict[str, any]):
        self.accuracy = base_model_data.get("accuracy")

        location = base_model_data.get("location")
        self.location.longitude = location.get("lng")
        self.location.latitude = location.get("lat")