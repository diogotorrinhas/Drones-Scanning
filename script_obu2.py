import paho.mqtt.client as mqtt
import json
from utils import check_proximity
from zones_obu2_db import *
import geopy.distance

analyze_zones = [[40.63239230194507,-8.6603676549793], [40.63195486065902,-8.661093930263293], [40.63142859277966,-8.660753978842079], [40.63192425397194, -8.659820484340262], [40.63284006630615,-8.660225733927449]]

def on_message(client, userdata, message):
    topic = message.topic
    #print("TOPIC FOR OBU "+str(client._client_id)[-2]+" : "+topic)
    
    if topic == "vanetza/out/cam":
        m_decode=str(message.payload.decode("utf-8","ignore"))
        cam = json.loads(m_decode)
        #print("CAMs: ", cam)
        
        ip_received = client._host #Ip address of the OBU that received the CAM
        #print("CAMs RECEIVED ON {} -> {}: ".format(ip_received, cam))
        ip = ""
        brk = ""
        lat = cam['latitude']
        lon = cam['longitude']
        
        if cam['stationID'] == 2:
            ip = "192.168.98.20"
            brk = "obu1"
        elif cam['stationID'] == 3:
            ip = "192.168.98.30"
            brk = "obu2"
        elif cam['stationID'] == 4:
            ip = "192.168.98.40"
            brk = "obu3"
        
        print("SCRIPT FOR OBU2 -> LAT: "+str(lat)+"| LON: "+str(lon)+ " FROM OBU ("+str(ip)+", "+str(brk)+") | RECEIVER: "+str(ip_received))
        
        for zone in analyze_zones:
            proximity = check_proximity(lat, lon, zone, 15) #15 meters of proximity
            #print("PROXIMITY FOR OBU "+str(client._host)+" : "+str(proximity))
            if proximity == True:
                update_zones_db(ip, brk, zone[0], zone[1]) #Update DB with the zone that the OBU will analyze when reach it
                break
            
    elif topic == "vanetza/out/denm":
        print("-----------------------------------------------------OUVIR DENM OBU2-----------------------------------------------------")
        m_decode=str(message.payload.decode("utf-8","ignore"))
        denm = json.loads(m_decode)
        print("DENMs RECEIVED ON {} -> {}: ".format(client._host, denm))
        
        if denm['stationID'] == 2:
            ip = "192.168.98.20"
            update_zones_db_watering_by_ip(ip, denm['fields']['denm']['situation']['eventType']['causeCode'], denm['fields']['denm']['management']['eventPosition']['latitude'], denm['fields']['denm']['management']['eventPosition']['longitude'])
        elif denm['stationID'] == 3:
            ip = "192.168.98.30"
            update_zones_db_watering_by_ip(ip, denm['fields']['denm']['situation']['eventType']['causeCode'], denm['fields']['denm']['management']['eventPosition']['latitude'], denm['fields']['denm']['management']['eventPosition']['longitude'])
        elif denm['stationID'] == 4:
            ip = "192.168.98.40"
            update_zones_db_watering_by_ip(ip, denm['fields']['denm']['situation']['eventType']['causeCode'], denm['fields']['denm']['management']['eventPosition']['latitude'], denm['fields']['denm']['management']['eventPosition']['longitude'])
    
    
def listen_cams(obu):
    obu.subscribe("vanetza/out/cam")
    
def update_zones_db_with_actualCoordinatesOfOBU2(lat, lon, ip, brk):
    for zone in analyze_zones:
        proximity = check_proximity(lat, lon, zone, 15) #15 meters of proximity
        #print("PROXIMITY FOR OBU "+str(client._host)+" : "+str(proximity))
        if proximity == True:
            update_zones_db(ip, brk, zone[0], zone[1]) #Update DB with the zone that the OBU will analyze when reach it
            break    
    
def listen_denms(obu):
    obu.subscribe("vanetza/out/denm")

def check_if_zone_occupied(ip, zone, initial_lat, initial_lon):
    occupied = False
    clear = False
    if ip == "192.168.98.30":   #OBU2
        zones_clear = check_zones_not_occupied() # json object with the zones that are not occupied
        zones_clear = json.loads(zones_clear)
        #clear = False
        #print('ZONES NOT OCCUPIED!!!!!!!: {} | OBU WITH IP {}'.format(zones_clear, ip))
        for info_zone_clear in zones_clear:
            zone_clear = [info_zone_clear["latitudeZone"], info_zone_clear["longitudeZone"]]
            #print('ZONE {} == ZONE CLEAR {} FOR OBU1'.format(zone, zone_clear))
            if zone == zone_clear:
                clear = True
                break
           
    #Se a zona não for as coordenadas iniciais de uma das OBUs, retornamos a zona associada à OBU atual        
    if zone != [initial_lat, initial_lon]:  
        associated_zone_to_this_obu = {}
        if ip == "192.168.98.30":   #OBU2
            associated_zone_to_this_obu = return_zone_associated_to_OBU(zone) 
            associated_zone_to_this_obu = json.loads(associated_zone_to_this_obu)
        
        if clear == False and associated_zone_to_this_obu["ip"] != ip:
            occupied = True
    
    return occupied

def find_closest_zone(obu_lat, obu_lon, id, broker):
    #Returns the closest zone to the given coordinates of the OBU, it can return the same zone for different OBUs
    zonesToAnalyse = []
    clear_zones = {} #Json object with the info about the clear zones
    if broker == "192.168.98.30":   #OBU2
        clear_zones = check_zones_not_occupied() 
        clear_zones = json.loads(clear_zones)
        
    #print("--------------------------------->CLEAR ZONES FOR OBU WITH ID "+str(id)+": "+str(clear_zones) +"<---------------------------------")
    for info_zone in clear_zones:
        zone = [info_zone["latitudeZone"], info_zone["longitudeZone"]]
        zonesToAnalyse.append(zone)
        
    closest_zone_distance = float('inf')
    closest_zone = None
    #print("ZONES TO ANALYSE: ", zonesToAnalyse)
    for zone in zonesToAnalyse:
        current_distance = geopy.distance.distance((obu_lat, obu_lon), (zone[0], zone[1])).m
        if current_distance < closest_zone_distance:
            closest_zone_distance = current_distance
            closest_zone = zone
    return closest_zone 