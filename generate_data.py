import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Port, Shipment, WeatherEvent, CongestionEvent
import numpy as np

PORTS_DATA = [
    {"port_code": "CNSHA", "name": "Shanghai", "country": "China", "latitude": 31.2304, "longitude": 121.4737},
    {"port_code": "SGSIN", "name": "Singapore", "country": "Singapore", "latitude": 1.3521, "longitude": 103.8198},
    {"port_code": "NLRTM", "name": "Rotterdam", "country": "Netherlands", "latitude": 51.9225, "longitude": 4.47917},
    {"port_code": "USNYC", "name": "New York", "country": "USA", "latitude": 40.7128, "longitude": -74.0060},
    {"port_code": "USSEA", "name": "Seattle", "country": "USA", "latitude": 47.6062, "longitude": -122.3321},
    {"port_code": "USLAX", "name": "Los Angeles", "country": "USA", "latitude": 33.7701, "longitude": -118.1937},
    {"port_code": "HKHKG", "name": "Hong Kong", "country": "Hong Kong", "latitude": 22.3193, "longitude": 114.1694},
    {"port_code": "JPYKK", "name": "Yokohama", "country": "Japan", "latitude": 35.4437, "longitude": 139.6380},
    {"port_code": "DEHAM", "name": "Hamburg", "country": "Germany", "latitude": 53.5511, "longitude": 9.9937},
    {"port_code": "AEDXB", "name": "Dubai", "country": "UAE", "latitude": 25.2048, "longitude": 55.2708}
]

CARRIERS = ["Maersk", "MSC", "CMA CGM", "COSCO", "Hapag-Lloyd", "ONE", "Evergreen", "Yang Ming"]
VESSEL_NAMES = ["Ocean Trader", "Sea Pioneer", "Blue Horizon", "Pacific Star", "Atlantic Wave", "Global Express", "Cargo Master", "Trade Wind"]
CARGO_TYPES = ["Electronics", "Machinery", "Textiles", "Food Products", "Chemicals", "Automobiles", "Raw Materials", "Consumer Goods"]
WEATHER_TYPES = ["Clear", "Rain", "Storm", "Hurricane", "Fog", "High Winds"]

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def calculate_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    nm = 3440.065 * c
    return nm

def seed_ports(db: Session):
    ports = []
    for port_data in PORTS_DATA:
        port = Port(**port_data)
        db.add(port)
        ports.append(port)
    db.commit()
    return ports

def seed_weather_events(db: Session, ports):
    for _ in range(50):
        port = random.choice(ports)
        event_type = random.choice(WEATHER_TYPES)
        severity = "low"
        storm_flag = False
        
        if event_type in ["Storm", "Hurricane"]:
            severity = random.choice(["medium", "high"])
            storm_flag = True
        
        weather = WeatherEvent(
            location=port.name,
            latitude=port.latitude,
            longitude=port.longitude,
            event_type=event_type,
            severity=severity,
            wind_speed_kts=random.uniform(5, 80) if event_type in ["Storm", "Hurricane", "High Winds"] else random.uniform(0, 20),
            precipitation_mm=random.uniform(0, 100) if event_type in ["Rain", "Storm", "Hurricane"] else 0,
            storm_flag=storm_flag,
            forecast_time=datetime.utcnow() + timedelta(hours=random.randint(-24, 72))
        )
        db.add(weather)
    db.commit()

def seed_congestion_events(db: Session, ports):
    for port in ports:
        for _ in range(random.randint(1, 3)):
            queue_length = random.randint(5, 50)
            avg_wait = random.uniform(2, 48)
            
            if avg_wait > 24:
                level = "high"
            elif avg_wait > 12:
                level = "medium"
            else:
                level = "low"
            
            congestion = CongestionEvent(
                port_id=port.id,
                queue_length=queue_length,
                avg_wait_hours=avg_wait,
                congestion_level=level,
                recorded_at=datetime.utcnow() - timedelta(hours=random.randint(0, 48))
            )
            db.add(congestion)
    db.commit()

def seed_shipments(db: Session, ports):
    shipments = []
    for i in range(100):
        origin = random.choice(ports)
        dest = random.choice([p for p in ports if p.id != origin.id])
        
        etd = datetime.utcnow() + timedelta(days=random.randint(-30, 10))
        distance = calculate_distance(origin.latitude, origin.longitude, dest.latitude, dest.longitude)
        transit_days = int(distance / 400) + random.randint(1, 5)
        eta_planned = etd + timedelta(days=transit_days)
        
        status_options = ["in_transit", "delayed", "on_time", "pending"]
        status = random.choice(status_options)
        
        eta_actual = None
        if status == "delayed":
            eta_actual = eta_planned + timedelta(hours=random.randint(12, 120))
        elif status == "on_time" and eta_planned < datetime.utcnow():
            eta_actual = eta_planned
        
        shipment = Shipment(
            shipment_id=f"SHP-{1000+i}",
            origin_port_id=origin.id,
            dest_port_id=dest.id,
            carrier=random.choice(CARRIERS),
            vessel_name=random.choice(VESSEL_NAMES),
            etd=etd,
            eta_planned=eta_planned,
            eta_actual=eta_actual,
            status=status,
            value_usd=random.uniform(100000, 5000000),
            cargo_type=random.choice(CARGO_TYPES),
            route_distance_nm=float(distance)
        )
        db.add(shipment)
        shipments.append(shipment)
    db.commit()
    return shipments

def main():
    print("Initializing database...")
    init_db()
    
    db = SessionLocal()
    try:
        print("Seeding ports...")
        ports = seed_ports(db)
        
        print("Seeding weather events...")
        seed_weather_events(db, ports)
        
        print("Seeding congestion events...")
        seed_congestion_events(db, ports)
        
        print("Seeding shipments...")
        shipments = seed_shipments(db, ports)
        
        print(f"Database seeded successfully!")
        print(f"Created {len(ports)} ports, {len(shipments)} shipments")
    finally:
        db.close()

if __name__ == "__main__":
    main()
