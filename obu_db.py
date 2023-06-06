import sqlite3 as sql

def create_obu_table():
    db = sql.connect('obu.db')

    db.execute('''drop table if exists obu''')
    db.execute('''create table obu(
            latitude real,
            longitude real,
            ip text primary key
            );''')
    
    db.execute('''insert into obu values(null, null, "192.168.98.20")''')
    db.execute('''insert into obu values(null, null, "192.168.98.30")''')
    db.execute('''insert into obu values(null, null, "192.168.98.40")''')

    db.commit()
    db.close()
    
def insert_obu_values(latitude, longitude, ip):
    # Establish a connection to the SQLite database
    conn = sql.connect('obu.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Execute the INSERT statement
    insert_query = "INSERT INTO obu (latitude, longitude, ip) VALUES (?, ?, ?)"
    cursor.execute(insert_query, (latitude, longitude, ip))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
def update_obu_db(latitude, longitude, ip):
    # Establish a connection to the SQLite database
    conn = sql.connect('obu.db')

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Execute the UPDATE statement
    update_query = "UPDATE obu SET latitude = ?, longitude = ? WHERE ip = ?"
    cursor.execute(update_query, (latitude, longitude, ip))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()