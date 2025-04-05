from pydantic import Field
from typing import List, Optional
from .base import DiligentizerModel

class EmploymentContract(DiligentizerModel):
    employer: str = Field(..., description="The employer's name")
    employee: str = Field(..., description="The employee's name")
    start_date: str = Field(..., description="Employment start date")
    salary: float = Field(..., description="Annual salary")
    benefits: List[str] = Field(default_factory=list, description="List of provided benefits")
    termination_clause: str = Field(..., description="Terms for contract termination")
