from flask import Flask, render_template, jsonify, request
from obu_db import create_obu_table
from zone_db import create_zones_table
from zones_obu2_db import create_zones_obu2_table
from zones_obu3_db import create_zones_obu3_table
import sqlite3
import json


app = Flask(__name__)

@app.route('/')
def index():
    conn_zones = sqlite3.connect('zones.db')
    zones = conn_zones.execute('SELECT latitude_zone, longitude_zone, id FROM zones')
    
    if request.is_json:
        obu_positions = {} # Dictionary to store the actual updated OBU position for each OBU ip address
        
        conn = sqlite3.connect('obu.db')
        cursor = conn.cursor()
        
        # Fetch the OBU positions from the database
        cursor.execute("SELECT * FROM obu")
        rows = cursor.fetchall()
        
        for row in rows:
            #obu_positions.setdefault(row[2], []).append({"latitude": row[0], "longitude": row[1]})
            obu_positions.update({row[2]: {"latitude": row[0], "longitude": row[1]}})
        
        conn.close()
        
        return jsonify(obu_positions)
    
    return render_template('map.html', zones=zones)

@app.route('/watering')
def watering_info():
    if request.is_json:
        info = {} # Dictionary to store the information about each zone about watering
        
        conn = sqlite3.connect('zones.db')
        cursor = conn.cursor()
        
        # Fetch the OBU positions from the database
        cursor.execute('SELECT ip, broker, water, id FROM zones')
        rows = cursor.fetchall()
        
        for row in rows:
            #obu_positions.setdefault(row[2], []).append({"latitude": row[0], "longitude": row[1]})
            info.update({row[3]: {"ip": row[0], "broker": row[1], "water": row[2]}})
        
        conn.close()
        #print(info)
        
        return jsonify(info)

#----------------------#

#TODO: Function just used for debug
@app.route('/coordinates', methods=['GET'])
def showCoordinates():
    obuCoordinatesList = []
    
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('obu.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()
    
    # Execute a SELECT query to retrieve all rows from the "obu" table
    cursor.execute("SELECT * FROM obu")
    
    # Fetch all rows from the result set
    rows = cursor.fetchall()
    
    for row in rows:
        obu = {"latitude": row[0], "longitude": row[1], "ip": row[2]}
        obuCoordinatesList.append(obu)
    
    cursor.close()
    conn.close()
    
    return json.dumps(obuCoordinatesList, indent=10)

#TODO: Function just used for debug
@app.route('/zones', methods=['GET'])
def showZones():
    zoneList = []
    
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('zones.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()
    
    # Execute a SELECT query to retrieve all rows from the "obu" table
    cursor.execute("SELECT * FROM zones")
    
    # Fetch all rows from the result set
    rows = cursor.fetchall()
    
    for row in rows:
        obu = {"ip": row[0], "broker": row[1], "watering":row[2], "latitude": row[3], "longitude": row[4], "id": row[5]}
        zoneList.append(obu)
    
    cursor.close()
    conn.close()
    
    return json.dumps(zoneList, indent=10)

#TODO: Function just used for debug
@app.route('/zones2', methods=['GET'])
def showZones2():
    zoneList = []
    
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('zones2.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()
    
    # Execute a SELECT query to retrieve all rows from the "obu" table
    cursor.execute("SELECT * FROM zones2")
    
    # Fetch all rows from the result set
    rows = cursor.fetchall()
    
    for row in rows:
        obu = {"ip": row[0], "broker": row[1], "watering":row[2], "latitude": row[3], "longitude": row[4], "id": row[5]}
        zoneList.append(obu)
    
    cursor.close()
    conn.close()
    
    return json.dumps(zoneList, indent=10)

#TODO: Function just used for debug
@app.route('/zones3', methods=['GET'])
def showZones3():
    zoneList = []
    
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('zones3.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()
    
    # Execute a SELECT query to retrieve all rows from the "obu" table
    cursor.execute("SELECT * FROM zones3")
    
    # Fetch all rows from the result set
    rows = cursor.fetchall()
    
    for row in rows:
        obu = {"ip": row[0], "broker": row[1], "watering":row[2], "latitude": row[3], "longitude": row[4], "id": row[5]}
        zoneList.append(obu)
    
    cursor.close()
    conn.close()
    
    return json.dumps(zoneList, indent=10)


if __name__ == '__main__':
    create_zones_table()
    create_zones_obu2_table()
    create_zones_obu3_table()
    create_obu_table()
    app.run(debug = True)