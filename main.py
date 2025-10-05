from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import uvicorn
import uuid
from datetime import datetime

from database import get_db, engine, Base
from models import Shipment, Port, Prediction, WeatherEvent, CongestionEvent, ChatLog
from schemas import (
    ShipmentWithPrediction, Prediction as PredictionSchema,
    ChatMessage, ChatResponse, DashboardStats, Port as PortSchema
)
from ml_predictor import RiskPredictor

app = FastAPI(title="Supply Chain Disruption Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = RiskPredictor()

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    predictor.load_model()

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(Shipment).count()
    
    high_risk = db.query(Prediction).filter(Prediction.risk_level == "high").count()
    medium_risk = db.query(Prediction).filter(Prediction.risk_level == "medium").count()
    low_risk = db.query(Prediction).filter(Prediction.risk_level == "low").count()
    
    avg_delay = db.query(func.avg(Prediction.predicted_delay_hours)).scalar() or 0
    
    high_risk_shipments = db.query(Shipment).join(Prediction).filter(
        Prediction.risk_level == "high"
    ).all()
    value_at_risk = sum([s.value_usd for s in high_risk_shipments])
    
    return DashboardStats(
        total_shipments=total,
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        avg_delay_hours=round(avg_delay, 1),
        total_value_at_risk=round(value_at_risk, 2)
    )

@app.get("/api/shipments", response_model=List[ShipmentWithPrediction])
def get_shipments(
    risk_level: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Shipment)
    
    if risk_level:
        query = query.join(Prediction).filter(Prediction.risk_level == risk_level)
    
    shipments = query.limit(limit).all()
    return shipments

@app.get("/api/shipments/{shipment_id}", response_model=ShipmentWithPrediction)
def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment

@app.get("/api/ports", response_model=List[PortSchema])
def get_ports(db: Session = Depends(get_db)):
    return db.query(Port).all()

@app.post("/api/predictions/generate")
def generate_predictions(db: Session = Depends(get_db)):
    try:
        run_id = predictor.generate_predictions(db)
        return {"status": "success", "run_id": run_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
def chat(message: ChatMessage, db: Session = Depends(get_db)):
    session_id = message.session_id or str(uuid.uuid4())
    user_msg = message.message.lower()
    
    response_text = ""
    data = {}
    
    if "risk" in user_msg or "at risk" in user_msg:
        high_risk = db.query(Shipment).join(Prediction).filter(
            Prediction.risk_level == "high"
        ).limit(5).all()
        
        if high_risk:
            response_text = f"I found {len(high_risk)} high-risk shipments:\n\n"
            for ship in high_risk:
                pred = ship.predictions[-1] if ship.predictions else None
                if pred:
                    response_text += f"• {ship.shipment_id}: {ship.origin.port_code} → {ship.destination.port_code}, "
                    response_text += f"{pred.delay_probability*100:.0f}% delay risk ({pred.predicted_delay_hours:.1f}h delay)\n"
        else:
            response_text = "No high-risk shipments found at the moment."
        
        data = {"count": len(high_risk)}
    
    elif "delay" in user_msg or "delayed" in user_msg:
        delayed = db.query(Shipment).filter(Shipment.status == "delayed").all()
        response_text = f"There are currently {len(delayed)} delayed shipments. "
        
        if delayed:
            total_value = sum([s.value_usd for s in delayed])
            response_text += f"Total value affected: ${total_value/1000000:.1f}M"
        
        data = {"delayed_count": len(delayed)}
    
    elif "weather" in user_msg:
        storms = db.query(WeatherEvent).filter(WeatherEvent.storm_flag == True).all()
        response_text = f"There are {len(storms)} active storm systems that could impact shipments:\n\n"
        for storm in storms[:3]:
            response_text += f"• {storm.event_type} near {storm.location} (wind: {storm.wind_speed_kts:.0f} kts)\n"
        
        data = {"storm_count": len(storms)}
    
    elif "port" in user_msg and "congestion" in user_msg:
        congested = db.query(CongestionEvent).filter(
            CongestionEvent.congestion_level.in_(["high", "medium"])
        ).all()
        
        response_text = f"Found {len(congested)} ports with congestion:\n\n"
        for cong in congested[:5]:
            response_text += f"• {cong.port.name}: {cong.congestion_level} ({cong.avg_wait_hours:.1f}h wait)\n"
        
        data = {"congested_ports": len(congested)}
    
    else:
        stats = get_dashboard_stats(db)
        response_text = f"Current supply chain status:\n\n"
        response_text += f"• Total shipments: {stats.total_shipments}\n"
        response_text += f"• High risk: {stats.high_risk_count}\n"
        response_text += f"• Medium risk: {stats.medium_risk_count}\n"
        response_text += f"• Average delay: {stats.avg_delay_hours}h\n"
        response_text += f"• Value at risk: ${stats.total_value_at_risk/1000000:.1f}M\n\n"
        response_text += "You can ask me about:\n- Which shipments are at risk?\n- Weather conditions\n- Port congestion\n- Delayed shipments"
        
        data = stats.dict()
    
    chat_log = ChatLog(
        session_id=session_id,
        user_message=message.message,
        bot_response=response_text
    )
    db.add(chat_log)
    db.commit()
    
    return ChatResponse(
        response=response_text,
        session_id=session_id,
        data=data
    )

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
