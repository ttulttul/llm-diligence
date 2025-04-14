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

