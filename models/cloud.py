from enum import Enum
from typing import Optional, List, Dict
from pydantic import Field
from .base import CustomerAgreement

class CloudServiceType(str, Enum):
    """Types of cloud services"""
    IAAS = "infrastructure as a service"
    PAAS = "platform as a service"
    SAAS = "software as a service"
    FAAS = "function as a service"
    DBAAS = "database as a service"
    STORAGE = "storage as a service"
    CAAS = "container as a service"

class CloudServiceAgreement(CustomerAgreement):
    """Base class for all cloud service agreements.
    This model represents contracts governing the provision of cloud-based services, capturing
    essential elements such as service type, SLA terms, data handling provisions, and termination
    conditions. It serves as the foundation for more specialized cloud service agreement types
    like IaaS, PaaS, and SaaS contracts."""
    service_type: CloudServiceType = Field(..., description="The type of cloud service provided")
    service_description: str = Field(..., description="Description of the cloud services provided")
    service_level_agreement_exists: bool = Field(False, description="Whether a service level agreement exists")
    data_processing_terms_exist: bool = Field(False, description="Whether data processing terms exist")
    acceptable_use_policy_exists: bool = Field(False, description="Whether an acceptable use policy exists")
    
    # Common cloud agreement fields
    termination_for_convenience_customer: bool = Field(True, description="Whether the customer can terminate without cause")
    termination_for_convenience_provider: bool = Field(False, description="Whether the provider can terminate without cause")
    data_deletion_upon_termination: bool = Field(True, description="Whether customer data is deleted upon termination")
    data_retrieval_period_days: Optional[int] = Field(None, description="Days allowed for data retrieval after termination")
