import time
import random
from src.db_manager import IndustrialDBManager

def run_simulator():
    db = IndustrialDBManager()
    db.setup_database()
    print("[INFO] Industrial Furnace Simulator activated. Transmitting telemetry...")
    
    equipment_id = 1 # Assuming 'Arc Furnace A'
    
    try:
        while True:
            # 95% probability of normal operating temperature
            if random.random() > 0.05:
                temp = round(random.uniform(70.0, 75.0), 2)
            else:
                # 5% probability of critical thermal anomaly
                temp = round(random.uniform(110.0, 130.0), 2)
                
            db.insert_telemetry(equipment_id, temp)
            print(f"[TX] Payload sent -> Temp: {temp}°C | Equipment ID: {equipment_id}")
            time.sleep(1.5)
            
    except KeyboardInterrupt:
        print("\n[INFO] Simulator terminated gracefully.")

if __name__ == "__main__":
    run_simulator()