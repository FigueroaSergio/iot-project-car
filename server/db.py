import sqlite3

def create_db_and_table():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('gps_coordinates.db')
    cursor = conn.cursor()

    # Create a table to store GPS coordinates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coordinates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def insert_coordinates(latitude, longitude):
    # Connect to SQLite database
    conn = sqlite3.connect('gps_coordinates.db')
    cursor = conn.cursor()

    # Insert GPS coordinates into the table
    cursor.execute('''
        INSERT INTO coordinates (latitude, longitude)
        VALUES (?, ?)
    ''', (latitude, longitude))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    create_db_and_table()