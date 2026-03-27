from database import SessionLocal
from ml_model import recommendation_engine
def main():
    db = SessionLocal()
    try:
        recommendation_engine.train(db)
        status = "trained" if recommendation_engine.trained else "not-trained"
        print(f"[OK] Recommendation engine status: {status}")
    finally:
        db.close()
if __name__ == "__main__":
    main()