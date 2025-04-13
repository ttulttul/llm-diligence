from pydantic import Field
from typing import List, Optional
from .base import DiligentizerModel, FinancialDocument

class FinancialStatement(FinancialDocument):
    revenue: float = Field(..., description="Total revenue for the period")
    expenses: float = Field(..., description="Total expenses for the period")
    net_income: float = Field(..., description="Net income for the period")
    cash_on_hand: float = Field(..., description="Cash on hand at the end of the period")
