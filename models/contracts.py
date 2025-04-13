from pydantic import Field, field_validator, BaseModel
from typing import List, Optional
from datetime import date
from .base import DiligentizerModel, EmploymentAgreement
import re

class Salary(BaseModel):
    """Represents salary details"""
    annual_amount: float = Field(..., description="The gross annual salary amount.")
    currency: str = Field(..., description="The currency of the salary (e.g., CAD, USD).")
    payment_frequency: Optional[str] = Field(None, description="How often the salary is paid (e.g., 'semi-monthly', 'bi-weekly', 'monthly').")
    effective_date: Optional[date] = Field(None, description="The date from which this salary amount is effective.")

class Bonus(BaseModel):
    """Represents bonus details"""
    description: str = Field(..., description="Description of the bonus structure (e.g., performance-based, signing bonus).")
    amount: Optional[float] = Field(None, description="The specific bonus amount, if fixed.")
    max_amount: Optional[float] = Field(None, description="The maximum possible bonus amount, if variable (e.g., 'up to' amount).")
    currency: Optional[str] = Field(None, description="The currency of the bonus.")
    timing: Optional[str] = Field(None, description="When the bonus is typically paid or assessed (e.g., 'end of March each year', 'within 10 days of execution').")
    conditions: Optional[str] = Field(None, description="Conditions for receiving the bonus (e.g., 'at the sole discretion of the Company', 'upon successful completion of probation').")

class TerminationClauses(BaseModel):
    """Details regarding contract termination"""
    for_cause: Optional[str] = Field(None, description="Conditions and consequences of termination for just cause.")
    without_cause_employer: Optional[str] = Field(None, description="Conditions and notice/pay requirements for termination by the employer without just cause (e.g., reference to statutory minimums like BC Employment Standards Act).")
    resignation_employee: Optional[str] = Field(None, description="Notice period required for employee resignation (e.g., 'two weeks prior written notice').")

class RestrictiveCovenants(BaseModel):
    """Details on non-solicitation, non-competition, etc."""
    non_solicitation_duration_months: Optional[int] = Field(None, description="Duration in months post-termination for non-solicitation clause.")
    non_solicitation_scope: Optional[str] = Field(None, description="Description of who/what cannot be solicited (e.g., employees, clients, suppliers).")
    non_competition_duration_months: Optional[int] = Field(None, description="Duration in months post-termination for non-competition clause.")
    non_competition_scope: Optional[str] = Field(None, description="Description of the scope of the non-competition clause (e.g., geographic area, type of business).")
    confidentiality_clause_present: Optional[bool] = Field(None, description="Indicates if a confidentiality clause or agreement is referenced/included.")
    intellectual_property_assignment: Optional[bool] = Field(None, description="Indicates if there's a clause assigning IP created during employment to the employer.")

class EmploymentContract(EmploymentAgreement):
    """Represents key details extracted from an employment agreement."""
    job_title: Optional[str] = Field(None, description="The employee's job title.")
    
    agreement_date: Optional[date] = Field(None, description="The date the agreement was signed or executed.")
    # Use original_start_date if the agreement supersedes a previous one but maintains seniority
    original_start_date: Optional[date] = Field(None, description="The employee's original start date with the employer, if different from the agreement date (relevant for continuous service).") 
    # Use effective_start_date for when *this specific contract* term begins
    effective_start_date: Optional[date] = Field(None, description="Employment start date under *this* specific agreement, if specified.")
    
    # Override parties from Agreement base class
    parties: List[str] = Field(default_factory=list, description="The parties involved in the agreement (employer and employee)")

    salary: Salary = Field(..., description="Details about the employee's salary.")
    
    bonuses: List[Bonus] = Field(default_factory=list, description="List of applicable bonuses (e.g., signing, performance).")
    
    benefits_description: Optional[str] = Field(None, description="General description of entitlement to benefits (e.g., 'participate in group insurance plan'). Specific benefits often listed elsewhere.")
    vacation_policy_description: Optional[str] = Field(None, description="Description of vacation entitlement or reference to policy (e.g., 'Accrued per BC Employment Standards Act and company policy').")
    
    termination_clauses: Optional[TerminationClauses] = Field(None, description="Details regarding contract termination conditions.")
    
    restrictive_covenants: Optional[RestrictiveCovenants] = Field(None, description="Details on non-solicitation, non-competition, confidentiality, and IP clauses.")

    governing_law: Optional[str] = Field(None, description="The jurisdiction's laws governing the agreement (e.g., 'Province of British Columbia').")
    
    on_call_requirements: Optional[str] = Field(None, description="Description of any on-call duties or requirements mentioned.")
    
    appendices_referenced: List[str] = Field(default_factory=list, description="List of appendices mentioned or attached to the agreement.")

    # Validator to attempt parsing dates from string representations if needed
    @field_validator('agreement_date', 'original_start_date', 'effective_start_date', mode='before')
    @classmethod
    def parse_date_str(cls, value):
        if isinstance(value, str):
            # Simple attempt to parse common formats, can be expanded
            # Example: "April 3, 2025", "2025-04-03", "04/03/2025" 
            # This is a basic example; a robust solution would use dateutil.parser
            from datetime import datetime 
            formats_to_try = ["%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%d day of %B %Y"] 
            for fmt in formats_to_try:
                try:
                    # Handle "3rd", "1st" etc. by removing suffix before parsing
                    cleaned_value = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', value)
                    return datetime.strptime(cleaned_value, fmt).date()
                except ValueError:
                    continue
            # If parsing fails, raise or return None/original value based on desired strictness
            # For flexibility, returning original string might be okay if direct date objects aren't always guaranteed
            # raise ValueError(f"Could not parse date: {value}") 
            return value # Return original if unparseable by simple formats
        return value
