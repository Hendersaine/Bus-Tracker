import csv
import xml.etree.ElementTree as et
import os

class Stop():   #Make a class to contain each stop
    def __init__(self):
        self.stopID = ""
        self.name = ""
        self.lat = 0
        self.long = 0
    def addID(self, id, commonName):
        self.stopID = id
        self.name = commonName
    def addPosition(self, position):
        self.lat = position[0]
        self.long = position[1]

#The basic 
base_dir = os.path.dirname(os.path.abspath(__file__))
dataLocation = os.path.join(base_dir, 'data')
stopsCSV = os.path.join(base_dir, "stops.csv")
routesCSV = os.path.join(base_dir, "routes.csv")
linksCSV = os.path.join(base_dir, "links.csv")

totalStops = {}
totalRoutes = []
totalLinks = []

files = [
    os.path.join(dataLocation, f)
    for f in os.listdir(dataLocation)
    if f.endswith(".xml")
]
for fileLocation in files:
    file = et.parse(fileLocation)
    root = file.getroot()
    stops = []
    coordinates = {}

    for stop in root.findall(".//{http://www.transxchange.org.uk/}AnnotatedStopPointRef"):
        s = Stop()
        s.addID(stop.find("{http://www.transxchange.org.uk/}StopPointRef").text, stop.find("{http://www.transxchange.org.uk/}CommonName").text)
        stops.append(s)

    stopPoints = root.findall(".//{http://www.transxchange.org.uk/}RouteLink")
    for stop in stops:
        for points in stopPoints:
            point = points.find("{http://www.transxchange.org.uk/}From/{http://www.transxchange.org.uk/}StopPointRef")

            if point != None and point.text == stop.stopID:
                location = points.find(".//{http://www.transxchange.org.uk/}Location")
                if location != None:
                    lat = location.find("{http://www.transxchange.org.uk/}Latitude")
                    lon = location.find("{http://www.transxchange.org.uk/}Longitude")
                    if lat.text != None and lon.text != None:
                        stop.addPosition([lat.text, lon.text])
                    else:
                        stops.remove(stop)
                    break
                else:
                    stops.remove(stop)
                    break
    
    id = root.find(".//{http://www.transxchange.org.uk/}LineName").text
    operator = root.find(".//{http://www.transxchange.org.uk/}OperatorShortName").text
    totalRoutes.append([id, operator])
    print(id)

    for stop in stops:
       if stop.lat != 0 and stop.long != 0:
        totalStops[stop.stopID] = [stop.stopID, stop.name, stop.lat, stop.long]
        totalLinks.append([id, stop.stopID])
    

with open(stopsCSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["stopID", "name", "lat", "lon"])
    writer.writerows(totalStops.values())

with open(routesCSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["routeID", "operator"])
    writer.writerows(totalRoutes)

with open(linksCSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["routeID", "stopID"])
    writer.writerows(totalLinks)