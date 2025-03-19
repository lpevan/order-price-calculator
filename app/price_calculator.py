from typing import List, Optional, Tuple
from .models import Promotion
from sqlalchemy.orm import Session
from datetime import datetime

class PriceCalculator:
    def __init__(self, db: Session):
        self.db = db

    def calculate_total_price(self, services: List[dict]) -> float:
        """Calculate the total price of all services"""
        return sum(service["price"] for service in services)

    def get_valid_promotions(
        self, 
        order_total: float, 
        user_location: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[Promotion]:
        """Get all valid promotions for the given order"""
        promotions = self.db.query(Promotion).all()
        return [
            promo for promo in promotions 
            if promo.is_valid(order_total, user_location, user_id)
        ]

    def find_best_promotion(
        self, 
        order_total: float, 
        promo_code: Optional[str] = None,
        user_location: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[Optional[Promotion], float]:
        """Find the promotion that gives the highest discount"""
        if promo_code:
            # If a specific promo code is provided, try to use it
            promotion = self.db.query(Promotion).filter(Promotion.code == promo_code).first()
            if promotion and promotion.is_valid(order_total, user_location, user_id):
                return promotion, promotion.calculate_discount(order_total)

        # Get all valid promotions and find the one with highest discount
        valid_promotions = self.get_valid_promotions(order_total, user_location, user_id)
        if not valid_promotions:
            return None, 0

        best_promotion = max(
            valid_promotions,
            key=lambda p: p.calculate_discount(order_total)
        )
        return best_promotion, best_promotion.calculate_discount(order_total)

    def calculate_final_price(
        self,
        services: List[dict],
        promo_code: Optional[str] = None,
        user_location: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> dict:
        """Calculate final price with best applicable promotion"""
        original_price = self.calculate_total_price(services)
        promotion, discount = self.find_best_promotion(
            original_price, 
            promo_code, 
            user_location,
            user_id
        )

        return {
            "original_price": original_price,
            "discount_applied": discount,
            "final_price": original_price - discount,
            "promotion_used": promotion.code if promotion else None
        }
