import sqlite3
import tkinter as tk
from tkinter import ttk
import os
import time

db_path = os.path.abspath(r"C:\Users\hp\OneDrive\Documents\VSCode\AI-Powered Smart Traffic Analyzer\database\traffic_data.db")

def fetch_vehicle_data():
    retries = 5
    for attempt in range(retries):
        try:
            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicle_counts'")
            if cursor.fetchone() is None:
                print("Database error: Table 'vehicle_counts' not found. Start tracking first!")
                conn.close()
                return []   
            cursor.execute("SELECT * FROM vehicle_counts")
            records = cursor.fetchall()
            conn.close()
            return records

        except sqlite3.OperationalError as e:
            if attempt == retries - 1:
                print("Database error:", e)
                return []
            time.sleep(1)
        except sqlite3.Error as e:
            print("Database error:", e)
            return []


def display_data():
    records = fetch_vehicle_data()
    
    for row in tree.get_children():
        tree.delete(row)
    
    for record in records:
        tree.insert("", "end", values=record)

# GUI Setup
root = tk.Tk()
root.title("Traffic Data Viewer")
root.geometry("600x400")

tree = ttk.Treeview(root, columns=("ID", "Timestamp", "Car", "Truck", "Bus", "Motorcycle"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Timestamp", text="Timestamp")
tree.heading("Car", text="Car")
tree.heading("Truck", text="Truck")
tree.heading("Bus", text="Bus")
tree.heading("Motorcycle", text="Motorcycle")
tree.pack(fill=tk.BOTH, expand=True)

btn_refresh = tk.Button(root, text="Refresh Data", command=display_data)
btn_refresh.pack(pady=10)

display_data()
root.mainloop()
