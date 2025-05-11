from pydantic import Field, field_validator
from typing import List, Optional
from datetime import date
from .base import DiligentizerModel
import re


# Base class for all agreements
class Agreement(DiligentizerModel):
    """A legal document establishing rights and obligations between parties, including effective dates and governing law.
    This base class captures the fundamental elements common to all types of agreements, providing
    a foundation for more specialized agreement types like licenses, employment contracts, etc."""
    agreement_title: Optional[str] = Field(None, description="The title of the agreement")
    agreement_date: Optional[date] = Field(None, description="The date the agreement was signed or executed")
    effective_date: Optional[date] = Field(None, description="The date when the agreement becomes effective")
    parties: List[str] = Field(default_factory=list, description="Names of the parties involved in the agreement")
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

    salary_amount: Optional[float] = Field(None, description="Gross annual salary amount")
    salary_currency: Optional[str] = Field(None, description="Currency of the salary (e.g., CAD, USD)")
    salary_payment_frequency: Optional[str] = Field(None, description="Salary payment frequency (e.g., bi-weekly)")
    salary_effective_date: Optional[date] = Field(None, description="Date from which the salary amount is effective")

    bonuses: List[str] = Field(default_factory=list, description="Descriptions of any bonuses (signing, performance, etc.)")
    
    benefits_description: Optional[str] = Field(None, description="General description of entitlement to benefits (e.g., 'participate in group insurance plan'). Specific benefits often listed elsewhere.")
    vacation_policy_description: Optional[str] = Field(None, description="Description of vacation entitlement or reference to policy (e.g., 'Accrued per BC Employment Standards Act and company policy').")
    
    termination_for_cause: Optional[str] = Field(None, description="Conditions/consequences of termination for cause")
    termination_without_cause_employer: Optional[str] = Field(None, description="Conditions for termination by employer without cause")
    resignation_employee_notice: Optional[str] = Field(None, description="Notice period required for employee resignation")
    
    non_solicitation_duration_months: Optional[int] = Field(None, description="Months for non-solicitation restriction")
    non_solicitation_scope: Optional[str] = Field(None, description="Scope of non-solicitation restriction")
    non_competition_duration_months: Optional[int] = Field(None, description="Months for non-compete restriction")
    non_competition_scope: Optional[str] = Field(None, description="Scope of non-compete restriction")
    confidentiality_clause_present: Optional[bool] = Field(None, description="True if a confidentiality clause is present")
    intellectual_property_assignment: Optional[bool] = Field(None, description="True if IP assignment clause is present")

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
