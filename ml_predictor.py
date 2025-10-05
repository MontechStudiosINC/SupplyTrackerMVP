import pickle
import os
from datetime import datetime, timedelta
from typing import List, Tuple
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session
from models import Shipment, WeatherEvent, CongestionEvent, Prediction, Port
import uuid

class RiskPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_path = "risk_model.pkl"
        self.scaler_path = "scaler.pkl"
        
    def extract_features(self, shipment: Shipment, weather_events: List[WeatherEvent], 
                        congestion: CongestionEvent = None, dest_port: Port = None) -> np.ndarray:
        features = []
        
        features.append(shipment.route_distance_nm / 10000.0)
        
        days_to_eta = (shipment.eta_planned - datetime.utcnow()).total_seconds() / 86400
        features.append(max(0, days_to_eta) / 30.0)
        
        features.append(shipment.value_usd / 1000000.0)
        
        nearby_weather = [w for w in weather_events 
                         if dest_port and abs(w.latitude - dest_port.latitude) < 5 
                         and abs(w.longitude - dest_port.longitude) < 5]
        
        max_wind = max([w.wind_speed_kts for w in nearby_weather], default=0)
        features.append(max_wind / 100.0)
        
        has_storm = any(w.storm_flag for w in nearby_weather)
        features.append(1.0 if has_storm else 0.0)
        
        congestion_hours = congestion.avg_wait_hours if congestion else 0
        features.append(congestion_hours / 48.0)
        
        congestion_queue = congestion.queue_length if congestion else 0
        features.append(congestion_queue / 50.0)
        
        return np.array(features).reshape(1, -1)
    
    def train_model(self, db: Session):
        shipments = db.query(Shipment).all()
        weather_events = db.query(WeatherEvent).all()
        
        X = []
        y = []
        
        for shipment in shipments:
            dest_port = db.query(Port).filter(Port.id == shipment.dest_port_id).first()
            congestion = db.query(CongestionEvent).filter(
                CongestionEvent.port_id == shipment.dest_port_id
            ).order_by(CongestionEvent.recorded_at.desc()).first()
            
            features = self.extract_features(shipment, weather_events, congestion, dest_port)
            X.append(features[0])
            
            is_delayed = False
            if shipment.eta_actual and shipment.eta_planned:
                delay_hours = (shipment.eta_actual - shipment.eta_planned).total_seconds() / 3600
                is_delayed = delay_hours > 12
            elif shipment.status == "delayed":
                is_delayed = True
            
            y.append(1 if is_delayed else 0)
        
        X = np.array(X)
        y = np.array(y)
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"Model trained with {len(X)} samples")
        return self.model
    
    def load_model(self):
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            return True
        return False
    
    def predict_risk(self, shipment: Shipment, weather_events: List[WeatherEvent], 
                    congestion: CongestionEvent, dest_port: Port) -> Tuple[float, float, str]:
        if not self.model or not self.scaler:
            if not self.load_model():
                return 0.5, 24.0, "medium"
        
        features = self.extract_features(shipment, weather_events, congestion, dest_port)
        features_scaled = self.scaler.transform(features)
        
        delay_prob = self.model.predict_proba(features_scaled)[0][1]
        
        predicted_delay_hours = delay_prob * 48.0
        
        if delay_prob > 0.7:
            risk_level = "high"
        elif delay_prob > 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return delay_prob, predicted_delay_hours, risk_level
    
    def generate_predictions(self, db: Session):
        shipments = db.query(Shipment).filter(Shipment.status.in_(["in_transit", "pending"])).all()
        weather_events = db.query(WeatherEvent).all()
        run_id = str(uuid.uuid4())[:8]
        
        for shipment in shipments:
            dest_port = db.query(Port).filter(Port.id == shipment.dest_port_id).first()
            congestion = db.query(CongestionEvent).filter(
                CongestionEvent.port_id == shipment.dest_port_id
            ).order_by(CongestionEvent.recorded_at.desc()).first()
            
            delay_prob, delay_hours, risk_level = self.predict_risk(
                shipment, weather_events, congestion, dest_port
            )
            
            risk_factors = []
            if congestion and congestion.avg_wait_hours > 12:
                risk_factors.append(f"Port congestion: {congestion.congestion_level}")
            
            nearby_storms = [w for w in weather_events 
                           if w.storm_flag and dest_port
                           and abs(w.latitude - dest_port.latitude) < 5]
            if nearby_storms:
                risk_factors.append(f"Weather: {nearby_storms[0].event_type}")
            
            if shipment.route_distance_nm > 8000:
                risk_factors.append("Long distance route")
            
            prediction = Prediction(
                shipment_id=shipment.id,
                run_id=run_id,
                delay_probability=float(delay_prob),
                predicted_delay_hours=float(delay_hours),
                risk_level=risk_level,
                risk_factors=", ".join(risk_factors) if risk_factors else "Normal conditions"
            )
            db.add(prediction)
        
        db.commit()
        print(f"Generated predictions for {len(shipments)} shipments (run_id: {run_id})")
        return run_id
