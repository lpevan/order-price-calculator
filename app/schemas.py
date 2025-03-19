from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Union
from datetime import date
from .models import PromotionRuleType


class Service(BaseModel):
    id: int
    name: str
    price: float

class PriceCalculationRequest(BaseModel):
    user_id: int
    services: List[Service]
    promo_code: Optional[str] = None
    location: Optional[str] = None

class PriceCalculationResponse(BaseModel):
    original_price: float
    discount_applied: float
    final_price: float
    promotion_used: Optional[str] = None

class PromotionBase(BaseModel):
    code: str
    discount_type: str
    value: float
    rule_type: str
    rule_params: Dict[str, Union[str, float, List[int]]]
    expiry_date: Optional[date] = None

    @validator('rule_type')
    def validate_rule_type(cls, v):
        if v not in [rule_type.value for rule_type in PromotionRuleType]:
            raise ValueError(f'Invalid rule type. Must be one of: {[rt.value for rt in PromotionRuleType]}')
        return v

    @validator('discount_type')
    def validate_discount_type(cls, v):
        if v not in ['fixed', 'percentage']:
            raise ValueError('discount_type must be either "fixed" or "percentage"')
        return v

    @validator('rule_params')
    def validate_rule_params(cls, v, values):
        rule_type = values.get('rule_type')
        if rule_type == PromotionRuleType.LOCATION:
            if 'required_location' not in v:
                raise ValueError('Location rule requires "required_location" parameter')
        elif rule_type == PromotionRuleType.ORDER:
            if 'min_order' not in v:
                raise ValueError('Order rule requires "min_order" parameter')
        elif rule_type == PromotionRuleType.USER:
            if 'user_ids' not in v or not isinstance(v['user_ids'], list):
                raise ValueError('User rule requires "user_ids" parameter as a list')
        return v

class PromotionCreate(PromotionBase):
    pass

class Promotion(PromotionBase):
    id: int
    created_at: date

    class Config:
        orm_mode = True
