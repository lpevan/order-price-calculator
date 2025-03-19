from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .price_calculator import PriceCalculator
from .database import engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Price Calculator API")

# Dependency to get database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/calculate-price", response_model=schemas.PriceCalculationResponse)
def calculate_price(
    request: schemas.PriceCalculationRequest,
    db: Session = Depends(get_db)
):
    calculator = PriceCalculator(db)
    
    try:
        result = calculator.calculate_final_price(
            services=[service.dict() for service in request.services],
            promo_code=request.promo_code,
            user_location=request.location,
            user_id=request.user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/promotions/", response_model=schemas.Promotion)
def create_promotion(
    promotion: schemas.PromotionCreate,
    db: Session = Depends(get_db)
):
    db_promotion = models.Promotion(**promotion.dict())
    db.add(db_promotion)
    try:
        db.commit()
        db.refresh(db_promotion)
        return db_promotion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Promotion code already exists")

@app.get("/promotions/", response_model=List[schemas.Promotion])
def list_promotions(db: Session = Depends(get_db)):
    promotions = db.query(models.Promotion).all()
    return promotions

# Add some sample promotions on startup
@app.on_event("startup")
async def startup_event():
    db = database.SessionLocal()
    try:
        # Only add if no promotions exist
        if db.query(models.Promotion).count() == 0:
            sample_promotions = [
                models.Promotion(
                    code="WELCOME10",
                    discount_type="fixed",
                    value=10,
                    rule_type="user",
                    rule_params={"user_ids": [1, 2, 3]},  # For new users
                    expiry_date="2025-12-31"
                ),
                models.Promotion(
                    code="BARCELONA30",
                    discount_type="percentage",
                    value=30,
                    rule_type="location",
                    rule_params={"required_location": "Barcelona"},
                    expiry_date="2025-06-30"
                ),
                models.Promotion(
                    code="MIN50",
                    discount_type="fixed",
                    value=5,
                    rule_type="order",
                    rule_params={"min_order": 50},
                    expiry_date=None
                ),
            ]
            db.bulk_save_objects(sample_promotions)
            db.commit()
    finally:
        db.close()
