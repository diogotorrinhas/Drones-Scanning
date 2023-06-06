from geographiclib.geodesic import Geodesic

# Function to check if the OBU coordinates are close to some zone coordinates
# proximity_threshold -> is value that indicates if OBU is close to zone, i.e, if proximity_threshold = 5 and OBU is 4 meters away from zone, then it is close to zone
def check_proximity(obu_lat, obu_lon, zone, proximity_threshold):
    geod = Geodesic.WGS84
    result = geod.Inverse(obu_lat, obu_lon, zone[0], zone[1])
    distance = result['s12']
    return distance <= proximity_threshold