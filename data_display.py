import sqlite3
import tkinter as tk
from tkinter import ttk
import os
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Database configuration
db_path = os.path.abspath(r"C:\Users\hp\OneDrive\Documents\VSCode\AI-Powered Smart Traffic Analyzer\database\traffic_data.db")

class TrafficDataViewer:
    def __init__(self, root):
        self.root = root 
        self.root.title("Traffic Analytics Dashboard")
        self.root.geometry("1200x800")
        
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        # Create main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Data table frame
        table_frame = tk.LabelFrame(main_frame, text="Live Traffic Data", padx=5, pady=5)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbars
        self.tree = ttk.Treeview(table_frame, columns=(
            "ID", "Timestamp", "Cars", "Trucks", "Buses", "Motorcycles",
            "Total", "Avg Speed", "Congestion", "Lane Occ", "Density"
        ), show="headings")
        
        # Configure columns
        columns = [
            ("ID", 50, tk.CENTER),
            ("Timestamp", 150, tk.CENTER),
            ("Cars", 60, tk.CENTER),
            ("Trucks", 60, tk.CENTER),
            ("Buses", 60, tk.CENTER),
            ("Motorcycles", 80, tk.CENTER),
            ("Total", 60, tk.CENTER),
            ("Avg Speed", 80, tk.CENTER),
            ("Congestion", 100, tk.CENTER),
            ("Lane Occ", 80, tk.CENTER),
            ("Density", 80, tk.CENTER)
        ]
        
        for col, width, anchor in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.btn_refresh = tk.Button(
            button_frame, text="Refresh Now", command=self.refresh_data)
        self.btn_refresh.pack(side=tk.LEFT, padx=5)
        
        self.btn_auto_refresh = tk.Button(
            button_frame, text="Start Auto-Refresh (5s)", 
            command=self.toggle_auto_refresh)
        self.btn_auto_refresh.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.lbl_status = tk.Label(
            main_frame, text="Ready", fg="blue", anchor=tk.W)
        self.lbl_status.pack(fill=tk.X)
        
        # Charts frame
        chart_frame = tk.LabelFrame(main_frame, text="Analytics", padx=5, pady=5)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figures
        self.fig1, self.ax1 = plt.subplots(figsize=(6, 3))
        self.fig2, self.ax2 = plt.subplots(figsize=(6, 3))
        
        # Add to tkinter
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=chart_frame)
        self.canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=chart_frame)
        self.canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Auto-refresh control
        self.auto_refresh_id = None
        self.auto_refresh_active = False
        
    def fetch_data(self):
        """Retrieve data from database with error handling"""
        try:
            conn = sqlite3.connect(db_path, timeout=5)
            query = """
                SELECT 
                    id, 
                    datetime(timestamp, 'localtime') as timestamp,
                    car_count as Cars,
                    truck_count as Trucks,
                    bus_count as Buses,
                    motorcycle_count as Motorcycles,
                    total_vehicles as Total,
                    ROUND(avg_speed, 2) as "Avg Speed",
                    congestion_level as Congestion,
                    ROUND(lane_occupancy, 2) as "Lane Occ",
                    ROUND(vehicle_density, 2) as Density
                FROM traffic_analytics
                ORDER BY timestamp DESC
                LIMIT 100
            """
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except sqlite3.Error as e:
            self.lbl_status.config(
                text=f"Database error: {str(e)}", fg="red")
            return pd.DataFrame()
        
    def refresh_data(self):
        """Update the display with fresh data"""
        self.lbl_status.config(text="Refreshing data...", fg="blue")
        self.root.update()
        
        df = self.fetch_data()
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Insert new data
        if not df.empty:
            for _, row in df.iterrows():
                self.tree.insert("", "end", values=tuple(row))
            
            # Update charts
            self.update_charts(df)
            
            status_text = f"Last updated: {datetime.now().strftime('%H:%M:%S')} | {len(df)} records shown"
            self.lbl_status.config(text=status_text, fg="green")
        else:
            self.lbl_status.config(text="No data available", fg="orange")
        
    def update_charts(self, df):
        """Update the analytics charts"""
        # Vehicle distribution pie chart
        self.ax1.clear()
        vehicle_counts = df[['Cars', 'Trucks', 'Buses', 'Motorcycles']].sum()
        self.ax1.pie(vehicle_counts, labels=vehicle_counts.index, 
                    autopct='%1.1f%%', startangle=90)
        self.ax1.set_title('Vehicle Type Distribution')
        self.canvas1.draw()
        
        # Traffic trend line chart
        self.ax2.clear()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df['Total'].plot(ax=self.ax2, color='blue', legend=True)
        self.ax2.set_ylabel('Vehicle Count')
        
        # Add secondary axis for speed
        ax2b = self.ax2.twinx()
        df['Avg Speed'].plot(ax=ax2b, color='red', legend=True)
        ax2b.set_ylabel('Speed (px/s)')
        
        self.ax2.set_title('Traffic Trends Over Time')
        self.ax2.grid(True)
        self.canvas2.draw()
        
    def toggle_auto_refresh(self):
        """Toggle automatic refresh every 5 seconds"""
        if self.auto_refresh_active:
            if self.auto_refresh_id:
                self.root.after_cancel(self.auto_refresh_id)
            self.auto_refresh_active = False
            self.btn_auto_refresh.config(text="Start Auto-Refresh (5s)")
            self.lbl_status.config(text="Auto-refresh stopped", fg="blue")
        else:
            self.auto_refresh_active = True
            self.btn_auto_refresh.config(text="Stop Auto-Refresh")
            self.run_auto_refresh()
            
    def run_auto_refresh(self):
        """Run the auto-refresh cycle"""
        if self.auto_refresh_active:
            self.refresh_data()
            self.auto_refresh_id = self.root.after(5000, self.run_auto_refresh)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficDataViewer(root)
    root.mainloop()