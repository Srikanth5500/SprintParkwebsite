import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '3isha417',
    'database': 'sprintparkwebsite'
}

def test_connection():
    print("Starting database connection test...")
    
    try:
        print("Trying to connect to MySQL...")
        conn = mysql.connector.connect(**DB_CONFIG)
        
        if conn.is_connected():
            print("Connection successful!")
            conn.close()
        else:
            print("Failed to connect to MySQL.")
    
    except mysql.connector.Error as err:
        print(f"Error while connecting to MySQL: {err}")

if __name__ == "__main__":
    test_connection()
