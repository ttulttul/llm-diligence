# --- START OF FILE iaas_agreement.py ---

from enum import Enum
from typing import Optional, List, Dict
from pydantic import Field
from .cloud import CloudServiceAgreement, CloudServiceType
from .legal import (
    WarrantyType,
    LiabilityLimit,
    DisputeResolutionMethod,
    AcceptanceMechanism,
    TerminationProvision, # Keep for general termination types if needed, but specific causes below are more detailed.
    ServiceLevelAgreementType,
    DataPrivacyRegime,
    AssignmentProvisionType,
    PricePeriod
)

# Define more generic Enums based on common IaaS agreement concepts

class SuspensionGroundType(str, Enum):
    """Common grounds for suspending IaaS services."""
    SECURITY_RISK = "poses a security risk to services, provider, or third parties"
    ADVERSE_SYSTEM_IMPACT = "could adversely impact provider systems or other customers' content/use"
    LIABILITY_RISK = "use could subject provider or third parties to liability"
    FRAUDULENT_USE = "suspected fraudulent activity associated with the account or usage"
    MATERIAL_BREACH = "material breach of the agreement terms (other than payment)"
    PAYMENT_BREACH = "failure to meet payment obligations"
    LEGAL_REQUIREMENT = "suspension required by law or governmental order"
    POLICY_VIOLATION = "violation of acceptable use policy or other critical policies"
    INSOLVENCY_EVENT = "customer insolvency, bankruptcy, or cessation of operations"

class TerminationCauseType(str, Enum):
    """Common grounds for terminating an IaaS agreement for cause."""
    MATERIAL_BREACH_UNCURED = "material breach remains uncured after notice period"
    SUSPENSION_ISSUE_NOT_REMEDIED = "issue leading to suspension is not remedied within a specified period"
    SUSPENSION_ISSUE_NOT_REMEDIABLE = "issue leading to suspension is incapable of remedy"
    THIRD_PARTY_DEPENDENCY_CHANGE = "critical change in relationship with underlying third-party technology/service provider"
    LEGAL_COMPLIANCE_REQUIREMENT = "termination required to comply with law or governmental requests"
    POLICY_VIOLATION_SEVERE_OR_REPEATED = "severe or repeated violation of acceptable use or other critical policies"
    INSOLVENCY_EVENT = "customer insolvency, bankruptcy, or cessation of operations"
    PROVIDER_BUSINESS_CHANGE = "significant change in provider's business making service provision unfeasible" # More generic than AWS's specific reasons

class DataProcessingScope(str, Enum):
    """How the provider may process customer data."""
    PROVIDE_MAINTAIN_SERVICE = "only as necessary to provide and maintain the services"
    COMPLY_WITH_LAW = "only as necessary to comply with law or binding legal orders"
    ANONYMIZED_AGGREGATED_ANALYTICS = "for anonymized/aggregated analytics or service improvement"
    AS_PERMITTED_BY_CUSTOMER = "as otherwise explicitly permitted by the customer"
    LIMITED_SUPPORT = "as necessary for providing technical support requested by customer"

class IaasCustomerAgreement(CloudServiceAgreement):
    """
    Represents the key concepts extracted from a generic Infrastructure as a Service (IaaS) Customer Agreement.
    Aims to be provider-agnostic (e.g., applicable to AWS, Azure, GCP, etc.).
    """
    # Parties and Agreement Setup
    customer_entity_description: str = Field(..., description="Description of the customer entity (e.g., 'you or the entity you represent').")
    customer_account_country: Optional[str] = Field(None, description="The country associated with the customer's account, often determining the specific provider entity, governing law, and taxes.")
    effective_date_description: str = Field(..., description="Describes how the agreement becomes effective (e.g., account creation, first use, explicit acceptance).")
    acceptance_mechanism: List[AcceptanceMechanism] = Field(..., description="Methods by which the customer accepts the agreement terms (e.g., Clickwrap, Use, Signature).")
    last_updated_date: Optional[str] = Field(None, description="The 'Last Updated' or version date mentioned on the agreement document.")

    # Service type is always IAAS for this agreement
    service_type: CloudServiceType = Field(CloudServiceType.IAAS, description="The type of cloud service (always IaaS for this agreement)")
    sla_type: Optional[ServiceLevelAgreementType] = Field(None, description="General type(s) of SLA guarantees offered (e.g., Availability, Performance). Specifics often vary per service.")
    service_specific_terms_apply: bool = Field(..., description="Indicates if specific terms apply to individual services offered by the provider.")
    third_party_content_allowed: Optional[bool] = Field(None, description="Specifies if third-party content/services can be used via the platform, potentially governed by separate terms.")

    # Provider Responsibilities
    provider_security_commitment_description: str = Field(..., description="Provider's stated commitment regarding security measures for the platform and potentially customer content.")
    customer_controls_data_storage_location: Optional[bool] = Field(None, description="Whether the customer can specify or control the geographic regions for data storage.")
    provider_data_access_limits_description: str = Field(..., description="Limitations on the provider accessing or using customer data/content.")
    provider_data_processing_scope: List[DataProcessingScope] = Field(..., description="Purposes for which the provider may access or process customer data.")
    provider_data_disclosure_limits_description: str = Field(..., description="Limitations on the provider disclosing customer data to third parties or government entities.")
    data_privacy_regime: DataPrivacyRegime = Field(DataPrivacyRegime.MINIMAL, description="Applicable data privacy compliance requirements (e.g., GDPR, CCPA) explicitly mentioned or implied.")
    provider_privacy_policy_url: Optional[str] = Field(None, description="URL for the provider's main privacy policy document.")
    material_service_change_notice_period_days: Optional[int] = Field(None, description="Notice period in days before discontinuing or making materially adverse changes to a generally available service.")
    adverse_sla_change_notice_period_days: Optional[int] = Field(None, description="Advance notice period in days for materially adverse changes to SLAs.")

    # Customer Responsibilities
    customer_compliance_obligation: str = Field("Comply with Agreement terms, applicable laws, regulations, and provider policies (e.g., Acceptable Use Policy).", description="Customer's general obligation to comply.")
    account_security_responsibility: str = Field("Responsible for all activities under the account, securing credentials, and configuring security options.", description="Customer's responsibility for account activities and security.")
    customer_content_responsibility: str = Field("Responsible for legality, security, and rights to customer data/content and its use.", description="Customer's responsibility for their hosted content.")
    customer_security_backup_responsibility: str = Field("Responsible for properly configuring services, securing, protecting and backing up accounts and content.", description="Customer's responsibility for configuration, security, and data backup.")
    credential_use_restrictions: str = Field("Restrictions on sharing or transferring account credentials and API keys.", description="Rules governing the use and confidentiality of access credentials.")
    end_user_responsibility: str = Field("Responsible for actions of end users accessing services via the customer's account and ensuring their compliance.", description="Customer's liability for their own users.")
    acceptable_use_policy_url: Optional[str] = Field(None, description="URL for the provider's Acceptable Use Policy (AUP).")

    # Payment Terms
    billing_frequency: PricePeriod = Field(PricePeriod.MONTHLY, description="Typical frequency for billing (e.g., Monthly, Usage-Based).") # Note: Usage-based might need to be added to PricePeriod Enum
    payment_method_description: str = Field(..., description="Requirements for providing and maintaining valid payment methods.")
    late_payment_interest_rate_percent_monthly: Optional[float] = Field(None, description="Monthly interest rate charged on overdue payments, if specified.")
    fee_change_notice_period_days: Optional[int] = Field(None, description="Advance notice period in days for changes to service fees.")
    tax_responsibility: str = Field("Typically customer pays applicable indirect taxes (VAT, GST, Sales Tax); provider may collect.", description="Allocation of responsibility for paying taxes.")
    payment_terms_details: Optional[str] = Field("Additional payment details like currency, due dates, no setoff clauses.", description="Other relevant payment clauses.")

    # Suspension
    suspension_grounds: List[SuspensionGroundType] = Field(..., description="Conditions under which the provider may suspend service access.")
    effect_of_suspension: str = Field("Consequences of service suspension (e.g., continued fees, no SLA credits).", description="Impact of suspension on customer obligations and rights.")

    # Term and Termination
    term_description: str = Field("Typically starts on acceptance/use and continues until terminated.", description="Duration of the agreement.")
    termination_for_convenience_customer: bool = Field(..., description="Whether the customer can terminate the agreement without cause.")
    termination_for_convenience_provider: bool = Field(..., description="Whether the provider can terminate the agreement without cause.")
    termination_for_convenience_provider_notice_days: Optional[int] = Field(None, description="Required notice period in days if provider terminates for convenience.")
    termination_for_cause_provisions: List[TerminationCauseType] = Field(..., description="Specific reasons allowing termination for cause by either party.")
    termination_cure_period_days: Optional[int] = Field(None, description="Cure period in days provided to remedy a material breach before termination, if applicable.")
    post_termination_content_retrieval_days: Optional[int] = Field(None, description="Period after termination during which customer may retrieve their data, often conditional on payment.")
    effect_of_termination_description: str = Field("General consequences of termination (e.g., rights cease, fees due, data deletion, survival of clauses).", description="Outcome upon agreement termination.")

    # Proprietary Rights & Restrictions
    customer_content_ownership: str = Field("Customer generally retains ownership of their data/content uploaded to the service.", description="Statement on ownership of customer data.")
    provider_content_ownership_description: str = Field("Provider or licensors own the services, APIs, documentation, and other provided materials.", description="Statement on ownership of provider's platform and related content.")
    provider_content_license_url: Optional[str] = Field(None, description="URL for specific license terms governing use of provider's APIs, SDKs, etc.")
    reverse_engineering_prohibited: bool = Field(True, description="Whether reverse engineering, decompiling, or disassembling the provider's services or software is prohibited.")
    reselling_prohibited: Optional[bool] = Field(None, description="Whether reselling the provider's services is prohibited without specific agreement.")
    feedback_ownership: str = Field("Typically states that provider owns any suggestions or feedback provided by the customer.", description="Ownership of suggestions, ideas, or feedback provided by the customer.")

    # Indemnification
    indemnification_by_customer: bool = Field(..., description="Whether the customer must indemnify the provider.")
    indemnification_by_customer_scope: List[str] = Field(..., description="Scope of customer's indemnification obligations (e.g., use of service, content infringement, breach of agreement, end user actions).")
    indemnification_by_provider: bool = Field(..., description="Whether the provider indemnifies the customer.")
    indemnification_by_provider_scope: List[str] = Field(..., description="Scope of provider's indemnification obligations (typically limited to third-party IP infringement claims regarding the core service).")
    indemnification_exclusions: List[str] = Field(..., description="Common exclusions from indemnification obligations (e.g., combinations with other products, customer modifications, use after notice).")
    indemnification_process_requirements: str = Field("Procedural requirements for triggering indemnification (e.g., prompt notice, control of defense, cooperation).", description="Steps required to claim indemnification.")

    # Disclaimers and Liability Limitations
    warranty_type: WarrantyType = Field(WarrantyType.NONE, description="Warranty level provided for the services (commonly 'AS IS' / None).")
    disclaimer_details: str = Field("Specifies disclaimed warranties (e.g., merchantability, fitness for purpose, non-infringement, uninterrupted/error-free service).", description="Details of warranties expressly disclaimed by the provider.")
    liability_exclusions: List[str] = Field(["Indirect, consequential, special, incidental damages", "Lost profits, revenue, data, or goodwill", "Cost of substitute services"], description="Types of damages typically excluded from liability for both parties.")
    liability_limit: LiabilityLimit = Field(LiabilityLimit.FEES_PAID, description="Nature of the cap on direct liability (e.g., limited to fees paid, fixed amount).")
    liability_cap_period_months: Optional[int] = Field(12, description="Look-back period in months for calculating a fee-based liability cap, if applicable.")
    liability_limit_exceptions: List[str] = Field(["Indemnification obligations", "Breach of confidentiality", "Customer payment obligations", "Willful misconduct"], description="Common exceptions to the liability cap.")

    # Modifications and Miscellaneous
    modification_process: str = Field("How the agreement can be modified (e.g., provider posts changes online, requires notice).", description="Process for amending the agreement terms.")
    assignment_provisions_customer: AssignmentProvisionType = Field(AssignmentProvisionType.WITH_CONSENT, description="Customer's ability to assign the agreement (typically requires provider consent).")
    assignment_provisions_provider_description: str = Field("Provider's ability to assign the agreement (often permitted for M&A, affiliates).", description="Provider's rights regarding assignment.")
    force_majeure_clause: bool = Field(True, description="Whether a force majeure clause is included, excusing performance for unforeseen events.")
    governing_law_jurisdiction: str = Field(..., description="The law and courts that govern the agreement, often dependent on provider/customer location.")
    dispute_resolution: DisputeResolutionMethod = Field(DisputeResolutionMethod.ARBITRATION, description="Primary method specified for resolving disputes (e.g., Arbitration, Litigation).")
    dispute_resolution_details: Optional[str] = Field("Specifics of the dispute resolution process (e.g., arbitration rules, location, exceptions for IP/injunctive relief).", description="Further details on dispute handling.")
    confidentiality_obligation_duration_years_post_term: Optional[int] = Field(None, description="Duration (in years) the confidentiality obligation lasts after the agreement terminates, if specified.")
    confidentiality_obligations_customer: str = Field("Customer's obligations regarding provider's confidential information.", description="Rules for handling provider's non-public info.")
    notice_methods_to_customer: List[str] = Field(["Email to account address", "Posting on provider portal/website"], description="Methods the provider uses to give notice to the customer.")
    notice_methods_to_provider: List[str] = Field(["Specific provider contact address/method", "Support portal ticket"], description="Methods the customer must use to give formal notice to the provider.")
    trade_compliance_required: bool = Field(True, description="Whether compliance with export control and sanctions laws is required.")
    relationship_of_parties: str = Field("Independent contractors", description="Specifies the legal relationship between the provider and customer.")
    language: str = Field("English", description="Controlling language of the agreement, especially if translations are provided.")
    no_third_party_beneficiaries: bool = Field(True, description="States that the agreement does not create rights for entities not party to it (except potentially for indemnified parties).")
    us_government_rights: Optional[str] = Field(None, description="Specific terms applicable if the customer is a U.S. Government entity (e.g., 'commercial item' clauses).")
    country_specific_terms_exist: Optional[bool] = Field(None, description="Indicates if specific addenda or modifications apply based on customer location.")

# --- END OF FILE iaas_agreement.py ---
