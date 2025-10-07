# 📦 Supply Chain Disruption Tracker

An AI-powered predictive logistics platform that monitors global shipping routes, analyzes weather events and port congestion, and provides real-time risk assessments for shipments in transit.

![Supply Chain Tracker](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.118-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### Real-Time Dashboard
- **Live Statistics**: Track total shipments, risk levels, average delays, and value at risk
- **Risk Visualization**: Color-coded risk levels (High/Medium/Low) with probability scores
- **Shipment Tracking**: Monitor 100+ global shipments across 10 major ports
- **Filtering**: Filter shipments by risk level for quick decision-making

### AI-Powered Predictions
- **Machine Learning Model**: Gradient Boosting Classifier trained on shipment patterns
- **Multi-Factor Risk Assessment**: Analyzes route distance, weather conditions, port congestion, and cargo value
- **Delay Forecasting**: Predicts delay probability and estimated delay hours
- **Risk Factors**: Explains why each shipment is flagged (e.g., "Port congestion: high", "Weather: Storm")

### Conversational AI Assistant
- **Natural Language Queries**: Ask questions in plain English
- **Smart Insights**: Get instant answers about high-risk shipments, weather conditions, port congestion, and delays
- **Context-Aware**: Understands logistics-specific terminology
- **Session Memory**: Maintains conversation context

### Geospatial Intelligence
- **Global Coverage**: Monitors 10 major shipping hubs (Shanghai, Singapore, Rotterdam, Los Angeles, etc.)
- **Weather Integration**: Tracks storms, hurricanes, and adverse conditions near ports
- **Port Congestion**: Real-time queue lengths and wait times
- **Distance Calculations**: Haversine formula for accurate nautical mile routing

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: ORM for PostgreSQL database management
- **scikit-learn**: Machine learning for risk prediction
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### Frontend
- **Vanilla JavaScript**: No framework overhead
- **Responsive Design**: CSS Grid layout
- **Real-time Updates**: Auto-refresh dashboard every 30 seconds
- **Interactive Chat**: WebSocket-ready architecture

### Database Schema
```
ports → shipments ← predictions
                  ← weather_events
                  ← congestion_events
                  ← chat_logs
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/SupplyTrackerMVP.git
cd SupplyTrackerMVP
```

2. **Install dependencies**
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary scikit-learn pandas numpy python-dotenv pydantic
```

3. **Set up environment variables**
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

4. **Initialize the database and generate data**
```bash
python generate_data.py
```

5. **Train the ML model**
```bash
python train_model.py
```

6. **Start the server**
```bash
python main.py
```

7. **Open your browser**
```
http://localhost:5000
```

## 📊 Usage

### Dashboard Overview
The main dashboard displays:
- Total number of tracked shipments
- Count of high/medium/low risk shipments
- Average predicted delay in hours
- Total value of high-risk cargo

### Querying the AI Assistant
Try asking:
- "Which shipments are at risk?"
- "Show me delayed shipments"
- "What are the weather conditions?"
- "Which ports have congestion?"

### API Endpoints

#### Dashboard Statistics
```http
GET /api/dashboard/stats
```
Returns aggregate metrics for all shipments.

#### List Shipments
```http
GET /api/shipments?risk_level=high&limit=50
```
Returns shipments filtered by risk level.

#### Get Shipment Details
```http
GET /api/shipments/{shipment_id}
```
Returns full details for a specific shipment including predictions.

#### Generate New Predictions
```http
POST /api/predictions/generate
```
Runs the ML model to generate fresh risk predictions.

#### Chat with AI
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Which shipments are at risk?",
  "session_id": "optional-session-id"
}
```

#### List All Ports
```http
GET /api/ports
```

## 📁 Project Structure

```
SupplyTrackerMVP/
├── main.py                 # FastAPI application and API routes
├── database.py             # Database connection and session management
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic schemas for validation
├── ml_predictor.py         # Machine learning risk prediction engine
├── generate_data.py        # Synthetic data generation script
├── train_model.py          # ML model training script
├── risk_model.pkl          # Trained ML model (generated)
├── scaler.pkl              # Feature scaler (generated)
├── static/
│   └── index.html          # Frontend dashboard UI
├── pyproject.toml          # Python dependencies
└── README.md               # This file
```

## 🤖 Machine Learning Model

### Features
The model uses 7 key features:
1. **Route Distance**: Nautical miles between origin and destination
2. **Days to ETA**: Time remaining until expected arrival
3. **Cargo Value**: USD value of shipment
4. **Weather Severity**: Maximum wind speed near destination
5. **Storm Flag**: Presence of storms/hurricanes
6. **Port Congestion**: Average wait time at destination port
7. **Queue Length**: Number of vessels waiting at port

### Training
- **Algorithm**: Gradient Boosting Classifier
- **Training Samples**: 100 historical shipments
- **Features**: Normalized using StandardScaler
- **Output**: Delay probability (0-1) and risk level (high/medium/low)

### Performance
- Considers multi-modal risk factors
- Real-time prediction on active shipments
- Explainable risk factors for each prediction

## 🎯 Sample Data

The system comes pre-loaded with:
- **10 Global Ports**: Shanghai, Singapore, Rotterdam, New York, Seattle, Los Angeles, Hong Kong, Yokohama, Hamburg, Dubai
- **100 Shipments**: Mix of in-transit, delayed, on-time, and pending
- **50 Weather Events**: Including storms, hurricanes, and clear conditions
- **30+ Congestion Events**: Varying levels across different ports

## 🔮 Future Enhancements

### Planned Features
- [ ] Real-time connector to actual shipping APIs (MarineTraffic, VesselFinder)
- [ ] Weather API integration (NOAA, AccuWeather)
- [ ] Interactive map visualization with vessel positions
- [ ] Email/SMS alerts for high-risk shipments
- [ ] Historical trend analysis and reporting
- [ ] Multi-tenant support for different customers
- [ ] Mobile app for on-the-go monitoring
- [ ] Integration with ERP systems (SAP, Oracle)

### Advanced ML
- [ ] Deep learning for time-series forecasting
- [ ] Anomaly detection for unusual patterns
- [ ] Reinforcement learning for optimal routing suggestions
- [ ] Natural language generation for automated reports

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Inspired by the need for proactive supply chain risk management
- Built for the Fivetran + Google Cloud AI Hackathon
- Special thanks to the open-source community

## 📞 Support

For support, email your-email@example.com or open an issue in the GitHub repository.

---

**Built with ❤️ for logistics teams worldwide**
