from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import re

# Assuming .base and .cloud are available if this were in a package structure
# For the purpose of this output, I'll use relative imports if it was structured,
# but for a single block I might need to define or mock them.
# The problem provides base.py and contracts.py, and cloud.py
# This new model should import from cloud.py
from .cloud import CloudServiceAgreement, CloudServiceType # From cloud.py
# from .base import DiligentizerModel # Not directly, but through CloudServiceAgreement
# from .contracts import AgreementParty # For the 'parties' field, inherited.

# Sub-models for pricing and prepayment
class PricingTier(BaseModel):
    from_units: Optional[float] = Field(None, description="Lower bound of the tier (inclusive).")
    to_units: Optional[float] = Field(None, description="Upper bound of the tier (inclusive for 'to', exclusive for next 'from').")
    fee_per_unit: float = Field(..., description="Cost per unit within this tier.")
    unit_metric: str = Field(..., description="The unit being measured (e.g., 'Inbound Domain', 'GB').")
    currency: str = Field(..., description="Currency of the fee (e.g., USD, EUR).")
    tier_description: Optional[str] = Field(None, description="Additional description for this tier.")

class ServicePlanDetail(BaseModel):
    plan_name: Optional[str] = Field(None, description="Name of the service plan (e.g., 'Uber Plan (Discounted)').")
    service_category: str = Field(..., description="Category of the service (e.g., 'Outbound Filtering', 'Inbound Filtering').")
    description: Optional[str] = Field(None, description="General description of the plan or service item.")
    
    # For fixed or allowance-based plans
    included_units: Optional[float] = Field(None, description="Number of units included in the base fee (e.g., 50,000,000 Email Messages).")
    unit_metric: Optional[str] = Field(None, description="The unit for included_units and base_fee period (e.g., 'Email Messages', 'Domains').")
    period: Optional[str] = Field("per month", description="Billing period for the base fee (e.g., 'per month', 'per year').")
    base_fee: Optional[float] = Field(None, description="The base fee for the plan for the specified period.")
    
    # For overage/additional usage
    overage_fee_per_unit: Optional[float] = Field(None, description="Cost for units exceeding the allowance or for pay-as-you-go usage.")
    overage_unit_metric: Optional[str] = Field(None, description="The unit for overage fees (e.g., 'per thousand messages', 'per GB').")
    
    # Limits
    max_units: Optional[str] = Field(None, description="Maximum units allowed or 'Unlimited' (e.g., '65,000,000', 'Unlimited').") # str to allow "Unlimited"
    
    currency: Optional[str] = Field(None, description="Currency for base_fee and overage_fee (e.g., USD, EUR). If None, might use a default from the main agreement.")
    
    # For tiered pricing (like Inbound Filtering)
    pricing_tiers: List[PricingTier] = Field(default_factory=list, description="List of pricing tiers for usage-based services.")
    
    # Other specific details
    minimum_charge_description: Optional[str] = Field(None, description="Description of any minimum charges applicable (e.g., 'minimum of 20,000 Inbound Domains').")
    additional_features: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Key-value pairs for other features, e.g., 'Mailboxes Per Domain': 'Unlimited'.")


class PrepaymentTerm(BaseModel):
    prepayment_amount: float = Field(..., description="The amount pre-paid by the customer.")
    credit_amount: float = Field(..., description="The credit applied to the account for the prepayment.")
    currency: str = Field(..., description="Currency of the prepayment and credit (e.g., USD, EUR).")
    description: Optional[str] = Field(None, description="Additional details about the prepayment term.")

class TermLetter(CloudServiceAgreement):
    """
    Represents a term letter, order form, or statement of work that details specific commercial terms
    for cloud services, often supplementing a master service agreement.
    This model captures the specifics of a particular engagement, including selected service plans,
    pricing, subscription terms, and any deviations or additions to the main agreement.
    """
    # Override or refine fields from CloudServiceAgreement / CustomerAgreement if necessary
    # provider_name and customer_name are already in CustomerAgreement (and thus CloudServiceAgreement)
    # agreement_date, effective_date, start_date, end_date are inherited.
    
    # Term Letter specific fields
    order_form_title: Optional[str] = Field(description="The title of the order form or term letter document, e.g., 'MailChannels Standard Term Letter'.") # Renamed from agreement_title for clarity, but agreement_title is fine too.
                                                                                                                                                        # Sticking with `agreement_title` from base `Agreement` is fine. This is just a thought.
                                                                                                                                                        # Let's keep `agreement_title` as it's inherited.

    initial_subscription_term_description: str = Field(..., description="Description of the initial subscription term (e.g., '12 months', '1 year from Effective Date').")
    
    # auto_renews and renewal_terms are already in CustomerAgreement.
    # We can add more structured renewal info if needed:
    renewal_period_description: Optional[str] = Field(None, description="Description of each renewal period (e.g., '12 months').")
    cancellation_notice_period_days: Optional[int] = Field(None, description="Number of days notice required to prevent auto-renewal.")

    # Details about the main agreement this order form might reference
    referenced_master_agreement_title: Optional[str] = Field(None, description="Title of the main/master agreement this order form is subject to (e.g., 'Terms of Service', 'Master Services Agreement').")
    precedence_clause: Optional[str] = Field(None, description="Clause stating the order of precedence if this document conflicts with the master agreement.")

    # Detailed service and pricing information
    service_plans_ordered: List[ServicePlanDetail] = Field(default_factory=list, description="List of specific service plans and their pricing details included in this order.")
    prepayment_terms_offered: List[PrepaymentTerm] = Field(default_factory=list, description="List of available pre-payment options and their corresponding credits.")

    # Override termination_for_convenience_customer if the order form has specific terms
    # The default in CloudServiceAgreement is True. For the sample, it's False.
    termination_for_convenience_customer: bool = Field(
        description="Whether the customer can terminate without cause. This might be restricted by the order form.",
        default=False # Defaulting to False as term letters often lock in for the term.
    )

    # The example letter mentions the governing law is from Terms of Service.
    # governing_law is in Agreement, so it's inherited.
    # This order form might reiterate or specify it if different for the order.

    # Add the date parsing validator for relevant date fields
    # These fields are inherited: agreement_date, effective_date, start_date, end_date
    @field_validator('agreement_date', 'effective_date', 'start_date', 'end_date', mode='before')
    @classmethod
    def parse_date_str(cls, value):
        if isinstance(value, str):
            from datetime import datetime # Local import to keep it self-contained if validator is copied
            
            # Handle "Nth" day ordinal like "June 9th, 2025"
            cleaned_value = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', value)
            
            formats_to_try = [
                "%B %d, %Y",  # June 9, 2025
                "%Y-%m-%d",   # 2025-06-09
                "%m/%d/%Y",   # 06/09/2025
                "%d %B %Y",   # 9 June 2025
                "%B %d %Y",   # June 9 2025 (if comma is missing)
                # Add other common formats as needed
            ]
            for fmt in formats_to_try:
                try:
                    return datetime.strptime(cleaned_value, fmt).date()
                except ValueError:
                    continue
            # If parsing fails, Pydantic might raise its own error, or we can raise/log here.
            # Returning the original value might lead to Pydantic's internal validation error for date type.
            # For stricter parsing, raise ValueError:
            # raise ValueError(f"Date string '{value}' could not be parsed into a valid date.")
            return value # Let Pydantic handle it or fail if unparseable
        return value

    # Example: Set service_type to SAAS by default if these order forms are typically for SaaS
    # service_type: CloudServiceType = Field(CloudServiceType.SAAS, description="The type of cloud service provided")
    # CloudServiceAgreement already requires service_type, so the instance must provide it.
    # It might be good to set a default if these order forms usually refer to a specific type like SaaS.
    # For MailChannels, it's SaaS.
    # However, an "Order Form" could be for IaaS or PaaS too. So, better to not default it here
    # and let it be specified during instantiation, or let the CloudServiceAgreement base handle it.
    # The base CloudServiceAgreement has `service_type: CloudServiceType = Field(..., description=...)`
    # This means it's a required field.
