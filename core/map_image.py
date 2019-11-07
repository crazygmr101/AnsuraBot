import core.url_utils

class Map_Imager:
    def __init__(self):
        self.image_endpoint = "http://www.mapquestapi.com/staticmap/v4/getmap"
        self.key = "uAer9Ura3n27HwSC3RnSWTqPxTgtg2X1"

    def get_static_url(self, *, lat, lon, size=200, zoom=2):
        return core.url_utils.build(self.image_endpoint, center=str(lat)+","+str(lon),
                                    size=str(size)+","+str(size), zoom=str(zoom), key=self.key,
                                    pois="PLACE,"+str(lat)+","+str(lon))