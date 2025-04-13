from enum import Enum
from typing import Optional, List, Dict
from pydantic import Field
from .base import DiligentizerModel, LicenseAgreement

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

class ExclusivityType(str, Enum):
    NONE = "no exclusivity"
    FULL = "full exclusivity"
    GEOGRAPHIC = "geographic exclusivity"
    INDUSTRY = "industry-specific exclusivity"
    TIME_LIMITED = "time-limited exclusivity"
    PARTIAL = "partial exclusivity with exceptions"

class RevenueRecognitionType(str, Enum):
    UPFRONT = "recognized upfront"
    RATABLE = "recognized ratably over term"
    MILESTONE = "recognized upon milestones"
    USAGE_BASED = "recognized based on usage"
    HYBRID = "hybrid recognition model"

class ServiceLevelAgreementType(str, Enum):
    NONE = "no SLA"
    AVAILABILITY = "availability guarantee only"
    RESPONSE_TIME = "response time guarantee"
    RESOLUTION_TIME = "resolution time guarantee"
    COMPREHENSIVE = "comprehensive SLA with multiple metrics"
    TIERED = "tiered SLA based on customer level"

class DataPrivacyRegime(str, Enum):
    MINIMAL = "minimal data protection"
    GDPR = "GDPR compliance required"
    CCPA = "CCPA compliance required"
    HIPAA = "HIPAA compliance required"
    MULTI_REGIME = "multiple data protection regimes"
    CUSTOM = "custom data protection requirements"

class NonCompeteType(str, Enum):
    NONE = "no non-compete provisions"
    GEOGRAPHIC = "geographic non-compete"
    INDUSTRY = "industry-specific non-compete"
    CUSTOMER = "customer-specific non-compete"
    TIME_LIMITED = "time-limited non-compete"
    COMPREHENSIVE = "comprehensive non-compete"

class SourceCodeEscrowType(str, Enum):
    NONE = "no source code escrow"
    BANKRUPTCY_ONLY = "release upon bankruptcy only"
    END_OF_SUPPORT = "release upon end of support"
    MATERIAL_BREACH = "release upon material breach"
    ACQUISITION = "release upon acquisition"
    COMPREHENSIVE = "comprehensive release conditions"

class TransitionServiceType(str, Enum):
    NONE = "no transition services"
    BASIC = "basic knowledge transfer only"
    STANDARD = "standard transition assistance"
    EXTENDED = "extended transition support"
    COMPREHENSIVE = "comprehensive transition services"

class MaterialAdverseChangeType(str, Enum):
    NONE = "no MAC provisions"
    STANDARD = "standard MAC clause"
    FINANCIAL_ONLY = "financial condition MAC only"
    PERFORMANCE_ONLY = "performance-related MAC only"
    INDUSTRY_SPECIFIC = "industry-specific MAC provisions"
    EXTENSIVE = "extensive MAC provisions"

class AssignmentProvisionType(str, Enum):
    PROHIBITED = "assignment prohibited"
    WITH_CONSENT = "assignment with consent"
    AFFILIATE_ONLY = "assignment to affiliates only"
    UNRESTRICTED = "unrestricted assignment"
    ACQUIRER_SPECIFIC = "specific acquirer restrictions"

class SoftwareLicenseAgreement(LicenseAgreement):
    # Parties and basic term information
    start_date: str = Field(..., description="The start date of the license agreement")
    end_date: str = Field(..., description="The end date of the license agreement")
    auto_renews: bool = Field(..., description="Whether the license automatically renews after the end date")
    renewal_notice_days: Optional[int] = Field(None, description="Days notice required to prevent automatic renewal")
    renewal_term_months: Optional[int] = Field(None, description="Duration of renewal term in months")
    
    # License grant and scope
    license_grant: LicenseGrantType = Field(..., description="The type of rights being granted")
    license_scope: LicenseScope = Field(..., description="Limitations on users, devices, or installations")
    user_limit: Optional[int] = Field(None, description="Maximum number of users allowed if applicable")
    device_limit: Optional[int] = Field(None, description="Maximum number of devices allowed if applicable")
    exclusivity: ExclusivityType = Field(ExclusivityType.NONE, description="Exclusivity arrangements that might limit future business")
    exclusivity_details: Optional[str] = Field(None, description="Details of exclusivity arrangements")
    
    # Payment terms
    minimum_price: float = Field(..., description="The minimum price of the license")
    price_period: PricePeriod = Field(..., description="The period for which the price applies")
    pre_payment_requirement: Optional[float] = Field(None, description="The pre-payment requirement amount, None if no pre-payment required")
    late_payment_interest: Optional[float] = Field(None, description="Interest rate for late payments, None if not specified")
    payment_due_days: Optional[int] = Field(None, description="Number of days after invoice when payment is due")
    revenue_recognition: RevenueRecognitionType = Field(RevenueRecognitionType.UPFRONT, description="How revenue is recognized")
    minimum_purchase_commitment: Optional[float] = Field(None, description="Minimum purchase or spend commitment")
    most_favored_nation: bool = Field(False, description="Whether MFN pricing provisions apply")
    most_favored_nation_scope: Optional[str] = Field(None, description="Scope of MFN provisions if applicable")
    
    # Intellectual property
    ip_ownership: str = Field("licensor", description="Who owns the intellectual property of the software")
    derivative_works_ownership: str = Field("licensor", description="Who owns any derivative works or modifications")
    source_code_escrow: SourceCodeEscrowType = Field(SourceCodeEscrowType.NONE, description="Source code escrow arrangements")
    source_code_escrow_details: Optional[str] = Field(None, description="Details of source code escrow if applicable")
    
    # Warranties and liability
    warranty_type: WarrantyType = Field(..., description="Type of warranty provided")
    warranty_period_days: Optional[int] = Field(None, description="Duration of warranty in days, if applicable")
    liability_limit: LiabilityLimit = Field(..., description="Limitation on licensor's financial responsibility")
    liability_cap_amount: Optional[float] = Field(None, description="Maximum liability amount if specified")
    
    # Service levels and performance
    service_level_agreement: ServiceLevelAgreementType = Field(ServiceLevelAgreementType.NONE, description="Type of SLA provided")
    service_level_details: Optional[Dict[str, float]] = Field(None, description="SLA metrics and their values")
    service_level_penalties: Optional[str] = Field(None, description="Penalties for failing to meet SLAs")
    
    # Legal and compliance
    indemnification_by_licensor: bool = Field(False, description="Whether licensor indemnifies licensee")
    indemnification_by_licensee: bool = Field(False, description="Whether licensee indemnifies licensor")
    indemnification_caps: Optional[float] = Field(None, description="Caps on indemnification amounts")
    indemnification_exclusions: Optional[List[str]] = Field(None, description="Exclusions from indemnification")
    confidentiality_term_months: Optional[int] = Field(None, description="Duration of confidentiality obligation in months")
    governing_law_jurisdiction: str = Field(..., description="Legal jurisdiction that applies to the agreement")
    dispute_resolution: DisputeResolutionMethod = Field(..., description="Method for resolving disputes")
    force_majeure_clause: bool = Field(True, description="Whether force majeure clause is included")
    export_control_compliance: bool = Field(False, description="Whether export control compliance is required")
    security_obligations: Optional[List[str]] = Field(None, description="Security standards or frameworks required")
    data_privacy_regime: DataPrivacyRegime = Field(DataPrivacyRegime.MINIMAL, description="Data privacy compliance requirements")
    data_privacy_details: Optional[str] = Field(None, description="Specific data privacy compliance details")
    
    # Assignment and termination
    assignment_provisions: AssignmentProvisionType = Field(AssignmentProvisionType.WITH_CONSENT, description="Assignment provisions for M&A scenarios")
    change_of_control: ChangeOfControlRestriction = Field(..., description="The restriction type for change of control")
    termination_provisions: TerminationProvision = Field(..., description="The provisions for terminating the agreement")
    termination_for_convenience_notice: Optional[int] = Field(None, description="Notice period for termination for convenience in days")
    material_adverse_change: MaterialAdverseChangeType = Field(MaterialAdverseChangeType.NONE, description="Material adverse change provisions")
    material_adverse_change_details: Optional[str] = Field(None, description="Details of MAC provisions if applicable")
    
    # Maintenance, support, and usage
    maintenance_included: bool = Field(False, description="Whether maintenance is included in the license")
    support_level: Optional[str] = Field(None, description="Level of technical support provided")
    support_hours: Optional[str] = Field(None, description="Hours during which support is available")
    data_usage_rights: Optional[str] = Field(None, description="How licensor may use licensee's data")
    audit_rights: bool = Field(False, description="Whether licensor has right to audit license usage")
    reverse_engineering_allowed: bool = Field(False, description="Whether reverse engineering is permitted")
    non_compete: NonCompeteType = Field(NonCompeteType.NONE, description="Non-compete restrictions")
    non_compete_duration_months: Optional[int] = Field(None, description="Duration of non-compete in months")
    non_compete_scope: Optional[str] = Field(None, description="Scope of non-compete restrictions")
    
    # Customer concentration risk
    is_key_customer: bool = Field(False, description="Whether this represents a key customer relationship")
    revenue_percentage: Optional[float] = Field(None, description="Percentage of total revenue represented by this contract")
    
    # Transition and change management
    transition_services: TransitionServiceType = Field(TransitionServiceType.NONE, description="Transition services upon ownership change")
    transition_services_duration_days: Optional[int] = Field(None, description="Duration of transition services in days")
    transition_services_costs: Optional[float] = Field(None, description="Costs associated with transition services")
    
    # Agreement mechanics
    acceptance_mechanism: AcceptanceMechanism = Field(..., description="How agreement to terms is established")
    amendment_process: str = Field("written and signed by both parties", description="Process for changing agreement terms")
