from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import re

# Import CommercialAgreement instead of CloudServiceAgreement
from .contracts import CommercialAgreement
# from .base import DiligentizerModel # Not directly, but through CloudServiceAgreement
# from .contracts import AgreementParty # For the 'parties' field, inherited.

class TermLetter(CommercialAgreement):
    """
    Represents a term letter, order form, or statement of work that details specific commercial terms
    for services, often supplementing a master service agreement.
    This model captures the specifics of a particular engagement, including selected service plans,
    pricing, subscription terms, and any deviations or additions to the main agreement.
    """
    # Fields that were previously inherited from CustomerAgreement
    provider_name: str = Field(..., description="The name of the service provider entity; this is usually found at the top of the letter next to 'From:'")
    customer_name: str = Field(..., description="The name of the customer entity; this is usually found at the top of the letter next to 'To:'")
    start_date: Optional[date] = Field(None, description="The start date of the agreement")
    end_date: Optional[date] = Field(None, description="The end date of the agreement")
    auto_renews: Optional[bool] = Field(None, description="Whether the agreement automatically renews")
    
    # Fields for cloud service specifics when applicable
    service_type: Optional[str] = Field(
        None,
        description="Type of cloud service (e.g., 'SaaS', 'IaaS', 'PaaS'); free-form text."
    )
    service_description: Optional[str] = Field(None, description="Description of the services provided")
    service_level_agreement_exists: bool = Field(False, description="Whether a service level agreement exists")
    data_processing_terms_exist: bool = Field(False, description="Whether data processing terms exist")
    acceptable_use_policy_exists: bool = Field(False, description="Whether an acceptable use policy exists")
    
    # Termination fields previously from CloudServiceAgreement
    data_deletion_upon_termination: bool = Field(True, description="Whether customer data is deleted upon termination")
    data_retrieval_period_days: Optional[int] = Field(None, description="Days allowed for data retrieval after termination")
    
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
    service_plans_ordered: List[str] = Field(
        default_factory=list,
        description="Names or identifiers of the service plans included in this order."
    )
    prepayment_terms_offered: List[str] = Field(
        default_factory=list,
        description="Descriptions of any pre-payment options offered."
    )

    # Termination convenience fields
    termination_for_convenience_customer: bool = Field(
        False,  # Defaulting to False as term letters often lock in for the term
        description="Whether the customer can terminate without cause. This might be restricted by the order form."
    )
    termination_for_convenience_provider: bool = Field(
        False,
        description="Whether the provider can terminate without cause."
    )


