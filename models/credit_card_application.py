import re
import importlib
import inspect
import pkgutil
import sys
from datetime import datetime, date
from enum import Enum, auto
from typing import Optional, Dict, Any, List, Type, Union

from pydantic import BaseModel, Field, field_serializer, field_validator

from .base import DiligentizerModel, FinancialDocument
from .contracts import AgreementParty

class ApplicationStatusType(str, Enum):
    """Whether the application is new or an increase."""
    NEW = "new_application"
    INCREASE = "increase_request"

class BusinessStructureType(str, Enum):
    """Legal structure of the business."""
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"
    CORPORATION = "corporation"
    OTHER = "other"

class BusinessType(str, Enum):
    """Categorization of the business's main activity."""
    RETAIL = "retail"
    RESTAURANT_BAR = "restaurant_bar"
    WHOLESALE = "wholesale"
    MANUFACTURING = "manufacturing"
    FARMING_FORESTRY_FISHING = "farming_forestry_fishing"
    FINANCE_INSURANCE_REAL_ESTATE = "finance_insurance_real_estate"
    TRANSPORTATION = "transportation"
    SERVICE = "service"
    CONSTRUCTION = "construction"
    SOFTWARE = "software"
    OTHER = "other"

class FinancialSummarySource(str, Enum):
    """Source of the financial data provided in the summary."""
    LATEST_FISCAL_YEAR_END = "latest_fiscal_year_end"
    PROJECTED_STATEMENTS = "projected_financial_statements"
    APPRAISAL = "most_recent_appraisal"

class HousingStatusType(str, Enum):
    """Owner's residential status."""
    OWN = "own"
    RENT = "rent"

class RequestedLoanProduct(BaseModel):
    """Details of a specific loan product requested."""
    product_name: str = Field(..., description="Name of the requested loan product (e.g., 'VISA* CreditLine for small business')")
    requested_amount: Optional[float] = Field(None, description="Specific amount requested for this product")
    maximum_amount: Optional[float] = Field(None, description="Maximum allowable amount for this product type, if stated on the form")
    is_selected: bool = Field(False, description="Whether this product was checked/selected on the application")

class BusinessFinancialSummary(BaseModel):
    """Summary of the business's financial information provided in the application."""
    source_description: Optional[FinancialSummarySource] = Field(None, description="Source of the financial summary data (e.g., latest fiscal year end)")
    source_date_description: Optional[str] = Field(None, description="Specific date related to the source (e.g., '12 months ending (M/D/Y)')")
    total_gross_annual_sales_revenue: Optional[float] = Field(None, description="Total Gross Annual Sales/Revenue figure provided")
    total_business_debt: Optional[float] = Field(None, description="Total Business Debt figure provided")
    net_after_tax_profit_loss: Optional[float] = Field(None, description="Net After Tax Profit or (Loss) figure provided")
    prior_adverse_events: bool = Field(..., description="Whether the business has ever been party to claim/lawsuit, owed back taxes, been in receivership or declared bankruptcy")
    adverse_event_details: Optional[str] = Field(None, description="Details provided if prior adverse events occurred")

class OwnerAssetItem(BaseModel):
    """An item listed in the owner's assets section."""
    asset_type: str = Field(..., description="Type of asset (e.g., 'Cash & Marketable Securities', 'RRSP/Retirement Accounts', 'Real Estate', 'Other Assets')")
    balance: float = Field(..., description="Balance or value of the asset")

class OwnerLiabilityItem(BaseModel):
    """An item listed in the owner's liabilities section."""
    liability_type: str = Field(..., description="Type of liability (e.g., 'Credit Cards', 'Bank Loans and Lines of Credit', 'Real Estate Mortgage(s)', 'Other Debt/Loans/Liabilities')")
    balance: float = Field(..., description="Balance of the liability")
    monthly_payment: Optional[float] = Field(None, description="Monthly payment amount for the liability")

class OwnerPersonalNetWorth(BaseModel):
    """Calculation of the owner's personal net worth as provided."""
    assets: List[OwnerAssetItem] = Field(default_factory=list, description="List of owner's assets")
    total_assets: Optional[float] = Field(None, description="Total calculated assets provided on the form")
    liabilities: List[OwnerLiabilityItem] = Field(default_factory=list, description="List of owner's liabilities")
    total_liabilities: Optional[float] = Field(None, description="Total calculated liabilities provided on the form")

class OwnerRealEstateDetail(BaseModel):
    """Details about real estate owned by the applicant owner."""
    property_index: int = Field(..., description="Identifier for the property listed (e.g., 1 or 2)")
    address: Optional[str] = Field(None, description="Full address of the real estate property")
    year_purchased: Optional[int] = Field(None, description="Year the property was purchased")
    purchase_price: Optional[float] = Field(None, description="Purchase price of the property")
    registered_owners: Optional[List[str]] = Field(default_factory=list, description="Names of registered owners")

class ApplicantOwnerInfo(AgreementParty):
    """Detailed information about an owner/partner applying for the loan."""
    party_type: Optional[str] = Field("Owner/Partner", description="Type of party (always Owner/Partner for this context)") # Override from base
    party_name: Optional[str] = Field(None, description="Full name of the owner/partner") # Explicitly add description
    is_existing_customer: Optional[bool] = Field(None, description="Whether the owner is an existing customer of the financial institution")
    customer_since: Optional[str] = Field(None, description="Date (m/d/y) the owner became a customer, if applicable (kept as string due to ambiguous format)")
    client_card_number: Optional[str] = Field(None, description="Owner's client card number, if applicable (potentially masked)")
    party_address: Optional[str] = Field(None, description="Owner's current home address") # Inherited from AgreementParty
    previous_home_address: Optional[str] = Field(None, description="Previous home address if at current address less than 2 years")
    birth_date: Optional[date] = Field(None, description="Owner's date of birth")
    social_insurance_number: Optional[str] = Field(None, description="Owner's Social Insurance Number (optional, likely masked or omitted)")
    drivers_license_number: Optional[str] = Field(None, description="Owner's Driver's License number")
    home_telephone: Optional[str] = Field(None, description="Owner's home telephone number")
    security_verification_word: Optional[str] = Field(None, description="Verification word for security purposes")
    personal_gross_annual_income: Optional[float] = Field(None, description="Total personal gross annual income from last year's tax return (line 150)")
    income_year: Optional[int] = Field(None, description="The tax year corresponding to the personal gross annual income figure")
    net_worth_calculation: Optional[OwnerPersonalNetWorth] = Field(None, description="Owner's personal net worth calculation details")
    housing_status: Optional[HousingStatusType] = Field(None, description="Whether the owner owns or rents their home")
    monthly_housing_payment: Optional[float] = Field(None, description="Owner's monthly mortgage or rent payment")
    mortgage_holder: Optional[str] = Field(None, description="Entity holding the mortgage, if applicable and owner owns")
    real_estate_details: List[OwnerRealEstateDetail] = Field(default_factory=list, description="Details of real estate owned by this owner")
    prior_personal_adverse_events_details: Optional[str] = Field(None, description="Details of any claim/lawsuit, prior bankruptcy, or currently owed back taxes for the owner/partner")


class CreditCardApplication(FinancialDocument):
    """Model representing a borrowing application focusing on
    requests for credit facilities like credit cards or lines of credit."""

    # Document Metadata
    document_id: Optional[str] = Field(None, description="Form identifier (e.g., E-FORM 89064)")
    document_version_date: Optional[str] = Field(None, description="Version date of the form (e.g., 03/2009)")

    # Section 1: Loan Request
    application_status: Optional[ApplicationStatusType] = Field(None, description="Whether this is a new application or an increase request")
    purpose_of_loan: Optional[str] = Field(None, description="The stated purpose for the loan/credit facility")
    requested_products: List[RequestedLoanProduct] = Field(default_factory=list, description="List of all loan products offered on the form and details of selection/amount requested")

    # Section 2: About the Business
    correspondence_address_preference: Optional[str] = Field(None, description="Preferred mailing address for correspondence ('Business' or 'Home')")
    referred_by_third_party: Optional[bool] = Field(None, description="Was the application referred by a third party?")
    referrer_name: Optional[str] = Field(None, description="Name of the referrer, if applicable")
    is_existing_client: Optional[bool] = Field(None, description="Is the Business currently a client of the financial institution?")
    account_number: Optional[str] = Field(None, description="Business Account Number with the financial institution, if applicable")
    branch_transit: Optional[str] = Field(None, description="Branch Transit number for the account, if applicable")
    primary_financial_institution_details: Optional[str] = Field(None, description="Name and address of primary financial institution if not a client")

    # Section 2(ii): Business Information
    main_business_type: Optional[BusinessType] = Field(None, description="Main type of business activity")
    business_type_other_description: Optional[str] = Field(None, description="Description if 'Other' business type is selected")
    is_franchise: Optional[bool] = Field(None, description="Is the business a franchise?")
    nature_of_business_description: Optional[str] = Field(None, description="Brief description of the nature of the business or type of farm")
    date_established: Optional[date] = Field(None, description="Month and Year the business was established")
    current_ownership_since: Optional[date] = Field(None, description="Month and Year the current ownership structure began")
    number_of_employees: Optional[int] = Field(None, description="Number of employees")
    business_structure: Optional[BusinessStructureType] = Field(None, description="Legal structure of the business")
    business_structure_other_description: Optional[str] = Field(None, description="Description if 'Other' business structure is selected")
    # company_name inherited from FinancialDocument, represents Full Business Name
    business_trading_name: Optional[str] = Field(None, description="Trading name if different from the legal name")
    is_trading_name_registered: Optional[bool] = Field(None, description="Is the trading name registered?")
    business_address: Optional[str] = Field(None, description="Full street address of the business (Street, City, Province, Postal Code)")
    business_telephone: Optional[str] = Field(None, description="Business telephone number")
    business_fax: Optional[str] = Field(None, description="Business fax number")
    business_email: Optional[str] = Field(None, description="Business email address")
    assets_on_indian_reserve: Optional[bool] = Field(None, description="Are the assets of this business located on an Indian Reserve?")
    ownership_structure_description: Optional[str] = Field(None, description="Description of owners/partners and their percentage ownership (e.g., 'Ken Simpson, 35%; Investors and employees, 65%')")

    # Section 2(iii): Financial Summary
    financial_summary: Optional[BusinessFinancialSummary] = Field(None, description="Summary of the business's financials provided on the form")

    # Section 3: Owner/Partner Information
    # Multiple owners can be represented by adding more items to this list
    owners: List[ApplicantOwnerInfo] = Field(default_factory=list, description="List of owners/partners providing personal information and guarantees")

    # Section 4: Agreement and Signatures
    application_signed_date: Optional[date] = Field(None, description="Date the application form was signed")
    # Storing actual signatures isn't feasible, but we can note if fields were signed
    authorized_officer_signed: Optional[bool] = Field(None, description="Indicates if the authorized officer signature block appears signed")
    owner_partner_signed: Optional[bool] = Field(None, description="Indicates if the owner/partner signature block appears signed")
    signed_business_name: Optional[str] = Field(None, description="Printed name of the business in the signature section")


    # Meta fields from base class customization
    currency: Optional[str] = Field("CAD", description="Currency used in the financial figures (Default: CAD)") # Override default None
    fiscal_year: Optional[str] = Field(None, description="Fiscal year corresponding to the financial summary, if derivable") # Inherited, maybe useful

    # --- Validators for Date Parsing ---

    @field_validator('date_established', 'current_ownership_since', mode='before', check_fields=False)
    @classmethod
    def parse_my_date(cls, value):
        """Attempts to parse M/Y or MM/YY format to a date (using 1st of month)."""
        if isinstance(value, str):
            value = value.strip()
            if not value: return None
            try:
                # Try MM/YY format first
                dt = datetime.strptime(value, '%m/%y')
                # Adjust year for YY format (e.g., 04 -> 2004, 99 -> 1999)
                current_year_last_two_digits = datetime.now().year % 100
                # If the parsed year (e.g., 77) is greater than current year's last two digits + buffer (e.g. 24 + 10 = 34), assume it's previous century
                buffer = 10 # Adjust buffer as needed
                if dt.year % 100 > current_year_last_two_digits + buffer:
                     dt = dt.replace(year=dt.year - 100)
                else:
                    # If parsed year is small (e.g. 04), ensure it's 20xx not 19xx
                    if dt.year < 1900: # Check if strptime defaulted badly
                         dt = dt.replace(year=dt.year + 100 if dt.year < (current_year_last_two_digits + buffer) else 0) # Basic century logic
                         if dt.year < 1950 : # Safety check for very old dates if logic is flawed
                             dt = dt.replace(year=dt.year + 100)


                return dt.date()
            except ValueError:
                pass # Continue to next format
            try:
                # Try MM/YYYY format
                return datetime.strptime(value, '%m/%Y').date()
            except ValueError:
                 print(f"Warning: Could not parse M/Y date format: {value}")
                 return None # Or raise error, or return original string
        elif isinstance(value, date):
            return value
        return None

    @field_validator('birth_date', 'application_signed_date', mode='before', check_fields=False)
    @classmethod
    def parse_full_date(cls, value):
        """Attempts to parse M/D/Y or similar full date formats."""
        if isinstance(value, str):
             value = value.strip()
             if not value: return None
             # Handle formats like M/D/Y, MM/DD/YY, MM/DD/YYYY
             formats_to_try = ["%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d"] # Add more formats if needed
             for fmt in formats_to_try:
                  try:
                     dt = datetime.strptime(value, fmt)
                     # Handle YY format ambiguity (e.g., 77 -> 1977, 09 -> 2009)
                     if fmt == "%m/%d/%y":
                        current_year_last_two_digits = datetime.now().year % 100
                        buffer = 10 # Adjust buffer as needed
                        if dt.year % 100 > current_year_last_two_digits + buffer:
                            dt = dt.replace(year=dt.year - 100)
                        else:
                            # Ensure small years are 20xx
                             if dt.year < 1900: # Check if strptime defaulted badly
                                dt = dt.replace(year=dt.year + 100 if dt.year < (current_year_last_two_digits + buffer) else 0) # Basic century logic
                                if dt.year < 1950 : # Safety check for very old dates if logic is flawed
                                    dt = dt.replace(year=dt.year + 100)


                     return dt.date()
                  except ValueError:
                     continue
             print(f"Warning: Could not parse full date format: {value}")
             return None # Or raise error, or return original string
        elif isinstance(value, date):
            return value
        return None

    @field_validator('income_year', mode='before', check_fields=False)
    @classmethod
    def parse_year(cls, value):
        """Attempts to parse a year, accepting string or int."""
        if isinstance(value, str):
            value = value.strip()
            # Extract potential YYYY from strings like "105,000 (2007)"
            match = re.search(r'\(?(\d{4})\)?$', value)
            if match:
                year_str = match.group(1)
                try:
                    year_int = int(year_str)
                    if 1900 < year_int < 2100:
                        return year_int
                except ValueError:
                    pass
            # Try direct conversion if string is just digits
            if re.fullmatch(r'\d{4}', value):
                 try:
                     year_int = int(value)
                     if 1900 < year_int < 2100:
                          return year_int
                 except ValueError:
                     pass
            print(f"Warning: Could not parse year from: {value}")
            return None
        elif isinstance(value, int):
            if 1900 < value < 2100:
                return value
            else:
                 print(f"Warning: Year out of reasonable range: {value}")
                 return None
        return None
