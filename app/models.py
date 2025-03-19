from sqlalchemy import Column, Integer, String, Float, Date, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum
from .promotion_rules import PromotionRuleFactory

Base = declarative_base()

class PromotionRuleType(str, Enum):
    LOCATION = "location"
    ORDER = "order"
    USER = "user"

class Promotion(Base):
    __tablename__ = "promotions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_type = Column(String)  # 'fixed' or 'percentage'
    value = Column(Float)
    rule_type = Column(String)  # 'location', 'order', or 'user'
    rule_params = Column(JSON)  # Parameters specific to the rule type
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def is_valid(self, order_total: float, user_location: str = None, user_id: int = None) -> bool:
        """Check if promotion is valid based on conditions"""
        # Check expiry date
        now = datetime.now().date()
        if self.expiry_date and now > self.expiry_date:
            return False
            
        # Create and validate using the appropriate rule
        try:
            rule = PromotionRuleFactory.create_rule(self.rule_type, self.rule_params)
            return rule.is_valid(order_total, user_location, user_id)
        except ValueError:
            return False
        
    def calculate_discount(self, order_total: float) -> float:
        """Calculate discount amount based on promotion type"""
        if self.discount_type == "fixed":
            return self.value
        elif self.discount_type == "percentage":
            return (self.value / 100) * order_total
        return 0
