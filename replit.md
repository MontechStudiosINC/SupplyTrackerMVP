# Supply Chain Disruption Tracker

## Overview

A supply chain disruption tracking system that uses machine learning to predict shipment delays and risk levels. The application monitors global shipping routes, analyzes weather events and port congestion, and provides real-time risk assessments for shipments in transit. Built with FastAPI backend and a vanilla JavaScript frontend, it integrates ML predictions with geospatial data to help logistics teams proactively manage supply chain risks.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

**Framework: FastAPI**
- RESTful API design with async support for handling concurrent requests
- Built-in OpenAPI documentation through FastAPI's automatic schema generation
- Dependency injection pattern used for database sessions via `get_db()` generator
- CORS middleware configured to allow all origins for development flexibility

**Database: SQLAlchemy ORM with PostgreSQL**
- Connection pooling with pre-ping health checks and 300-second connection recycling to prevent stale connections
- Declarative base pattern for model definitions
- Session management using context managers (generator pattern) to ensure proper cleanup
- Database URL configured through environment variables for security and deployment flexibility

**Machine Learning Integration**
- Custom `RiskPredictor` class implementing scikit-learn Gradient Boosting Classifier
- Persistent model storage using pickle serialization (risk_model.pkl, scaler.pkl)
- Feature engineering combines shipment data, weather conditions, and port congestion metrics
- StandardScaler for feature normalization before prediction
- Three-tier risk classification: high/medium/low based on delay probability thresholds

**Data Model Design**
- **Ports**: Reference data for shipping locations with geospatial coordinates
- **Shipments**: Core transaction records tracking vessel movements between ports
- **WeatherEvents**: Time-series weather data with severity classifications
- **CongestionEvents**: Port-specific metrics (wait times, queue lengths)
- **Predictions**: ML-generated risk assessments linked to shipments
- **ChatLog**: Conversation history for AI assistant feature
- Relationships use explicit foreign keys with SQLAlchemy relationships for bidirectional navigation

### Frontend Architecture

**Technology: Vanilla JavaScript with HTML/CSS**
- Single-page application served as static files through FastAPI's StaticFiles mount
- No framework dependencies - direct DOM manipulation and fetch API for backend communication
- CSS Grid layout for responsive dashboard design
- Gradient-based color scheme for modern UI aesthetics

**Design Pattern**
- Separation of presentation (HTML/CSS) from data fetching (JavaScript)
- Event-driven interactions for real-time updates
- Statistics dashboard showing aggregate metrics

### External Dependencies

**Required Services**
- **PostgreSQL Database**: Primary data store accessed via DATABASE_URL environment variable
- Connection string must be provided at runtime; application fails fast if not configured

**Python Libraries**
- **FastAPI**: Web framework for API endpoints
- **SQLAlchemy**: ORM and database abstraction layer
- **scikit-learn**: Machine learning models (GradientBoostingClassifier, StandardScaler)
- **numpy**: Numerical computations including haversine distance calculations
- **uvicorn**: ASGI server for running FastAPI application
- **pydantic**: Data validation and serialization schemas

**Data Generation**
- Synthetic data generator (`generate_data.py`) creates realistic shipping scenarios
- Ports based on real-world major shipping hubs (Shanghai, Singapore, Rotterdam, etc.)
- Haversine formula for calculating nautical mile distances between ports
- Random sampling from realistic carrier names, vessel types, and cargo categories

**Model Training Pipeline**
- Standalone training script (`train_model.py`) for offline model creation
- Feature extraction considers: route distance, time to ETA, cargo value, weather severity, storm flags, port congestion
- Model artifacts saved to filesystem for prediction service to load at startup
- Predictions generated in batches and stored in database with unique run identifiers

**Key Architectural Decisions**

1. **Separation of Training and Prediction**: Model training is decoupled from the web service, allowing offline batch processing and avoiding blocking the API during retraining

2. **Feature Normalization**: All features scaled to 0-1 range for consistent model performance across different measurement units

3. **Geospatial Proximity Matching**: Weather events matched to ports using simple lat/long bounding box (±5 degrees) rather than complex geospatial queries, trading precision for simplicity

4. **Risk Categorization**: Continuous delay probability converted to discrete risk levels for easier decision-making by users

5. **Database-First Design**: All predictions and events stored persistently rather than computed on-demand, enabling historical analysis and audit trails