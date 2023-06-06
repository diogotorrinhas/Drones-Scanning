import sqlite3 as sql
import json

#TODO: CRIAR UMA FUNÇÃO PARA RETORNAR UM ARRAY COM AS COORDENADAS DAS ZONAS NA BASE DE DADOS

def create_zones_obu2_table():
    db = sql.connect('zones2.db')

    db.execute('''drop table if exists zones2''')
    db.execute('''create table zones2(
            ip text,
            broker text,
            water text,
            latitude_zone real,
            longitude_zone real,
            id integer primary key
            );''')
    
    #Id is the index of the analyse_zones list
    db.execute('''insert into zones2 values(null, null, null, 40.63239230194507, -8.6603676549793, 0)''')
    db.execute('''insert into zones2 values(null, null, null, 40.63195486065902, -8.661093930263293, 1)''')
    db.execute('''insert into zones2 values(null, null, null, 40.63142859277966, -8.660753978842079, 2)''')
    db.execute('''insert into zones2 values(null, null, null, 40.63192425397194, -8.659820484340262, 3)''')
    db.execute('''insert into zones2 values(null, null, null, 40.63284006630615, -8.660225733927449, 4)''')

    db.commit()
    db.close()
    
def update_zones_db_watering(zone, causecode):
    watering = ""
    if causecode == 1:
        watering = "True"
    else:
        watering = "False"
    
    # Establish a connection to the SQLite database
    conn = sql.connect('zones2.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()
    
    # Execute the UPDATE statement
    update_query = "UPDATE zones2 SET water = ? WHERE latitude_zone = ? AND longitude_zone = ?"
    cursor.execute(update_query, (watering, zone[0], zone[1]))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
def update_zones_db_watering_by_ip(ip, causecode, latitude, longitude):
    watering = ""
    if causecode == 1:
        watering = "True"
    else:
        watering = "False"
    
    # Establish a connection to the SQLite database
    conn = sql.connect('zones2.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()
    
    # Execute the UPDATE statement with latitude and longitude comparison
    update_query = "UPDATE zones2 SET water = ? WHERE ip = ? AND ABS(latitude_zone - ?) <= ? AND ABS(longitude_zone - ?) <= ?"
    tolerance = 1e-6  # Adjust tolerance as needed
    cursor.execute(update_query, (watering, ip, latitude, tolerance, longitude, tolerance))

    # Commit the changes and close the connection
    conn.commit()
    conn.close() 
    
    
def update_zones_db(ip, broker, latitude, longitude):
    # Establish a connection to the SQLite database
    conn = sql.connect('zones2.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()
    
    #print("--------->GOING TO UPDATE ZONES DB BY "+ip)
    # Check if the row has already been updated
    select_query = "SELECT ip, broker FROM zones2 WHERE latitude_zone = ? AND longitude_zone = ?"
    cursor.execute(select_query, (latitude, longitude))
    row = cursor.fetchone()
    if row[0] is not None and row[1] is not None:
        #print("--------->"+ip+", THIS ZONE HAS BEEN ALREADY UPDATED BY "+str(row[0]))
        # Row has already been updated, which means that some OBU is already going to analyze this zone
        conn.close()
        return

    # Execute the UPDATE statement
    update_query = "UPDATE zones2 SET ip = ?, broker = ? WHERE latitude_zone = ? AND longitude_zone = ?"
    cursor.execute(update_query, (ip, broker, latitude, longitude))
    
    #print("--------->FINISHED UPDATING ZONES DB BY "+ip)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
def check_zones_not_occupied():
    # Return a list of zones that are not occupied
    
    # Establish a connection to the SQLite database
    conn = sql.connect('zones2.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Select the zones with non-null IP and broker
    select_query = "SELECT * FROM zones2 WHERE ip IS NULL and broker IS NULL"
    cursor.execute(select_query)

    # Fetch all rows from the result
    rows = cursor.fetchall()
    
    zones_not_occupied = []

    # Print the zones with their IP and broker
    for row in rows:
        zone_not_occupied = {
            "ip": row[0],
            "broker": row[1],
            "water": row[2],
            "latitudeZone": row[3],
            "longitudeZone": row[4],
            "id": row[5]
        }
        zones_not_occupied.append(zone_not_occupied)
        
    # Close the connection
    conn.close()
    
    return json.dumps(zones_not_occupied)

def get_ID_by_coordinates(zone):
    
    # Establish a connection to the SQLite database
    conn = sql.connect('zones2.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Select the zones with non-null IP and broker
    select_query = "SELECT id FROM zones2 WHERE latitude_zone = ? AND longitude_zone = ?"
    cursor.execute(select_query, (zone[0],zone[1]))

    # Fetch all rows from the result
    id = cursor.fetchall()
    
    return id[0][0]
    

def return_zone_associated_to_OBU(zone):
    # Return the zone associated to the OBU ip address
    
    # Establish a connection to the SQLite database
    conn = sql.connect('zones2.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Select the zones with ip = ip
    select_query = "SELECT * FROM zones2 WHERE latitude_zone = ? AND longitude_zone = ?"
    cursor.execute(select_query, (zone[0],zone[1]))

    # Fetch all rows from the result
    row = cursor.fetchall()
    print("ROW: ", row)
    if row == []:
        return json.dumps({"ip": None})
    
    info_zone = {
        "ip": row[0][0],
        "broker": row[0][1],
        "water": row[0][2],
        "latitudeZone": row[0][3],
        "longitudeZone": row[0][4],
        "id": row[0][5]
    } 
        
    # Close the connection
    conn.close()
    
    return json.dumps(info_zone)
    