import sqlite3
import os

db_path = os.path.abspath(r"C:\Users\hp\OneDrive\Documents\VSCode\AI-Powered Smart Traffic Analyzer\database\traffic_data.db")

def create_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            car_count INTEGER DEFAULT 0,
            truck_count INTEGER DEFAULT 0,
            bus_count INTEGER DEFAULT 0,
            motorcycle_count INTEGER DEFAULT 0,
            total_vehicles INTEGER DEFAULT 0,
            avg_speed FLOAT,
            congestion_level TEXT,
            lane_occupancy FLOAT,
            vehicle_density FLOAT
        )
    ''') 
    
    conn.commit()
    conn.close()
    print("Database setup completed with improved schema!")

if __name__ == "__main__":
    create_database()