from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PortBase(BaseModel):
    port_code: str
    name: str
    country: str
    latitude: float
    longitude: float

class Port(PortBase):
    id: int
    
    class Config:
        from_attributes = True

class ShipmentBase(BaseModel):
    shipment_id: str
    carrier: str
    vessel_name: str
    etd: datetime
    eta_planned: datetime
    status: str
    value_usd: float
    cargo_type: str
    route_distance_nm: float

class Shipment(ShipmentBase):
    id: int
    origin_port_id: int
    dest_port_id: int
    eta_actual: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ShipmentWithPorts(Shipment):
    origin: Port
    destination: Port

class PredictionBase(BaseModel):
    delay_probability: float
    predicted_delay_hours: float
    risk_level: str
    risk_factors: str

class Prediction(PredictionBase):
    id: int
    shipment_id: int
    run_id: str
    generated_at: datetime
    
    class Config:
        from_attributes = True

class ShipmentWithPrediction(ShipmentWithPorts):
    predictions: List[Prediction] = []

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    data: Optional[dict] = None

class DashboardStats(BaseModel):
    total_shipments: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    avg_delay_hours: float
    total_value_at_risk: float
