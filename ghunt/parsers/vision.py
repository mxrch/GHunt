from ghunt.objects.apis import Parser

from typing import *


class VisionPosition(Parser):
    def __init__(self):
        self.x: int = None
        self.y: int = None
        self.z: int = None
    
    def _scrape(self, position_data: Dict[str, int]):
        self.x = position_data.get("x")
        self.y = position_data.get("y")
        self.z = position_data.get("z")

class VisionLandmark(Parser):
    def __init__(self):
        self.type: str = ""
        self.position: VisionPosition = VisionPosition()

    def _scrape(self, landmark_data: Dict[str, any]):
        self.type = landmark_data["type"]
        self.position._scrape(landmark_data["position"])

class VisionVertice(Parser):
    def __init__(self):
        self.x: int = None
        self.y: int = None

    def _scrape(self, vertice_data: Dict[str, int]):
        self.x = vertice_data.get("x")
        self.y = vertice_data.get("y")

class VisionVertices(Parser):
    def __init__(self):
        self.vertices: List[VisionVertice] = []

    def _scrape(self, vertices_data: List[Dict[str, int]]):
        for vertice_data in vertices_data:
            vertice = VisionVertice()
            vertice._scrape(vertice_data)
            self.vertices.append(vertice)

class VisionFaceAnnotation(Parser):
    def __init__(self):
        self.bounding_poly: VisionVertices = VisionVertices()
        self.fd_bounding_poly: VisionVertices = VisionVertices()
        self.landmarks: List[VisionLandmark] = []
        self.roll_angle: int = 0,
        self.pan_angle: int = 0,
        self.tilt_angle: int = 0,
        self.detection_confidence: int = 0,
        self.landmarking_confidence: int = 0,
        self.joy_likelihood: str = "",
        self.sorrow_likelihood: str = "",
        self.anger_likelihood: str = "",
        self.surprise_likelihood: str = "",
        self.under_exposed_likelihood: str = "",
        self.blurred_likelihood: str = "",
        self.headwear_likelihood: str = ""

    def _scrape(self, face_data: Dict[str, any]):
        if (vertices_data := face_data.get("boundingPoly", {}).get("vertices")):
            self.bounding_poly._scrape(vertices_data)
        if (vertices_data := face_data.get("fdBoundingPoly", {}).get("vertices")):
            self.fd_bounding_poly._scrape(vertices_data)
        if (landmarks_data := face_data.get("landmarks")):
            for landmark_data in landmarks_data:
                landmark = VisionLandmark()
                landmark._scrape(landmark_data)
                self.landmarks.append(landmark)
        self.roll_angle = face_data.get("rollAngle")
        self.pan_angle = face_data.get("panAngle")
        self.tilt_angle = face_data.get("tiltAngle")
        self.detection_confidence = face_data.get("detectionConfidence")
        self.landmarking_confidence = face_data.get("landmarkingConfidence")
        self.joy_likelihood = face_data.get("joyLikelihood")
        self.sorrow_likelihood = face_data.get("sorrowLikelihood")
        self.anger_likelihood = face_data.get("angerLikelihood")
        self.surprise_likelihood = face_data.get("surpriseLikelihood")
        self.under_exposed_likelihood = face_data.get("underExposedLikelihood")
        self.blurred_likelihood = face_data.get("blurredLikelihood")
        self.headwear_likelihood = face_data.get("headwearLikelihood")

class VisionFaceDetection(Parser):
    def __init__(self):
        self.face_annotations: List[VisionFaceAnnotation] = []

    def _scrape(self, vision_data: Dict[str, any]):
        for face_data in vision_data["faceAnnotations"]:
            face_annotation = VisionFaceAnnotation()
            face_annotation._scrape(face_data)
            self.face_annotations.append(face_annotation)