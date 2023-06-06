import paho.mqtt.client as mqtt
import json
import image_analyzer
import time, json, sys, multiprocessing as mp
from driving import *
import geopy.distance
from zone_db import check_zones_not_occupied as obu1_check_zones_not_occupied, update_zones_db_watering as obu1_update_zones_db_watering, get_ID_by_coordinates as obu1_get_ID_by_coordinates
from zones_obu2_db import check_zones_not_occupied as obu2_check_zones_not_occupied, update_zones_db_watering as obu2_update_zones_db_watering, get_ID_by_coordinates as obu2_get_ID_by_coordinates
from zones_obu3_db import check_zones_not_occupied as obu3_check_zones_not_occupied, update_zones_db_watering as obu3_update_zones_db_watering, get_ID_by_coordinates as obu3_get_ID_by_coordinates
from script_obu1 import on_message as obu1_on_message, listen_denms as obu1_listen_denms, find_closest_zone as obu1_find_closest_zone
from script_obu2 import on_message as obu2_on_message, listen_denms as obu2_listen_denms, find_closest_zone as obu2_find_closest_zone
from script_obu3 import on_message as obu3_on_message, listen_denms as obu3_listen_denms, find_closest_zone as obu3_find_closest_zone


obus_cameras = ["static/seca.png", "static/verde2.png", "static/seca3.png", "static/verde1.jpg", "static/seca2.jpg"]  #Scans das cameras das obus -> obus_cameras[0] = scan da camera da zona1, ...
analyze_zones = [[40.63239230194507,-8.6603676549793], [40.63195486065902,-8.661093930263293], [40.63142859277966,-8.660753978842079], [40.63192425397194, -8.659820484340262], [40.63284006630615,-8.660225733927449]]

manager = mp.Manager()
OBU_ZONES = manager.list() #Zonas que já estão a ser analisadas por OBUs


def on_connect(client, userdata, flags, rc):
    if rc==0: 
        print("OBU"+str(client._client_id)[-2]+" connected")
    else: 
        print("bad connection code=",rc)
        
def on_publish(client,userdata,result):
    print("data published \n")

def on_disconnect(client, userdata, flags, rc=0):
    print("OBU"+str(client._client_id)[-2]+": disconnected")

            
def sendDENM(obu, need_water, random_zone):
    f = open('DENM.json')
    denm = json.load(f)
    denm['management']['eventPosition']['latitude'] = random_zone[0]
    denm['management']['eventPosition']['longitude'] = random_zone[1]
    denm['management']['actionID']['sequenceNumber'] += 1
    denm['situation']['eventType']['causeCode'] = need_water
    denm['detectionTime'] = datetime.timestamp(datetime.now())
    denm['referenceTime'] = datetime.timestamp(datetime.now())
    obu.publish("vanetza/in/denm", json.dumps(denm))
    f.close()
    #time.sleep(1)
    
     
def obu_process(broker, id, startDrone_lat, startDrone_lon, lock):
    print("Start Drone LAT ({}) for ID ({}) ".format(startDrone_lat, id))
    print("Start Drone LON ({}) for ID ({}) ".format(startDrone_lon, id))
    
    obu = mqtt.Client(client_id="obu"+str(id))
    obu.on_connect = on_connect
    obu.on_disconnect = on_disconnect
    #obu.on_publish = on_publish
    #obu.on_message = on_message
    
    if broker == "192.168.98.20":
        obu.on_message = obu1_on_message
    elif broker == "192.168.98.30":
        obu.on_message = obu2_on_message
    elif broker == "192.168.98.40":
        obu.on_message = obu3_on_message
    
    obu.loop_start()
    # Connect to the broker ip address
    obu.connect(broker)
    
    # Load the CAMs template
    f = open('CAM.json')
    cam = json.load(f)
    cam['stationID'] = id+1
    
    # Inicialize variables
    reached_zone = False
    lat = startDrone_lat
    lon = startDrone_lon
    still_zones_to_analyze = True
    random_zone = None
    
    while still_zones_to_analyze == True:
        while reached_zone == False:
            # Choose closest zone to analyze
            random_zone = None
            if broker == "192.168.98.20":
                random_zone = obu1_find_closest_zone(lat, lon, id, broker)
            elif broker == "192.168.98.30":
                random_zone = obu2_find_closest_zone(lat, lon, id, broker)
            elif broker == "192.168.98.40":
                random_zone = obu3_find_closest_zone(lat, lon, id, broker)
                
            # Iterate drone to the choosen zone
            if random_zone == None: # Means that there is no more zones do analyse
                break   
            reached_zone, last_lat, last_lon  = iterate_drone_to_zone(lat, lon, cam, obu, id, random_zone, broker, startDrone_lat, startDrone_lon)
            lat = last_lat
            lon = last_lon
        
            # Listen for DENMs with watering information of other OBUS to update their database
            if broker == "192.168.98.20":   #OBU1
                print("-----------------------------------------------------OUVIR DENMS OBU1-----------------------------------------------------")
                obu1_listen_denms(obu)
            elif broker == "192.168.98.30": #OBU2
                print("-----------------------------------------------------OUVIR DENMS OBU2-----------------------------------------------------")
                obu2_listen_denms(obu)
            elif broker == "192.168.98.40": #OBU3
                print("-----------------------------------------------------OUVIR DENMS OBU3-----------------------------------------------------")
                obu3_listen_denms(obu)
        
        print("REACHED_ZONE: {} FOR OBU {}".format(reached_zone, broker))
        if reached_zone == True:
        
            print("----->Starting analyzing the local image<------")
            
            filename = ""
            # Getting filename for the OBU
            if broker == "192.168.98.20":   #OBU1
                filename = obus_cameras[obu1_get_ID_by_coordinates(random_zone)] 
            elif broker == "192.168.98.30": #OBU2
                filename = obus_cameras[obu2_get_ID_by_coordinates(random_zone)] 
            elif broker == "192.168.98.40": #OBU3
                filename = obus_cameras[obu3_get_ID_by_coordinates(random_zone)] 
            
            #filename = obus_cameras[get_ID_by_coordinates(random_zone)]     
            print("FILENAME {} for OBU with ip ({})".format(filename, broker))
            
            time.sleep(1)
            
            green_percent, yellow_percent, brown_percent = image_analyzer.analyse_image(filename)
            need_water = image_analyzer.need_water(green_percent, yellow_percent, brown_percent)
            
            print("OBU with ID {} needs water? {}".format(id, need_water))
            
            # Initialize causeCode to 0
            causeCode = 0   
            if need_water == True:
                causeCode = 1
                
            # Send DENMs with watering information
            print("CAUSE CODE VALUE {} FOR OBU WITH ID {}".format(causeCode, id))
            sendDENM(obu, causeCode, random_zone)
            
            # Update the database with the watering information
            print("OBU with ID {} is updating the watering information".format(id))
            if broker == "192.168.98.20":   #OBU1
                obu1_update_zones_db_watering(random_zone, causeCode)
            elif broker == "192.168.98.30": #OBU2
                obu2_update_zones_db_watering(random_zone, causeCode)
            elif broker == "192.168.98.40": #OBU3
                obu3_update_zones_db_watering(random_zone, causeCode)
                
            
        #print("------------------------------------>CLEAR ZONES AFTER FOR OBU WITH ID {}: {} AND REACHED_ZONE BEFORE {} AND STILL ZONES TO ANALYSE BEFORE <----------------------------------".format(id, json.loads(check_zones_not_occupied()), reached_zone, still_zones_to_analyze))
        if broker == "192.168.98.20":   #OBU1
            if json.loads(obu1_check_zones_not_occupied()) == []:
                still_zones_to_analyze = False
            else:
                reached_zone = False
                #break
        elif broker == "192.168.98.30": #OBU2
            if json.loads(obu2_check_zones_not_occupied()) == []:
                still_zones_to_analyze = False
            else:
                reached_zone = False
                #break
        elif broker == "192.168.98.40": #OBU3
            if json.loads(obu3_check_zones_not_occupied()) == []:
                still_zones_to_analyze = False
            else:
                reached_zone = False
                #break
            
        #print("---------------------------------------------REACHED_ZONE {} AND STILL_ZONES_TO_ANALYZE {} FOR OBU WITH ID {} ----------------------------------".format(reached_zone, still_zones_to_analyze, id))
    
    # #After going to the zone, the OBU will go back to the start point
    #print("----------------------------------------------------")
    #print("LAT: {} | LON: {} and initial LAT {} and initial LON {} for OBU with id ({})".format(lat, lon, startDrone_lat, startDrone_lon, id))
    reached_initialPoint , final_latSimulation, final_lonSimulation = iterate_drone_to_zone(lat, lon, cam, obu, id, [startDrone_lat,startDrone_lon], broker, startDrone_lat, startDrone_lon)        

    print("OBU"+str(id)+": Simulation finished")
    
    obu.loop_stop()
    obu.disconnect()
    
def obu_init_simulation(broker_obus, start_lat, start_lon):
    # Create list of starting coordinates for each drone
    coords_list = [(start_lat, start_lon),
                   (start_lat + 0.00022, start_lon + 0.00022),
                   (start_lat - 0.0002, start_lon - 0.0002)]
    
    process_list = []
    i = 0
    lock = manager.Lock()
    for broker in broker_obus:
        # Get starting coordinates for current drone
        coords = coords_list[i]
        
        obuProcess = mp.Process(target=obu_process, args=[broker[0], broker[1], coords[0], coords[1], lock])
        obuProcess.start()
        process_list.append(obuProcess)
        i = i + 1
        
    for obuProc in process_list:
        obuProc.join()    
        

if(__name__ == '__main__'):
    starter_coordinates = [40.63142812994117,-8.662089161361086]
    obu_init_simulation([("192.168.98.20",1),("192.168.98.30",2),("192.168.98.40",3)], starter_coordinates[0], starter_coordinates[1])
 
