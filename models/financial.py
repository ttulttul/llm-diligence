from pydantic import Field
from typing import List, Optional
from .base import DiligentizerModel, FinancialDocument

class FinancialStatement(FinancialDocument):
    """A formal record of the financial activities and position of a business, individual, or other entity.
    This model captures key financial metrics including revenue, expenses, net income, and cash position,
    providing a snapshot of the entity's financial performance and status for a specific reporting period."""
    revenue: float = Field(..., description="Total revenue for the period")
    expenses: float = Field(..., description="Total expenses for the period")
    net_income: float = Field(..., description="Net income for the period")
    cash_on_hand: float = Field(..., description="Cash on hand at the end of the period")
