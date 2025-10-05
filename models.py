from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Port(Base):
    __tablename__ = "ports"
    
    id = Column(Integer, primary_key=True, index=True)
    port_code = Column(String(10), unique=True, index=True)
    name = Column(String(200))
    country = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    
    shipments_origin = relationship("Shipment", foreign_keys="Shipment.origin_port_id", back_populates="origin")
    shipments_dest = relationship("Shipment", foreign_keys="Shipment.dest_port_id", back_populates="destination")
    congestion_events = relationship("CongestionEvent", back_populates="port")

class Shipment(Base):
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String(50), unique=True, index=True)
    origin_port_id = Column(Integer, ForeignKey("ports.id"))
    dest_port_id = Column(Integer, ForeignKey("ports.id"))
    carrier = Column(String(100))
    vessel_name = Column(String(100))
    etd = Column(DateTime)
    eta_planned = Column(DateTime)
    eta_actual = Column(DateTime, nullable=True)
    status = Column(String(50))
    value_usd = Column(Float)
    cargo_type = Column(String(100))
    route_distance_nm = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    origin = relationship("Port", foreign_keys=[origin_port_id], back_populates="shipments_origin")
    destination = relationship("Port", foreign_keys=[dest_port_id], back_populates="shipments_dest")
    predictions = relationship("Prediction", back_populates="shipment")

class WeatherEvent(Base):
    __tablename__ = "weather_events"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    event_type = Column(String(50))
    severity = Column(String(20))
    wind_speed_kts = Column(Float)
    precipitation_mm = Column(Float)
    storm_flag = Column(Boolean, default=False)
    forecast_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class CongestionEvent(Base):
    __tablename__ = "congestion_events"
    
    id = Column(Integer, primary_key=True, index=True)
    port_id = Column(Integer, ForeignKey("ports.id"))
    queue_length = Column(Integer)
    avg_wait_hours = Column(Float)
    congestion_level = Column(String(20))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    port = relationship("Port", back_populates="congestion_events")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"))
    run_id = Column(String(50))
    delay_probability = Column(Float)
    predicted_delay_hours = Column(Float)
    risk_level = Column(String(20))
    risk_factors = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    shipment = relationship("Shipment", back_populates="predictions")

class ChatLog(Base):
    __tablename__ = "chat_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    user_message = Column(Text)
    bot_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
