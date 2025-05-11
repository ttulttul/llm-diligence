from pydantic import Field, field_validator, BaseModel
from typing import List, Optional, Dict, Any
from datetime import date
from enum import Enum, auto
from .base import DiligentizerModel
import re

# Party to an Agreement
class AgreementParty(BaseModel):
    """Represents a party to a legal agreement."""
    party_name: Optional[str] = Field(None, description="The name of a party to an agreement")
    party_type: Optional[str] = Field(None, description="The type of party (e.g., individual, corporation, LLC)")
    party_address: Optional[str] = Field(None, description="The address of the party")

# Base class for all agreements
class Agreement(DiligentizerModel):
    """A legal document establishing rights and obligations between parties, including effective dates and governing law.
    This base class captures the fundamental elements common to all types of agreements, providing
    a foundation for more specialized agreement types like licenses, employment contracts, etc."""
    agreement_title: Optional[str] = Field(None, description="The title of the agreement")
    agreement_date: Optional[date] = Field(None, description="The date the agreement was signed or executed")
    effective_date: Optional[date] = Field(None, description="The date when the agreement becomes effective")
    parties: List[AgreementParty] = Field(default_factory=list, description="The parties involved in the agreement")
    governing_law: Optional[str] = Field(None, description="The jurisdiction's laws governing the agreement")
    term_description: Optional[str] = Field(None, description="Description of the agreement's term")

# Base class for commercial agreements
class CommercialAgreement(Agreement):
    """Base class for agreements that have a commercial nature between businesses or entities."""
    payment_terms: Optional[str] = Field(None, description="Description of payment terms")
    termination_provisions: Optional[str] = Field(None, description="Provisions for terminating the agreement")
    confidentiality_provisions: Optional[str] = Field(None, description="Provisions regarding confidentiality")

# Base class for customer agreements
class CustomerAgreement(CommercialAgreement):
    """A contractual arrangement where a provider delivers services or products to a customer under specific terms and conditions.
    This model represents commercial agreements between service/product providers and their customers,
    capturing key relationship details like term dates, renewal provisions, and party identification."""
    provider_name: str = Field(..., description="The name of the service provider entity")
    customer_name: str = Field(..., description="The name of the customer entity")
    start_date: Optional[date] = Field(None, description="The start date of the agreement")
    end_date: Optional[date] = Field(None, description="The end date of the agreement")
    auto_renews: Optional[bool] = Field(None, description="Whether the agreement automatically renews")
    renewal_terms: Optional[str] = Field(None, description="Description of renewal terms if applicable")

# Base class for license agreements
class LicenseAgreement(CommercialAgreement):
    """A legal agreement granting permission to use intellectual property or assets under specified conditions and restrictions.
    This model represents agreements that grant usage rights to intellectual property or other assets,
    capturing the licensor-licensee relationship and the scope and limitations of the granted rights."""
    licensor: str = Field(..., description="The party granting the license")
    licensee: str = Field(..., description="The party receiving the license")
    license_scope: Optional[str] = Field(None, description="The scope of the license grant")
    license_restrictions: Optional[List[str]] = Field(default_factory=list, description="Restrictions on the license")
    license_fee: Optional[str] = Field(None, description="Description of license fees")
    license_term: Optional[str] = Field(None, description="Term of the license")

# Base class for employment agreements
class EmploymentAgreement(Agreement):
    """A contract establishing the relationship between employer and employee, including work terms, compensation, and obligations.
    This model represents the formal agreement between an employer and employee, capturing essential
    employment details such as parties involved, start date, and compensation structure.
    Employment agreements are NOT appropriate to capture concepts like software license or service terms."""
    employer: str = Field(..., description="The employer entity")
    employee: str = Field(..., description="The employee name")
    start_date: Optional[date] = Field(None, description="Employment start date")
    compensation_description: Optional[str] = Field(None, description="Description of compensation terms")

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
    """Represents key details extracted from an employment agreement.
    This model captures the comprehensive terms of employment between an employer and employee,
    including job details, compensation structure, benefits, termination provisions, and restrictive
    covenants. It provides a structured representation of the rights, obligations, and conditions
    that govern the employment relationship, facilitating analysis of employment terms and conditions."""
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
