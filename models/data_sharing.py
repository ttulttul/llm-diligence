from enum import Enum
from typing import Optional, List, Dict
from pydantic import Field
from datetime import date
from .contracts import CommercialAgreement

class GDPRAgreementType(str, Enum):
    """Types of GDPR-specific data sharing agreements"""
    DPA = "data processing addendum"
    JOINT_CONTROLLER = "joint controller agreement"
    SCCs = "standard contractual clauses"
    BCRs = "binding corporate rules"
    CONSENT_FRAMEWORK = "consent framework agreement"
    DPIA = "data protection impact assessment"

class DataCategory(str, Enum):
    """Categories of data that may be shared"""
    PERSONAL = "personal data"
    SENSITIVE_PERSONAL = "sensitive personal data"
    ANONYMIZED = "anonymized data"
    PSEUDONYMIZED = "pseudonymized data"
    AGGREGATED = "aggregated data"
    BUSINESS = "business data"
    FINANCIAL = "financial data"
    TECHNICAL = "technical data"
    OPERATIONAL = "operational data"
    INTELLECTUAL_PROPERTY = "intellectual property"
    PUBLIC = "public data"
    CONFIDENTIAL = "confidential data"
    PROPRIETARY = "proprietary data"

class DataProcessingPurpose(str, Enum):
    """Common purposes for data processing"""
    ANALYTICS = "analytics and insights"
    RESEARCH = "research and development"
    SERVICE_PROVISION = "service provision"
    MARKETING = "marketing and advertising"
    COMPLIANCE = "regulatory compliance"
    SECURITY = "security and fraud prevention"
    PRODUCT_IMPROVEMENT = "product improvement"
    BUSINESS_OPERATIONS = "business operations"
    CUSTOMER_SUPPORT = "customer support"
    PERSONALIZATION = "personalization"
    THIRD_PARTY_SHARING = "third-party sharing"
    PROFILING = "profiling and automated decision-making"

class DataTransferMechanism(str, Enum):
    """Mechanisms for transferring data"""
    API = "application programming interface"
    SFTP = "secure file transfer protocol"
    ENCRYPTED_EMAIL = "encrypted email"
    SECURE_PORTAL = "secure portal"
    DIRECT_DATABASE_ACCESS = "direct database access"
    PHYSICAL_MEDIA = "physical media"
    CLOUD_STORAGE = "cloud storage service"
    VPN = "virtual private network"
    BATCH_TRANSFER = "batch transfer"
    REAL_TIME_STREAMING = "real-time streaming"

class DataProtectionMeasure(str, Enum):
    """Security and protection measures for data"""
    ENCRYPTION_AT_REST = "encryption at rest"
    ENCRYPTION_IN_TRANSIT = "encryption in transit"
    ACCESS_CONTROLS = "access controls"
    AUDIT_LOGGING = "audit logging"
    DATA_MINIMIZATION = "data minimization"
    ANONYMIZATION = "anonymization techniques"
    PSEUDONYMIZATION = "pseudonymization techniques"
    REGULAR_AUDITS = "regular security audits"
    EMPLOYEE_TRAINING = "employee training"
    INCIDENT_RESPONSE = "incident response plan"
    DATA_RETENTION_LIMITS = "data retention limitations"
    SECURE_DELETION = "secure deletion procedures"

class DataSharingFrequency(str, Enum):
    """Frequency of data sharing"""
    ONE_TIME = "one-time transfer"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    ON_DEMAND = "on-demand"
    REAL_TIME = "real-time"
    CONTINUOUS = "continuous"
    SCHEDULED = "according to schedule"

class DataRetentionPeriod(str, Enum):
    """Common data retention periods"""
    TRANSACTION_DURATION = "duration of transaction only"
    CONTRACT_TERM = "term of the contract"
    SPECIFIED_PERIOD = "specified time period"
    REGULATORY_REQUIREMENT = "as required by regulations"
    INDEFINITE = "indefinite retention"
    UNTIL_REQUEST = "until deletion is requested"
    PURPOSE_COMPLETION = "until purpose is completed"
    HYBRID = "varies by data category"

class DataProtectionAddendum(CommercialAgreement):
    """A GDPR-focused agreement that establishes the terms and conditions for processing personal data.
    
    This model captures the specific requirements under GDPR for data processing relationships,
    including controller-processor obligations, data subject rights management, breach notification
    requirements, and cross-border transfer mechanisms. It enables systematic analysis of GDPR
    compliance in data processing arrangements between organizations."""
    
    # Parties and roles
    controller_name: str = Field(..., description="Entity acting as the data controller")
    processor_name: str = Field(..., description="Entity acting as the data processor")
    sub_processors_allowed: bool = Field(False, description="Whether sub-processors are permitted")
    sub_processor_approval_required: Optional[bool] = Field(None, description="Whether controller approval is required for sub-processors")
    
    # GDPR specifics
    gdpr_agreement_type: GDPRAgreementType = Field(GDPRAgreementType.DPA, description="Type of GDPR agreement")
    article_28_compliant: bool = Field(True, description="Whether the agreement is compliant with GDPR Article 28")
    sccs_incorporated: bool = Field(False, description="Whether Standard Contractual Clauses are incorporated")
    sccs_version: Optional[str] = Field(None, description="Version of SCCs used if applicable")
    
    # Data subject rights
    data_subject_request_handling: str = Field(..., description="Process for handling data subject requests")
    data_subject_request_timeframe_days: Optional[int] = Field(None, description="Timeframe for responding to data subject requests in days")
    right_to_erasure_process: Optional[str] = Field(None, description="Process for handling right to erasure requests")
    right_to_access_process: Optional[str] = Field(None, description="Process for handling right to access requests")
    
    # Breach notification
    breach_notification_hours: int = Field(72, description="Time frame for breach notification in hours")
    breach_notification_process: str = Field(..., description="Process for notifying of data breaches")
    
    # Technical and organizational measures
    technical_measures: List[str] = Field(..., description="Technical measures for data protection")
    organizational_measures: List[str] = Field(..., description="Organizational measures for data protection")
    
    # Audit and compliance
    audit_rights: bool = Field(True, description="Whether the controller has audit rights")
    audit_frequency: Optional[str] = Field(None, description="How often audits may be conducted")
    audit_notice_period_days: Optional[int] = Field(None, description="Notice period required for audits in days")
    
    # Cross-border transfers
    transfers_outside_eea_allowed: bool = Field(False, description="Whether transfers outside the EEA are allowed")
    transfer_safeguards: Optional[List[str]] = Field(None, description="Safeguards for international transfers")
    
    # Term and termination
    return_or_deletion_upon_termination: str = Field(..., description="Requirements for data return or deletion upon termination")
    certification_of_deletion_required: bool = Field(True, description="Whether certification of deletion is required")
    
    # Liability
    liability_cap_specified: Optional[bool] = Field(None, description="Whether a liability cap is specified")
    liability_cap_amount: Optional[float] = Field(None, description="Amount of liability cap if specified")
    processor_indemnification_required: Optional[bool] = Field(None, description="Whether processor indemnification is required")

class DataSharingAgreement(CommercialAgreement):
    """A contractual arrangement governing the sharing of data between organizations, establishing the terms, 
    conditions, and safeguards for data exchange.
    
    This model captures the comprehensive framework for data sharing partnerships, including data types, 
    processing purposes, transfer mechanisms, security measures, and compliance requirements. It enables 
    systematic analysis of data sharing arrangements to ensure proper governance, risk management, and 
    regulatory compliance across organizational boundaries."""
    
    # GDPR-specific fields
    is_gdpr_relevant: Optional[bool] = Field(None, description="Whether the agreement is subject to GDPR")
    gdpr_agreement_type: Optional[GDPRAgreementType] = Field(None, description="Type of GDPR agreement if applicable")
    has_data_protection_addendum: Optional[bool] = Field(None, description="Whether a separate DPA is attached or referenced")
    dpa_date: Optional[date] = Field(None, description="Date of the associated Data Protection Addendum")
    controller_processor_relationship: Optional[str] = Field(None, description="Nature of controller-processor relationship if applicable")
    
    # Parties and roles
    data_provider: str = Field(..., description="Entity providing the data")
    data_recipient: str = Field(..., description="Entity receiving the data")
    third_party_recipients: Optional[List[str]] = Field(None, description="Additional third parties who may receive the data")
    
    # Data details
    data_categories: List[DataCategory] = Field(..., description="Categories of data being shared")
    data_description: str = Field(..., description="Detailed description of the data being shared")
    data_sources: Optional[List[str]] = Field(None, description="Sources of the data being shared")
    data_subjects: Optional[List[str]] = Field(None, description="Types of individuals or entities the data relates to")
    data_volume_estimate: Optional[str] = Field(None, description="Estimated volume of data (e.g., records, size)")
    sample_data_provided: Optional[bool] = Field(None, description="Whether sample data is provided as part of the agreement")
    
    # Purpose and usage
    processing_purposes: List[DataProcessingPurpose] = Field(..., description="Purposes for which the data may be processed")
    purpose_limitations: Optional[List[str]] = Field(None, description="Specific limitations on data usage")
    prohibited_uses: Optional[List[str]] = Field(None, description="Explicitly prohibited uses of the data")
    
    # Transfer and logistics
    transfer_mechanism: DataTransferMechanism = Field(..., description="Method used to transfer the data")
    transfer_details: Optional[str] = Field(None, description="Technical details of the transfer process")
    sharing_frequency: DataSharingFrequency = Field(..., description="How often data is shared")
    sharing_schedule: Optional[str] = Field(None, description="Specific schedule for data sharing if applicable")
    
    # Duration and termination
    start_date: date = Field(..., description="Date when data sharing begins")
    end_date: Optional[date] = Field(None, description="Date when data sharing ends, if fixed")
    renewal_terms: Optional[str] = Field(None, description="Terms for renewing the agreement")
    termination_notice_period_days: Optional[int] = Field(None, description="Notice period required for termination in days")
    
    # Data protection and security
    protection_measures: List[DataProtectionMeasure] = Field(..., description="Security measures required for the data")
    breach_notification_hours: Optional[int] = Field(None, description="Time frame for breach notification in hours")
    breach_notification_process: Optional[str] = Field(None, description="Process for notifying of data breaches")
    
    # Compliance
    applicable_data_laws: List[str] = Field(..., description="Data protection laws applicable to the agreement")
    compliance_requirements: Optional[List[str]] = Field(None, description="Specific compliance requirements")
    cross_border_transfers: Optional[bool] = Field(None, description="Whether data crosses international borders")
    transfer_safeguards: Optional[List[str]] = Field(None, description="Safeguards for international transfers")
    
    # Rights and responsibilities
    data_ownership: str = Field(..., description="Statement of who owns the data")
    intellectual_property_rights: Optional[str] = Field(None, description="IP rights related to the data")
    derived_data_ownership: Optional[str] = Field(None, description="Ownership of data derived from the shared data")
    
    # Retention and deletion
    retention_period: DataRetentionPeriod = Field(..., description="How long data may be retained")
    retention_period_details: Optional[str] = Field(None, description="Specific details about retention period")
    deletion_requirements: Optional[str] = Field(None, description="Requirements for data deletion")
    deletion_certification: Optional[bool] = Field(None, description="Whether certification of deletion is required")
    
    # Audit and oversight
    audit_rights: Optional[bool] = Field(None, description="Whether the data provider has audit rights")
    audit_frequency: Optional[str] = Field(None, description="How often audits may be conducted")
    audit_notice_period_days: Optional[int] = Field(None, description="Notice period required for audits in days")
    
    # Liability and indemnification
    liability_limitations: Optional[str] = Field(None, description="Limitations on liability")
    indemnification_provisions: Optional[str] = Field(None, description="Indemnification requirements")
    insurance_requirements: Optional[str] = Field(None, description="Insurance requirements for data handling")
    
    # Fees and compensation
    fee_structure: Optional[str] = Field(None, description="Fee structure for data sharing if applicable")
    payment_terms: Optional[str] = Field(None, description="Payment terms if fees are involved")
    
    # Miscellaneous
    confidentiality_provisions: Optional[str] = Field(None, description="Provisions regarding confidentiality")
    dispute_resolution_mechanism: Optional[str] = Field(None, description="Mechanism for resolving disputes")
    governing_law: str = Field(..., description="Jurisdiction's laws governing the agreement")
    force_majeure_clause: Optional[bool] = Field(None, description="Whether force majeure clause is included")
    
    # Amendments and modifications
    amendment_process: Optional[str] = Field(None, description="Process for amending the agreement")
    
    # Risk assessment
    risk_assessment_conducted: Optional[bool] = Field(None, description="Whether a data protection impact assessment was conducted")
    identified_risks: Optional[List[str]] = Field(None, description="Key risks identified in assessment")
    risk_mitigation_measures: Optional[List[str]] = Field(None, description="Measures to mitigate identified risks")
