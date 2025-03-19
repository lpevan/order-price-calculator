from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

class PromotionRule(ABC):
    @abstractmethod
    def is_valid(self, order_total: float, user_location: Optional[str] = None, user_id: Optional[int] = None) -> bool:
        pass

class LocationRule(PromotionRule):
    def __init__(self, required_location: str):
        self.required_location = required_location

    def is_valid(self, order_total: float, user_location: Optional[str] = None, user_id: Optional[int] = None) -> bool:
        return user_location and user_location.lower() == self.required_location.lower()

class OrderRule(PromotionRule):
    def __init__(self, min_order: float):
        self.min_order = min_order

    def is_valid(self, order_total: float, user_location: Optional[str] = None, user_id: Optional[int] = None) -> bool:
        return order_total >= self.min_order

class UserRule(PromotionRule):
    def __init__(self, user_ids: list[int]):
        self.user_ids = user_ids

    def is_valid(self, order_total: float, user_location: Optional[str] = None, user_id: Optional[int] = None) -> bool:
        
            return user_id in self.user_ids

class PromotionRuleFactory:
    @staticmethod
    def create_rule(rule_type: str, rule_params: dict) -> PromotionRule:
        if rule_type == "location":
            return LocationRule(rule_params.get("required_location"))
        elif rule_type == "order":
            return OrderRule(rule_params.get("min_order", 0))
        elif rule_type == "user":
            return UserRule(rule_params.get("user_ids", []))
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")
