from enum import Enum
from typing import Optional, List
from pydantic import Field
from .base import DiligentizerModel

class LicenseGrantType(str, Enum):
    USE = "use only"
    USE_AND_MODIFY = "use and modify"
    USE_MODIFY_DISTRIBUTE = "use, modify, and distribute"
    SAAS = "software as a service"
    DEVELOPMENT = "development only"
    EVALUATION = "evaluation only"
    PERPETUAL = "perpetual license"
    SUBSCRIPTION = "subscription"

class LicenseScope(str, Enum):
    UNLIMITED = "unlimited"
    NAMED_USERS = "limited to specific named users"
    CONCURRENT_USERS = "limited to concurrent users"
    CPU_BASED = "based on CPU count"
    DEVICE_LIMITED = "limited to specific devices"
    SITE_LICENSE = "entire site"
    ENTERPRISE = "entire enterprise"

class WarrantyType(str, Enum):
    NONE = "no warranty provided"
    LIMITED = "limited warranty"
    FITNESS_FOR_PURPOSE = "fitness for particular purpose"
    AS_DESCRIBED = "as described in documentation"
    PERFORMANCE = "performance warranty"
    SECURITY = "security warranty"

class LiabilityLimit(str, Enum):
    NONE = "no limitation"
    FEES_PAID = "limited to fees paid"
    FIXED_AMOUNT = "fixed monetary amount"
    EXCLUDED = "all liability excluded"
    PARTIAL_EXCLUSION = "partial exclusion of liability"

class DisputeResolutionMethod(str, Enum):
    LITIGATION = "litigation"
    ARBITRATION = "arbitration"
    MEDIATION_THEN_ARBITRATION = "mediation then arbitration"
    NEGOTIATION_THEN_LITIGATION = "negotiation then litigation"

class AcceptanceMechanism(str, Enum):
    CLICKWRAP = "clickwrap agreement"
    SIGNATURE = "signature required"
    PAYMENT = "payment constitutes acceptance"
    USE = "use constitutes acceptance"
    EMAIL_CONFIRMATION = "email confirmation"

class ChangeOfControlRestriction(str, Enum):
    NO_RESTRICTIONS = "no restrictions"
    CUSTOMER_CONSENT = "customer consent required"
    VENDOR_CONSENT = "vendor consent required"
    BOTH_PARTIES_CONSENT = "both parties consent required"

class PricePeriod(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi-annually"
    ANNUALLY = "annually"
    ONE_TIME = "one-time"

class TerminationProvision(str, Enum):
    NO_CAUSE_BOTH_PARTIES = "either party can terminate without cause"
    NO_CAUSE_LICENSOR_ONLY = "only licensor can terminate without cause"
    NO_CAUSE_LICENSEE_ONLY = "only licensee can terminate without cause"
    BREACH_ONLY = "can only terminate for material breach"
    BREACH_WITH_CURE_PERIOD = "can terminate for breach after cure period"
    CONVENIENCE_WITH_NOTICE = "can terminate for convenience with notice period"

class SoftwareLicenseAgreement(DiligentizerModel):
    # Parties and basic term information
    licensor: str = Field(..., description="The party granting the license")
    licensee: str = Field(..., description="The party receiving the license")
    start_date: str = Field(..., description="The start date of the license agreement")
    end_date: str = Field(..., description="The end date of the license agreement")
    auto_renews: bool = Field(..., description="Whether the license automatically renews after the end date")
    
    # License grant and scope
    license_grant: LicenseGrantType = Field(..., description="The type of rights being granted")
    license_scope: LicenseScope = Field(..., description="Limitations on users, devices, or installations")
    user_limit: Optional[int] = Field(None, description="Maximum number of users allowed if applicable")
    device_limit: Optional[int] = Field(None, description="Maximum number of devices allowed if applicable")
    
    # Payment terms
    minimum_price: float = Field(..., description="The minimum price of the license")
    price_period: PricePeriod = Field(..., description="The period for which the price applies")
    pre_payment_requirement: Optional[float] = Field(None, description="The pre-payment requirement amount, None if no pre-payment required")
    late_payment_interest: Optional[float] = Field(None, description="Interest rate for late payments, None if not specified")
    payment_due_days: Optional[int] = Field(None, description="Number of days after invoice when payment is due")
    
    # Intellectual property
    ip_ownership: str = Field("licensor", description="Who owns the intellectual property of the software")
    derivative_works_ownership: str = Field("licensor", description="Who owns any derivative works or modifications")
    
    # Warranties and liability
    warranty_type: WarrantyType = Field(..., description="Type of warranty provided")
    warranty_period_days: Optional[int] = Field(None, description="Duration of warranty in days, if applicable")
    liability_limit: LiabilityLimit = Field(..., description="Limitation on licensor's financial responsibility")
    liability_cap_amount: Optional[float] = Field(None, description="Maximum liability amount if specified")
    
    # Legal and compliance
    indemnification_by_licensor: bool = Field(False, description="Whether licensor indemnifies licensee")
    indemnification_by_licensee: bool = Field(False, description="Whether licensee indemnifies licensor")
    confidentiality_term_months: Optional[int] = Field(None, description="Duration of confidentiality obligation in months")
    governing_law_jurisdiction: str = Field(..., description="Legal jurisdiction that applies to the agreement")
    dispute_resolution: DisputeResolutionMethod = Field(..., description="Method for resolving disputes")
    force_majeure_clause: bool = Field(True, description="Whether force majeure clause is included")
    export_control_compliance: bool = Field(False, description="Whether export control compliance is required")
    
    # Assignment and termination
    change_of_control: ChangeOfControlRestriction = Field(..., description="The restriction type for change of control")
    assignment_allowed: bool = Field(False, description="Whether the license can be transferred to another entity")
    termination_provisions: TerminationProvision = Field(..., description="The provisions for terminating the agreement")
    
    # Maintenance, support, and usage
    maintenance_included: bool = Field(False, description="Whether maintenance is included in the license")
    support_level: Optional[str] = Field(None, description="Level of technical support provided")
    support_hours: Optional[str] = Field(None, description="Hours during which support is available")
    data_usage_rights: Optional[str] = Field(None, description="How licensor may use licensee's data")
    audit_rights: bool = Field(False, description="Whether licensor has right to audit license usage")
    reverse_engineering_allowed: bool = Field(False, description="Whether reverse engineering is permitted")
    
    # Agreement mechanics
    acceptance_mechanism: AcceptanceMechanism = Field(..., description="How agreement to terms is established")
    amendment_process: str = Field("written and signed by both parties", description="Process for changing agreement terms")
