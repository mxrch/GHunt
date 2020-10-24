from datetime import datetime

from PIL import ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim

from lib.utils import *


class ExifEater():

    def __init__(self):
        self.devices = {}
        self.softwares = {}
        self.locations = {}
        self.geolocator = Nominatim(user_agent="nominatim")

    def get_GPS(self, img):
        location = ""
        geoaxis = {}
        geotags = {}
        try:
            exif = img._getexif()

            for (idx, tag) in TAGS.items():
                if tag == 'GPSInfo':
                    if idx in exif:
                        for (key, val) in GPSTAGS.items():
                            if key in exif[idx]:
                                geotags[val] = exif[idx][key]

                        for axis in ["Latitude", "Longitude"]:
                            dms = geotags[f'GPS{axis}']
                            ref = geotags[f'GPS{axis}Ref']

                            degrees = dms[0][0] / dms[0][1]
                            minutes = dms[1][0] / dms[1][1] / 60.0
                            seconds = dms[2][0] / dms[2][1] / 3600.0

                            if ref in ['S', 'W']:
                                degrees = -degrees
                                minutes = -minutes
                                seconds = -seconds

                            geoaxis[axis] = round(degrees + minutes + seconds, 5)
                        location = \
                        self.geolocator.reverse("{}, {}".format(geoaxis["Latitude"], geoaxis["Longitude"])).raw[
                            "address"]
        except Exception:
            return ""
        else:
            if location:
                location = sanitize_location(location)
                if not location:
                    return ""
                return f'{location["town"]}, {location["country"]}'
            else:
                return ""

    def feed(self, img):
        try:
            img._getexif()
        except:
            try:
                img._getexif = img.getexif
            except:
                img._getexif = lambda d={}:d
        if img._getexif():
            location = self.get_GPS(img)
            exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
            interesting_fields = ["Make", "Model", "DateTime", "Software"]
            metadata = {k: v for k, v in exif.items() if k in interesting_fields}
            try:
                date = datetime.strptime(metadata["DateTime"], '%Y:%m:%d %H:%M:%S')
                is_date_valid = "Valid"
            except Exception:
                date = None
                is_date_valid = "Invalid"

            if location:
                if location not in self.locations:
                    self.locations[location] = {"Valid": [], "Invalid": []}
                self.locations[location][is_date_valid].append(date)
            if "Make" in metadata and "Model" in metadata:
                if metadata["Model"] not in self.devices:
                    self.devices[metadata["Model"]] = {"Make": metadata["Make"],
                                                       "History": {"Valid": [], "Invalid": []}, "Firmwares": {}}
                self.devices[metadata["Model"]]["History"][is_date_valid].append(date)
                if "Software" in metadata:
                    if metadata["Software"] not in self.devices[metadata["Model"]]["Firmwares"]:
                        self.devices[metadata["Model"]]["Firmwares"][metadata["Software"]] = {"Valid": [],
                                                                                              "Invalid": []}
                    self.devices[metadata["Model"]]["Firmwares"][metadata["Software"]][is_date_valid].append(date)
            elif "Software" in metadata:
                if metadata["Software"] not in self.softwares:
                    self.softwares[metadata["Software"]] = {"Valid": [], "Invalid": []}
                self.softwares[metadata["Software"]][is_date_valid].append(date)

    def give_back(self):
        return self.locations, self.devices

    def output(self):
        bkn = '\n'  # to use in f-strings

        def picx(n):
            return "s" if n > 1 else ""

        def print_dates(dates_list):
            dates = {}
            dates["max"] = max(dates_list).strftime("%Y/%m/%d")
            dates["min"] = min(dates_list).strftime("%Y/%m/%d")
            if dates["max"] == dates["min"]:
                return dates["max"]
            else:
                return f'{dates["min"]} -> {dates["max"]}'

        # pprint((self.devices, self.softwares, self.locations))

        devices = self.devices
        if devices:
            print(f"[+] {len(devices)} device{picx(len(devices))} found !")
            for model, data in devices.items():
                make = data["Make"]
                if model.lower().startswith(make.lower()):
                    model = model[len(make):].strip()
                n = len(data["History"]["Valid"] + data["History"]["Invalid"])
                for validity, dateslist in data["History"].items():
                    if dateslist and (
                            (validity == "Valid") or (validity == "Invalid" and not data["History"]["Valid"])):
                        if validity == "Valid":
                            dates = print_dates(data["History"]["Valid"])
                        elif validity == "Valid" and data["History"]["Invalid"]:
                            dates = print_dates(data["History"]["Valid"])
                            dates += " (+ ?)"
                        elif validity == "Invalid" and not data["History"]["Valid"]:
                            dates = "?"
                        print(
                            f"{bkn if data['Firmwares'] else ''}- {make.capitalize()} {model} ({n} pic{picx(n)}) [{dates}]")
                        if data["Firmwares"]:
                            n = len(data['Firmwares'])
                            print(f"-> {n} Firmware{picx(n)} found !")
                            for firmware, firmdata in data["Firmwares"].items():
                                for validity2, dateslist2 in firmdata.items():
                                    if dateslist2 and ((validity2 == "Valid") or (
                                            validity2 == "Invalid" and not firmdata["Valid"])):
                                        if validity2 == "Valid":
                                            dates2 = print_dates(firmdata["Valid"])
                                        elif validity2 == "Valid" and firmdata["Invalid"]:
                                            dates2 = print_dates(firmdata["Valid"])
                                            dates2 += " (+ ?)"
                                        elif validity2 == "Invalid" and not firmdata["Valid"]:
                                            dates2 = "?"
                                        print(f"--> {firmware} [{dates2}]")

        locations = self.locations
        if locations:
            print(f"\n[+] {len(locations)} location{picx(len(locations))} found !")
            for location, data in locations.items():
                n = len(data["Valid"] + data["Invalid"])
                for validity, dateslist in data.items():
                    if dateslist and ((validity == "Valid") or (validity == "Invalid" and not data["Valid"])):
                        if validity == "Valid":
                            dates = print_dates(data["Valid"])
                        elif validity == "Valid" and data["Invalid"]:
                            dates = print_dates(data["Valid"])
                            dates += " (+ ?)"
                        elif validity == "Invalid" and not data["Valid"]:
                            dates = "?"
                        print(f"- {location} ({n} pic{picx(n)}) [{dates}]")

        softwares = self.softwares
        if softwares:
            print(f"\n[+] {len(softwares)} software{picx(len(softwares))} found !")
            for software, data in softwares.items():
                n = len(data["Valid"] + data["Invalid"])
                for validity, dateslist in data.items():
                    if dateslist and ((validity == "Valid") or (validity == "Invalid" and not data["Valid"])):
                        if validity == "Valid":
                            dates = print_dates(data["Valid"])
                        elif validity == "Valid" and data["Invalid"]:
                            dates = print_dates(data["Valid"])
                            dates += " (+ ?)"
                        elif validity == "Invalid" and not data["Valid"]:
                            dates = "?"
                        print(f"- {software} ({n} pic{picx(n)}) [{dates}]")

        if not devices and not locations and not softwares:
            print("=> Nothing found")
