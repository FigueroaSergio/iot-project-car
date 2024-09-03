import sqlite3

def fetch_all_coordinates():
    try:
        conn = sqlite3.connect('gps_coordinates.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM coordinates')
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            print("Data fetched successfully:")
            for row in rows:
                print(row)
        else:
            print("No data found in the database.")
        
        return rows
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
if __name__ == '__main__':
    fetch_all_coordinates()
