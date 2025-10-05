from database import SessionLocal
from ml_predictor import RiskPredictor

def main():
    db = SessionLocal()
    try:
        predictor = RiskPredictor()
        
        print("Training ML model...")
        predictor.train_model(db)
        print("Model trained successfully!")
        
        print("\nGenerating predictions...")
        run_id = predictor.generate_predictions(db)
        print(f"Predictions generated successfully! (run_id: {run_id})")
    finally:
        db.close()

if __name__ == "__main__":
    main()
