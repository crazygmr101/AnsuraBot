import requests
import json

class Geolocation:
    def __init__(self):
        self.API = "GW598KKQJWTQ"

    def timezone(self,lat,long):
        url = "http://api.timezonedb.com/v2.1/get-time-zone"
        url += "?key=" + self.API + "&format=json&by=position&lat=" + str(lat) + "&lng=" + str(long)
        r = requests.get(url)
        return r.json()

    def locate(self, place):
        url = "https://nominatim.openstreetmap.org/search/" + place + "?format=json"
        r = requests.get(url)
        loc = r.json()[0]
        return [loc["lat"], loc["lon"], loc["display_name"]]

    def tzplace(self, place):
        loc = self.locate(place)
        return [self.timezone(loc[0],loc[1])["formatted"],loc[2]]