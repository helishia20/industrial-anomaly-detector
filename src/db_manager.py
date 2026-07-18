import mysql.connector
from config.database_config import DB_SETTINGS

class IndustrialDBManager:
    def __init__(self):
        self.conn = None

    def connect(self):
        try:
            # Fatal Fix for MySQL: Check connection status dynamically
            if self.conn is None or not self.conn.is_connected():
                self.conn = mysql.connector.connect(**DB_SETTINGS)
                self.conn.autocommit = True
            return True
        except Exception as e:
            print(f"[CRITICAL ERROR] MySQL connection failed: {e}")
            return False

    def setup_database(self):
        """Initializes the relational MySQL schema with AUTO_INCREMENT"""
        if self.connect():
            cursor = self.conn.cursor()
            try:
                # 1. Equipment Entity
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS equipment (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        location VARCHAR(100)
                    )
                """)
                
                # Seed default equipment if table is empty
                cursor.execute("SELECT count(*) FROM equipment")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO equipment (name, location) VALUES ('Arc Furnace A', 'Melt Shop 1')")

                # 2. Telemetry Entity
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sensor_telemetry (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        equipment_id INT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        temperature DECIMAL(5, 2),
                        FOREIGN KEY (equipment_id) REFERENCES equipment(id)
                    )
                """)
            finally:
                cursor.close()

    def insert_telemetry(self, equipment_id, temp):
        if self.connect():
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO sensor_telemetry (equipment_id, temperature) 
                    VALUES (%s, %s)
                """, (equipment_id, temp))

    def fetch_latest_telemetry(self):
        if self.connect():
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT t.timestamp, t.temperature, e.name 
                    FROM sensor_telemetry t
                    JOIN equipment e ON t.equipment_id = e.id
                    ORDER BY t.id DESC 
                    LIMIT 1
                """)
                return cur.fetchone()
        return None

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()