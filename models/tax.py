from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import Field, BaseModel
from datetime import date, datetime
from .base import DiligentizerModel

class TaxJurisdiction(str, Enum):
    """Types of tax jurisdictions"""
    FEDERAL = "federal"
    STATE = "state"
    PROVINCIAL = "provincial"
    LOCAL = "local"
    INTERNATIONAL = "international"

class TaxType(str, Enum):
    """Common types of taxes"""
    INCOME = "income tax"
    SALES = "sales tax"
    VAT = "value-added tax"
    GST = "goods and services tax"
    PAYROLL = "payroll tax"
    PROPERTY = "property tax"
    EXCISE = "excise tax"
    CUSTOM_DUTY = "customs duty"
    WITHHOLDING = "withholding tax"
    CAPITAL_GAINS = "capital gains tax"
    TRANSFER = "transfer tax"
    FRANCHISE = "franchise tax"

class TaxFilingStatus(str, Enum):
    """Status of tax filings"""
    FILED_ON_TIME = "filed on time"
    FILED_EXTENSION = "filed with extension"
    FILED_LATE = "filed late"
    NOT_FILED = "not filed"
    EXEMPT = "exempt from filing"
    UNDER_AUDIT = "under audit"
    CONTESTED = "contested"

class TaxDisputeStatus(str, Enum):
    """Status of tax disputes"""
    NO_DISPUTE = "no dispute"
    UNDER_REVIEW = "under internal review"
    INFORMAL_NEGOTIATION = "informal negotiation with authority"
    FORMAL_APPEAL = "formal administrative appeal"
    LITIGATION = "litigation"
    SETTLEMENT_NEGOTIATION = "settlement negotiation"
    RESOLVED = "resolved"

class TaxIncentiveType(str, Enum):
    """Types of tax incentives"""
    R_AND_D_CREDIT = "research and development credit"
    INVESTMENT_CREDIT = "investment tax credit"
    JOBS_CREDIT = "jobs/employment credit"
    ENTERPRISE_ZONE = "enterprise/opportunity zone incentive"
    ENERGY_CREDIT = "energy/sustainability credit"
    FOREIGN_TAX_CREDIT = "foreign tax credit"
    EMPOWERMENT_ZONE = "empowerment zone incentive"
    ACCELERATED_DEPRECIATION = "accelerated depreciation"
    EXPORT_INCENTIVE = "export incentive"
    OTHER = "other tax incentive"

class TaxDocument(DiligentizerModel):
    """A document related to taxation, such as documents from Canada Revenue Agency or the IRS.
    
    This model serves as the foundation for all tax-related document types, capturing essential
    metadata such as tax year, jurisdiction, document date, and document type. It provides a
    structured representation of tax documents from various authorities, enabling systematic
    analysis and organization of tax-related information across different jurisdictions and
    time periods."""
    tax_year: Optional[str] = Field(None, description="The tax year(s) the document pertains to")
    company_name: Optional[str] = Field(None, description="Name of the company or entity")
    tax_id_number: Optional[str] = Field(None, description="Tax identification number (e.g., EIN, TIN)")
    jurisdiction: Optional[TaxJurisdiction] = Field(None, description="The tax jurisdiction (federal, state, etc.)")
    jurisdiction_name: Optional[str] = Field(None, description="Name of specific jurisdiction (e.g., 'California', 'Canada')")
    document_date: Optional[date] = Field(None, description="Date the document was created or filed")
    prepared_by: Optional[str] = Field(None, description="Name of person or firm who prepared the document")
    document_id: Optional[str] = Field(None, description="Unique identifier for the document")
    document_type: Optional[str] = Field(None, description="Type of tax document")
    filing_requirement: Optional[str] = Field(None, description="Legal or regulatory requirement for this document")
    confidentiality_level: Optional[str] = Field(None, description="Level of confidentiality (e.g., Public, Confidential, Highly Confidential)")
    retention_period: Optional[str] = Field(None, description="Required retention period for the document")
    related_documents: Optional[List[str]] = Field(None, description="References to related tax documents")

class ComplianceDocument(TaxDocument):
    """A document related to tax compliance requirements and filings"""
    due_date: Optional[date] = Field(None, description="Original due date for the document")
    extended_due_date: Optional[date] = Field(None, description="Extended due date if an extension was filed")
    filing_date: Optional[date] = Field(None, description="Date the document was filed")
    filing_method: Optional[str] = Field(None, description="Method used for filing (e.g., electronic, paper)")
    filing_status: Optional[str] = Field(None, description="Status of the filing")
    signature_required: Optional[bool] = Field(None, description="Whether a signature is required")
    signatory: Optional[str] = Field(None, description="Person who signed or will sign the document")
    penalties_for_late_filing: Optional[float] = Field(None, description="Penalties for late filing")
    extension_filed: Optional[bool] = Field(None, description="Whether an extension was filed")
    extension_details: Optional[str] = Field(None, description="Details about any extension")

class AnalyticalDocument(TaxDocument):
    """A document containing tax analysis, assessments, or evaluations"""
    analysis_date: Optional[date] = Field(None, description="Date the analysis was performed")
    analysis_period: Optional[str] = Field(None, description="Period covered by the analysis")
    analysis_purpose: Optional[str] = Field(None, description="Purpose of the analysis")
    methodology: Optional[str] = Field(None, description="Methodology used in the analysis")
    key_assumptions: Optional[List[str]] = Field(None, description="Key assumptions made in the analysis")
    conclusions: Optional[List[str]] = Field(None, description="Conclusions reached in the analysis")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations based on the analysis")
    data_sources: Optional[List[str]] = Field(None, description="Sources of data used in the analysis")
    limitations: Optional[List[str]] = Field(None, description="Limitations of the analysis")

class TaxAuthorityDocument(TaxDocument):
    """A document such as a letter, notice, audit result, etc. issued by a tax authority such as Canada Revenue Agency or the IRS"""
    issuing_authority: Optional[str] = Field(None, description="Authority that issued the document")
    authority_reference_number: Optional[str] = Field(None, description="Reference number assigned by the authority")
    issuance_date: Optional[date] = Field(None, description="Date the document was issued")
    response_required: Optional[bool] = Field(None, description="Whether a response is required")
    response_deadline: Optional[date] = Field(None, description="Deadline for any required response")
    authority_contact: Optional[str] = Field(None, description="Contact person at the authority")
    authority_department: Optional[str] = Field(None, description="Department within the authority")
    delivery_method: Optional[str] = Field(None, description="How the document was delivered")
    receipt_date: Optional[date] = Field(None, description="Date the document was received")

class ProfessionalTaxAdvisoryDocument(TaxDocument):
    """A document written by a tax professional providing tax advice, guidance,
    or recommendations from a professional (not a tax authority) For avoidance
    of doubt: this model is NOT appropriate for a document produced by a tax
    authority such as Canada Revenue Agency or the IRS. It is for documents
    from tax professionals like accountants, KPMG, etc."""
    advisor: Optional[str] = Field(None, description="Advisor who provided the advice")
    advisor_firm: Optional[str] = Field(None, description="Firm of the advisor")
    advice_date: Optional[date] = Field(None, description="Date the advice was provided")
    advice_scope: Optional[str] = Field(None, description="Scope of the advice")
    advice_limitations: Optional[List[str]] = Field(None, description="Limitations of the advice")
    reliance_permitted: Optional[bool] = Field(None, description="Whether reliance on the advice is permitted")
    reliance_limitations: Optional[List[str]] = Field(None, description="Limitations on reliance")
    fee_arrangement: Optional[str] = Field(None, description="Fee arrangement for the advice")
    conflicts_of_interest: Optional[List[str]] = Field(None, description="Any disclosed conflicts of interest")
    privilege_status: Optional[str] = Field(None, description="Privilege status of the document")

class TaxReturn(ComplianceDocument):
    """Represents a tax return filing"""
    return_type: Optional[str] = Field(None, description="Type of tax return (e.g., Form 1120, Form 1065)")
    tax_types: List[TaxType] = Field(default_factory=list, description="Types of taxes covered in the return")
    filing_status: TaxFilingStatus = Field(TaxFilingStatus.FILED_ON_TIME, description="Status of the tax filing")
    filing_date: Optional[date] = Field(None, description="Date the return was filed")
    due_date: Optional[date] = Field(None, description="Original due date for the return")
    extended_due_date: Optional[date] = Field(None, description="Extended due date if an extension was filed")
    taxable_income: Optional[float] = Field(None, description="Reported taxable income amount")
    tax_liability: Optional[float] = Field(None, description="Total tax liability reported")
    tax_paid: Optional[float] = Field(None, description="Total tax already paid or credited")
    balance_due_or_refund: Optional[float] = Field(None, description="Final balance due or refund amount")
    signature_present: Optional[bool] = Field(None, description="Whether the return contains required signatures")
    electronic_filing: Optional[bool] = Field(None, description="Whether the return was filed electronically")
    amended: Optional[bool] = Field(False, description="Whether this is an amended return")
    consolidated_return: Optional[bool] = Field(False, description="Whether this is a consolidated return filing")
    included_entities: Optional[List[str]] = Field(None, description="Entities included in a consolidated return")
    
    # Common tax schedules and forms
    key_schedules_present: Optional[List[str]] = Field(None, description="Key schedules or forms included (e.g., 'Schedule M-3', 'Form 5471')")
    
    # Auditor's notes
    material_positions: Optional[List[str]] = Field(None, description="Material tax positions or elections taken")
    notes: Optional[str] = Field(None, description="Additional notes or observations about the return")

class CorporateTaxReturn(TaxReturn):
    """Corporate income tax return"""
    corporate_structure: Optional[str] = Field(None, description="Corporate structure (e.g., C-Corp, S-Corp)")
    revenue: Optional[float] = Field(None, description="Total revenue reported")
    cogs: Optional[float] = Field(None, description="Cost of goods sold")
    gross_profit: Optional[float] = Field(None, description="Gross profit")
    total_deductions: Optional[float] = Field(None, description="Total deductions claimed")
    net_operating_loss: Optional[float] = Field(None, description="Net operating loss reported or utilized")
    foreign_tax_credits: Optional[float] = Field(None, description="Foreign tax credits claimed")
    other_credits: Optional[Dict[str, float]] = Field(None, description="Other tax credits claimed")
    total_assets: Optional[float] = Field(None, description="Total assets reported")
    total_liabilities: Optional[float] = Field(None, description="Total liabilities reported")
    shareholder_equity: Optional[float] = Field(None, description="Shareholder equity")
    dividend_distributions: Optional[float] = Field(None, description="Dividend distributions made")
    officer_compensation: Optional[Dict[str, float]] = Field(None, description="Compensation to officers")
    depreciation_method: Optional[str] = Field(None, description="Depreciation method used")
    depreciation_amount: Optional[float] = Field(None, description="Depreciation amount claimed")
    amortization_amount: Optional[float] = Field(None, description="Amortization amount claimed")
    
    # International tax information
    has_foreign_operations: Optional[bool] = Field(None, description="Indicates if company has foreign operations")
    foreign_subsidiaries: Optional[List[str]] = Field(None, description="Foreign subsidiaries reported")
    transfer_pricing_documentation: Optional[bool] = Field(None, description="Whether transfer pricing documentation was referenced")
    
    # Key tax reconciliation items
    book_to_tax_differences: Optional[Dict[str, float]] = Field(None, description="Major book-to-tax differences")
    effective_tax_rate: Optional[float] = Field(None, description="Effective tax rate")
    statutory_to_effective_rate_reconciliation: Optional[Dict[str, float]] = Field(None, description="Reconciliation of statutory to effective rate")

class PassthroughTaxReturn(TaxReturn):
    """Tax return for pass-through entities (partnerships, LLCs, S-Corps)"""
    entity_type: Optional[str] = Field(None, description="Type of pass-through entity (e.g., Partnership, LLC, S-Corp)")
    number_of_partners: Optional[int] = Field(None, description="Number of partners or members")
    ordinary_income: Optional[float] = Field(None, description="Ordinary business income or loss")
    rental_income: Optional[float] = Field(None, description="Rental income or loss")
    interest_income: Optional[float] = Field(None, description="Interest income")
    dividend_income: Optional[float] = Field(None, description="Dividend income")
    capital_gains: Optional[float] = Field(None, description="Net capital gains or losses")
    partner_distributions: Optional[float] = Field(None, description="Total distributions to partners/members")
    guaranteed_payments: Optional[float] = Field(None, description="Guaranteed payments to partners")
    
    # Section 704(b) allocations
    special_allocations: Optional[bool] = Field(None, description="Whether special allocations were used")
    allocation_method: Optional[str] = Field(None, description="Method used for allocations")
    
    # Foreign reporting
    foreign_partners: Optional[bool] = Field(None, description="Whether entity has foreign partners")
    foreign_income: Optional[float] = Field(None, description="Foreign-source income reported")
    
    # Ownership information
    ownership_changes: Optional[bool] = Field(None, description="Whether ownership changes occurred during tax year")
    major_owners: Optional[List[Dict[str, Any]]] = Field(None, description="Information about major owners (>5%)")

class TaxAssessment(TaxAuthorityDocument):
    """Tax assessment or notice from a tax authority"""
    assessment_id: Optional[str] = Field(None, description="Identification number of the assessment")
    tax_type: TaxType = Field(..., description="Type of tax being assessed")
    assessment_amount: Optional[float] = Field(None, description="Amount of tax assessed")
    penalties_amount: Optional[float] = Field(None, description="Amount of penalties assessed")
    interest_amount: Optional[float] = Field(None, description="Amount of interest assessed")
    total_amount_due: Optional[float] = Field(None, description="Total amount due")
    issue_date: Optional[date] = Field(None, description="Date the assessment was issued")
    response_due_date: Optional[date] = Field(None, description="Date by which a response is required")
    payment_due_date: Optional[date] = Field(None, description="Date by which payment is due")
    reason_for_assessment: Optional[str] = Field(None, description="Reason provided for the assessment")
    periods_covered: Optional[List[str]] = Field(None, description="Tax periods covered by the assessment")
    current_status: Optional[str] = Field(None, description="Current status of the assessment")
    response_filed: Optional[bool] = Field(None, description="Whether a response has been filed")
    payment_made: Optional[bool] = Field(None, description="Whether payment has been made")
    dispute_in_progress: Optional[bool] = Field(None, description="Whether the assessment is being disputed")

class TaxDispute(TaxDocument):
    """Document related to a tax dispute or controversy"""
    dispute_id: Optional[str] = Field(None, description="Identification number of the dispute")
    tax_types: List[TaxType] = Field(default_factory=list, description="Types of taxes involved in the dispute")
    disputed_amount: Optional[float] = Field(None, description="Amount of tax in dispute")
    periods_covered: Optional[List[str]] = Field(None, description="Tax periods covered by the dispute")
    dispute_status: TaxDisputeStatus = Field(TaxDisputeStatus.NO_DISPUTE, description="Current status of the dispute")
    dispute_start_date: Optional[date] = Field(None, description="Date the dispute began")
    dispute_forum: Optional[str] = Field(None, description="Forum where the dispute is being adjudicated")
    issues_in_dispute: Optional[List[str]] = Field(None, description="Tax issues being disputed")
    company_position: Optional[str] = Field(None, description="Company's position on the disputed issues")
    authority_position: Optional[str] = Field(None, description="Tax authority's position on the disputed issues")
    potential_exposure: Optional[float] = Field(None, description="Estimated potential financial exposure")
    reserve_amount: Optional[float] = Field(None, description="Tax reserve amount related to the dispute")
    external_counsel: Optional[str] = Field(None, description="External counsel representing the company")
    settlement_offers: Optional[List[Dict[str, Any]]] = Field(None, description="Details of any settlement offers")
    expected_resolution_date: Optional[date] = Field(None, description="Expected resolution date")
    probability_of_favorable_outcome: Optional[float] = Field(None, description="Estimated probability of favorable outcome (0-1)")

class ProfessionalTaxOpinion(ProfessionalTaxAdvisoryDocument):
    """A tax opinion or advice document from a tax professional (not a tax authority)"""
    opinion_provider: Optional[str] = Field(None, description="Firm or professional providing the opinion")
    opinion_type: Optional[str] = Field(None, description="Type of tax opinion (e.g., 'Will Opinion', 'Should Opinion', 'More Likely Than Not')")
    confidence_level: Optional[float] = Field(None, description="Numerical confidence level (0-1) if provided")
    addressed_to: Optional[str] = Field(None, description="Entity to whom the opinion is addressed")
    tax_issues_addressed: Optional[List[str]] = Field(None, description="Tax issues addressed in the opinion")
    transactions_covered: Optional[List[str]] = Field(None, description="Transactions covered by the opinion")
    key_conclusions: Optional[List[str]] = Field(None, description="Key conclusions reached in the opinion")
    reliance_limitations: Optional[List[str]] = Field(None, description="Limitations on reliance on the opinion")
    factual_assumptions: Optional[List[str]] = Field(None, description="Key factual assumptions made")
    opinion_date: Optional[date] = Field(None, description="Date the opinion was issued")
    referenced_authorities: Optional[List[str]] = Field(None, description="Tax authorities referenced (codes, regulations, cases)")
    related_to_transaction: Optional[bool] = Field(None, description="Whether the opinion relates to a specific transaction")
    transaction_date: Optional[date] = Field(None, description="Date of the transaction if applicable")
    penalty_protection_intended: Optional[bool] = Field(None, description="Whether the opinion is intended to provide penalty protection")

class TaxRuling(TaxAuthorityDocument):
    """A private tax ruling or determination letter"""
    ruling_id: Optional[str] = Field(None, description="Identification number of the ruling")
    ruling_type: Optional[str] = Field(None, description="Type of ruling (e.g., Private Letter Ruling, Technical Advice Memorandum)")
    issuing_authority: Optional[str] = Field(None, description="Tax authority that issued the ruling")
    requestor: Optional[str] = Field(None, description="Entity that requested the ruling")
    issue_date: Optional[date] = Field(None, description="Date the ruling was issued")
    effective_period: Optional[str] = Field(None, description="Period for which the ruling is effective")
    tax_issues_addressed: Optional[List[str]] = Field(None, description="Tax issues addressed in the ruling")
    key_determinations: Optional[List[str]] = Field(None, description="Key determinations made in the ruling")
    applicable_law: Optional[List[str]] = Field(None, description="Applicable law sections referenced")
    factual_assumptions: Optional[List[str]] = Field(None, description="Factual assumptions on which the ruling is based")
    conditions_imposed: Optional[List[str]] = Field(None, description="Conditions imposed by the ruling")
    reliance_limitations: Optional[List[str]] = Field(None, description="Limitations on reliance on the ruling")
    related_transactions: Optional[List[str]] = Field(None, description="Transactions to which the ruling applies")

# Additional specialized tax document types
class TaxNotice(TaxAuthorityDocument):
    """Notice received from a tax authority"""
    notice_type: Optional[str] = Field(None, description="Type of notice (e.g., Information Request, Deficiency Notice)")
    notice_purpose: Optional[str] = Field(None, description="Purpose of the notice")
    amount_due: Optional[float] = Field(None, description="Amount due according to the notice")
    explanation: Optional[str] = Field(None, description="Explanation provided in the notice")
    correction_required: Optional[bool] = Field(None, description="Whether a correction is required")
    payment_required: Optional[bool] = Field(None, description="Whether a payment is required")
    payment_deadline: Optional[date] = Field(None, description="Deadline for any required payment")
    response_actions: Optional[List[str]] = Field(None, description="Actions taken in response to the notice")
    resolution_date: Optional[date] = Field(None, description="Date the matter was resolved")
    resolution_details: Optional[str] = Field(None, description="Details of how the matter was resolved")

class TaxSettlement(TaxAuthorityDocument):
    """Document related to a tax settlement with authorities"""
    settlement_type: Optional[str] = Field(None, description="Type of settlement")
    original_disputed_amount: Optional[float] = Field(None, description="Original amount in dispute")
    settled_amount: Optional[float] = Field(None, description="Amount agreed in settlement")
    settlement_date: Optional[date] = Field(None, description="Date of the settlement")
    settlement_terms: Optional[str] = Field(None, description="Terms of the settlement")
    waiver_of_penalties: Optional[bool] = Field(None, description="Whether penalties were waived")
    waiver_of_interest: Optional[bool] = Field(None, description="Whether interest was waived")
    confidentiality_provisions: Optional[str] = Field(None, description="Confidentiality provisions in the settlement")
    future_compliance_requirements: Optional[List[str]] = Field(None, description="Future compliance requirements")
    collateral_issues_addressed: Optional[List[str]] = Field(None, description="Collateral issues addressed in settlement")
    approval_requirements: Optional[List[str]] = Field(None, description="Requirements for final approval")

class TaxRiskAssessment(AnalyticalDocument):
    """Document assessing tax risks"""
    risk_areas: Optional[List[str]] = Field(None, description="Areas of tax risk identified")
    risk_ratings: Optional[Dict[str, str]] = Field(None, description="Risk ratings by area (e.g., High, Medium, Low)")
    potential_exposure: Optional[Dict[str, float]] = Field(None, description="Potential financial exposure by risk area")
    likelihood_assessment: Optional[Dict[str, float]] = Field(None, description="Likelihood assessment by risk area")
    mitigation_strategies: Optional[Dict[str, str]] = Field(None, description="Strategies to mitigate identified risks")
    monitoring_procedures: Optional[List[str]] = Field(None, description="Procedures for monitoring risks")
    responsible_parties: Optional[Dict[str, str]] = Field(None, description="Parties responsible for each risk area")
    review_frequency: Optional[str] = Field(None, description="Frequency of risk assessment review")
    previous_issues: Optional[List[str]] = Field(None, description="Previous issues in risk areas")
    industry_benchmarking: Optional[str] = Field(None, description="Benchmarking against industry peers")

class TaxReservesAnalysis(AnalyticalDocument, FinancialDocument):
    """Analysis of tax reserves and uncertain tax positions"""
    accounting_standard: Optional[str] = Field(None, description="Applicable accounting standard (e.g., ASC 740, IAS 12)")
    reporting_period: Optional[str] = Field(None, description="Reporting period covered")
    uncertain_tax_positions: Optional[List[Dict[str, Any]]] = Field(None, description="Details of uncertain tax positions")
    total_reserve_amount: Optional[float] = Field(None, description="Total amount of tax reserves")
    reserve_by_jurisdiction: Optional[Dict[str, float]] = Field(None, description="Reserves by tax jurisdiction")
    reserve_by_issue: Optional[Dict[str, float]] = Field(None, description="Reserves by tax issue")
    technical_merits_analysis: Optional[Dict[str, str]] = Field(None, description="Analysis of technical merits by position")
    probability_assessments: Optional[Dict[str, float]] = Field(None, description="Probability assessments by position")
    reserve_changes: Optional[Dict[str, float]] = Field(None, description="Changes in reserves during the period")
    effective_tax_rate_impact: Optional[float] = Field(None, description="Impact on effective tax rate")
    disclosure_requirements: Optional[List[str]] = Field(None, description="Financial statement disclosure requirements")

class TaxAuditStatus(str, Enum):
    """Status of a tax audit"""
    NOT_STARTED = "not started"
    INITIAL_CONTACT = "initial contact"
    INFORMATION_GATHERING = "information gathering"
    FIELD_WORK = "field work in progress"
    ISSUES_IDENTIFIED = "issues identified"
    PROPOSED_ADJUSTMENTS = "proposed adjustments issued"
    RESPONSE_SUBMITTED = "response submitted"
    NEGOTIATIONS = "negotiations in progress"
    CLOSING_CONFERENCE = "closing conference"
    FINAL_ASSESSMENT = "final assessment issued"
    CLOSED_NO_CHANGE = "closed - no change"
    CLOSED_WITH_ADJUSTMENTS = "closed - with adjustments"
    APPEALED = "appealed"
    LITIGATION = "litigation"

class AuditScope(str, Enum):
    """Scope of a tax audit"""
    COMPREHENSIVE = "comprehensive audit"
    LIMITED_SCOPE = "limited scope audit"
    SPECIFIC_ISSUE = "specific issue audit"
    COMPLIANCE_CHECK = "compliance check"
    CORRESPONDENCE_AUDIT = "correspondence audit"
    FIELD_AUDIT = "field audit"
    OFFICE_AUDIT = "office audit"
    RANDOM_AUDIT = "random audit"
    TARGETED_AUDIT = "targeted audit"

class AuditIssue(BaseModel):
    """Represents a specific issue identified in a tax audit"""
    issue_id: Optional[str] = Field(None, description="Identifier for the issue")
    description: str = Field(..., description="Description of the issue")
    tax_type: TaxType = Field(..., description="Type of tax related to the issue")
    periods_affected: List[str] = Field(default_factory=list, description="Tax periods affected by the issue")
    proposed_adjustment: Optional[float] = Field(None, description="Amount of proposed adjustment")
    penalties_proposed: Optional[float] = Field(None, description="Amount of penalties proposed")
    interest_proposed: Optional[float] = Field(None, description="Amount of interest proposed")
    company_position: Optional[str] = Field(None, description="Company's position on the issue")
    authority_position: Optional[str] = Field(None, description="Tax authority's position on the issue")
    status: Optional[str] = Field(None, description="Current status of the issue")
    resolution: Optional[str] = Field(None, description="How the issue was resolved, if applicable")
    final_adjustment: Optional[float] = Field(None, description="Final adjustment amount, if resolved")
    supporting_documentation: Optional[List[str]] = Field(None, description="Documentation supporting the company's position")
    risk_assessment: Optional[str] = Field(None, description="Assessment of risk related to the issue")
    technical_merits: Optional[str] = Field(None, description="Technical merits of the company's position")

class InformationRequest(BaseModel):
    """Represents an information request during a tax audit"""
    request_id: Optional[str] = Field(None, description="Identifier for the request")
    request_date: date = Field(..., description="Date the request was issued")
    response_due_date: date = Field(..., description="Date by which response is due")
    extended_due_date: Optional[date] = Field(None, description="Extended due date if applicable")
    items_requested: List[str] = Field(..., description="Items requested by the auditor")
    response_status: Optional[str] = Field(None, description="Status of the response")
    response_date: Optional[date] = Field(None, description="Date the response was submitted")
    items_provided: Optional[List[str]] = Field(None, description="Items provided in the response")
    items_not_provided: Optional[List[str]] = Field(None, description="Items not provided and reasons")
    follow_up_requests: Optional[List[str]] = Field(None, description="Follow-up requests from the auditor")
    notes: Optional[str] = Field(None, description="Additional notes about the request")

class TaxAudit(TaxAuthorityDocument):
    """Document related to a tax audit, review, or examination by a taxation authority like Canada Revenue Agency or the IRS"""
    audit_id: Optional[str] = Field(None, description="Identification number of the audit")
    auditing_authority: Optional[str] = Field(None, description="Tax authority conducting the audit")
    tax_types: List[TaxType] = Field(default_factory=list, description="Types of taxes being audited")
    periods_under_audit: Optional[List[str]] = Field(None, description="Tax periods under audit")
    audit_start_date: Optional[date] = Field(None, description="Date the audit began")
    audit_status: Optional[TaxAuditStatus] = Field(None, description="Current status of the audit")
    audit_scope: Optional[AuditScope] = Field(None, description="Scope of the audit")
    audit_trigger: Optional[str] = Field(None, description="What triggered the audit, if known")
    initial_information_request_date: Optional[date] = Field(None, description="Date of initial information request")
    information_provided: Optional[bool] = Field(None, description="Whether requested information has been provided")
    information_requests: Optional[List[InformationRequest]] = Field(None, description="Detailed information requests")
    issues_identified: Optional[List[str]] = Field(None, description="Issues identified by the auditor")
    detailed_issues: Optional[List[AuditIssue]] = Field(None, description="Detailed audit issues")
    proposed_adjustments: Optional[Dict[str, float]] = Field(None, description="Proposed tax adjustments by issue")
    total_proposed_adjustment: Optional[float] = Field(None, description="Total amount of proposed adjustments")
    total_proposed_penalties: Optional[float] = Field(None, description="Total amount of proposed penalties")
    total_proposed_interest: Optional[float] = Field(None, description="Total amount of proposed interest")
    company_responses: Optional[Dict[str, str]] = Field(None, description="Company's responses to identified issues")
    expected_completion_date: Optional[date] = Field(None, description="Expected completion date of the audit")
    actual_completion_date: Optional[date] = Field(None, description="Actual completion date of the audit")
    potential_exposure: Optional[float] = Field(None, description="Estimated potential financial exposure")
    final_assessment_amount: Optional[float] = Field(None, description="Final assessment amount")
    amount_paid: Optional[float] = Field(None, description="Amount paid as a result of the audit")
    audit_representatives: Optional[List[str]] = Field(None, description="Company representatives for the audit")
    external_advisors: Optional[List[str]] = Field(None, description="External advisors assisting with the audit")
    lead_auditor: Optional[str] = Field(None, description="Lead auditor from the tax authority")
    audit_meetings: Optional[List[Dict[str, Any]]] = Field(None, description="Key meetings during the audit")
    statute_of_limitations: Optional[date] = Field(None, description="Statute of limitations expiration date")
    extensions_filed: Optional[List[Dict[str, Any]]] = Field(None, description="Extensions to statute of limitations")
    closing_agreement: Optional[bool] = Field(None, description="Whether a closing agreement was executed")
    closing_agreement_terms: Optional[str] = Field(None, description="Terms of any closing agreement")
    appeal_filed: Optional[bool] = Field(None, description="Whether an appeal was filed")
    appeal_status: Optional[str] = Field(None, description="Status of any appeal")
    lessons_learned: Optional[List[str]] = Field(None, description="Lessons learned from the audit")
    process_improvements: Optional[List[str]] = Field(None, description="Process improvements identified")

class TaxPlanningDocument(AnalyticalDocument):
    """Tax planning document or strategy"""
    planning_strategy_name: Optional[str] = Field(None, description="Name of the tax planning strategy")
    prepared_by: Optional[str] = Field(None, description="Firm or professional who prepared the document")
    preparation_date: Optional[date] = Field(None, description="Date the document was prepared")
    implementation_status: Optional[str] = Field(None, description="Implementation status of the planning strategy")
    target_jurisdictions: Optional[List[str]] = Field(None, description="Jurisdictions targeted by the planning")
    tax_types_addressed: List[TaxType] = Field(default_factory=list, description="Types of taxes addressed")
    expected_tax_benefit: Optional[float] = Field(None, description="Expected tax benefit amount")
    annual_tax_savings: Optional[float] = Field(None, description="Estimated annual tax savings")
    implementation_costs: Optional[float] = Field(None, description="Estimated costs to implement")
    key_steps: Optional[List[str]] = Field(None, description="Key steps in the planning strategy")
    required_restructuring: Optional[str] = Field(None, description="Restructuring required for implementation")
    risks_identified: Optional[List[str]] = Field(None, description="Risks identified with the strategy")
    risk_mitigation_steps: Optional[List[str]] = Field(None, description="Steps to mitigate identified risks")
    reportable_transaction: Optional[bool] = Field(None, description="Whether the strategy is a reportable transaction")
    approval_status: Optional[str] = Field(None, description="Approval status of the strategy")
    approving_parties: Optional[List[str]] = Field(None, description="Parties who approved the strategy")

class TaxIncentiveDocument(ComplianceDocument):
    """Document related to tax incentives, credits, or special regimes"""
    incentive_type: TaxIncentiveType = Field(..., description="Type of tax incentive")
    incentive_description: Optional[str] = Field(None, description="Description of the tax incentive")
    governing_authority: Optional[str] = Field(None, description="Authority governing the incentive")
    qualification_criteria: Optional[List[str]] = Field(None, description="Criteria for qualifying for the incentive")
    application_date: Optional[date] = Field(None, description="Date of application for the incentive")
    approval_date: Optional[date] = Field(None, description="Date the incentive was approved")
    effective_period_start: Optional[date] = Field(None, description="Start date of the effective period")
    effective_period_end: Optional[date] = Field(None, description="End date of the effective period")
    benefit_amount: Optional[float] = Field(None, description="Amount of benefit received or expected")
    qualifying_expenditures: Optional[float] = Field(None, description="Amount of qualifying expenditures")
    compliance_requirements: Optional[List[str]] = Field(None, description="Ongoing compliance requirements")
    reporting_obligations: Optional[List[str]] = Field(None, description="Reporting obligations to maintain the incentive")
    carryforward_available: Optional[bool] = Field(None, description="Whether unused benefits can be carried forward")
    carryforward_period_years: Optional[int] = Field(None, description="Years for which benefits can be carried forward")
    recapture_provisions: Optional[List[str]] = Field(None, description="Provisions for recapture of benefits")
    current_status: Optional[str] = Field(None, description="Current status of the incentive")

class TransferPricingDocument(AnalyticalDocument, TaxDocument):
    """Transfer pricing documentation"""
    documentation_type: Optional[str] = Field(None, description="Type of transfer pricing documentation (e.g., Master File, Local File)")
    covered_entities: Optional[List[str]] = Field(None, description="Entities covered by the documentation")
    covered_transactions: Optional[List[str]] = Field(None, description="Intercompany transactions covered")
    annual_transaction_volume: Optional[Dict[str, float]] = Field(None, description="Volume of transactions by type")
    pricing_methodology: Optional[Dict[str, str]] = Field(None, description="Methodology used for each transaction type")
    benchmark_studies_present: Optional[bool] = Field(None, description="Whether benchmark studies are included")
    comparables_identified: Optional[List[str]] = Field(None, description="Comparable companies identified")
    arm_length_range: Optional[Dict[str, List[float]]] = Field(None, description="Arm's length ranges determined")
    actual_results: Optional[Dict[str, float]] = Field(None, description="Actual results achieved")
    adjustments_made: Optional[Dict[str, float]] = Field(None, description="Adjustments made to achieve arm's length")
    functional_analysis_present: Optional[bool] = Field(None, description="Whether functional analysis is included")
    industry_analysis_present: Optional[bool] = Field(None, description="Whether industry analysis is included")
    risk_assessment: Optional[str] = Field(None, description="Risk assessment for transfer pricing positions")
    prepared_by: Optional[str] = Field(None, description="Firm that prepared the documentation")
    local_filing_requirements_met: Optional[bool] = Field(None, description="Whether documentation meets local requirements")
    apa_in_place: Optional[bool] = Field(None, description="Whether an Advance Pricing Agreement is in place")
    apa_terms: Optional[str] = Field(None, description="Terms of any Advance Pricing Agreement")

class TaxComplianceCalendar(ComplianceDocument):
    """Calendar of tax compliance deadlines and requirements"""
    calendar_period: str = Field(..., description="Period covered by the calendar (e.g., '2023', 'FY2023')")
    filing_obligations: Optional[List[Dict[str, Any]]] = Field(None, description="List of filing obligations")
    payment_obligations: Optional[List[Dict[str, Any]]] = Field(None, description="List of payment obligations")
    information_reporting: Optional[List[Dict[str, Any]]] = Field(None, description="Information reporting requirements")
    estimated_tax_payments: Optional[List[Dict[str, Any]]] = Field(None, description="Estimated tax payment schedule")
    extension_deadlines: Optional[List[Dict[str, Any]]] = Field(None, description="Deadlines for filing extensions")
    responsible_parties: Optional[Dict[str, str]] = Field(None, description="Parties responsible for each obligation")
    completion_status: Optional[Dict[str, str]] = Field(None, description="Status of each obligation")
    recurring_obligations: Optional[List[Dict[str, Any]]] = Field(None, description="Recurring tax obligations")
    special_obligations: Optional[List[Dict[str, Any]]] = Field(None, description="One-time or special obligations")
    notes: Optional[Dict[str, str]] = Field(None, description="Notes on specific obligations")

class TaxAuthorityCorrespondence(TaxAuthorityDocument):
    """Correspondence with tax authorities"""
    correspondence_type: Optional[str] = Field(None, description="Type of correspondence")
    correspondence_direction: Optional[str] = Field(None, description="Direction (Inbound/Outbound)")
    related_matter: Optional[str] = Field(None, description="Matter the correspondence relates to")
    key_points: Optional[List[str]] = Field(None, description="Key points in the correspondence")
    action_items: Optional[List[str]] = Field(None, description="Action items resulting from correspondence")
    response_prepared: Optional[bool] = Field(None, description="Whether a response was prepared")
    response_date: Optional[date] = Field(None, description="Date of any response")
    follow_up_required: Optional[bool] = Field(None, description="Whether follow-up is required")
    follow_up_date: Optional[date] = Field(None, description="Date for any required follow-up")
    correspondence_outcome: Optional[str] = Field(None, description="Outcome of the correspondence")
    archived_location: Optional[str] = Field(None, description="Where the correspondence is archived")

class AuditCycle(BaseModel):
    """Represents a tax audit cycle for a specific jurisdiction and period"""
    jurisdiction: str = Field(..., description="Tax jurisdiction")
    tax_years: List[str] = Field(..., description="Tax years covered in this audit cycle")
    cycle_status: Optional[TaxAuditStatus] = Field(None, description="Status of this audit cycle")
    primary_audits: Optional[List[str]] = Field(None, description="References to primary audit documents")
    cycle_start_date: Optional[date] = Field(None, description="Start date of the audit cycle")
    cycle_end_date: Optional[date] = Field(None, description="End date of the audit cycle")
    cycle_manager: Optional[str] = Field(None, description="Person managing this audit cycle")
    total_adjustments: Optional[float] = Field(None, description="Total adjustments across all audits in cycle")
    total_exposure: Optional[float] = Field(None, description="Total exposure across all audits in cycle")
    key_issues: Optional[List[str]] = Field(None, description="Key issues across all audits in cycle")
    notes: Optional[str] = Field(None, description="Notes about this audit cycle")

class AuditHistory(AnalyticalDocument):
    """Document tracking the history of tax audits for an entity"""
    entity_name: str = Field(..., description="Name of the entity")
    tax_id: Optional[str] = Field(None, description="Tax ID of the entity")
    audit_cycles: List[AuditCycle] = Field(default_factory=list, description="History of audit cycles")
    open_audits: Optional[List[str]] = Field(None, description="References to currently open audits")
    closed_audits: Optional[List[str]] = Field(None, description="References to closed audits")
    audit_frequency: Optional[str] = Field(None, description="Observed frequency of audits")
    high_risk_areas: Optional[List[str]] = Field(None, description="Areas frequently targeted in audits")
    total_historical_adjustments: Optional[Dict[str, float]] = Field(None, description="Total historical adjustments by jurisdiction")
    audit_defense_strategy: Optional[str] = Field(None, description="Overall strategy for audit defense")
    recurring_issues: Optional[List[str]] = Field(None, description="Issues that recur across multiple audits")
    successful_defense_strategies: Optional[List[str]] = Field(None, description="Strategies that have been successful in past audits")
    relationship_notes: Optional[Dict[str, str]] = Field(None, description="Notes on relationships with tax authorities")

class AuditWorkpaper(AnalyticalDocument):
    """Represents a workpaper prepared during a tax audit"""
    workpaper_id: str = Field(..., description="Identifier for the workpaper")
    related_audit_id: str = Field(..., description="ID of the related audit")
    prepared_by: str = Field(..., description="Person who prepared the workpaper")
    preparation_date: date = Field(..., description="Date the workpaper was prepared")
    reviewed_by: Optional[str] = Field(None, description="Person who reviewed the workpaper")
    review_date: Optional[date] = Field(None, description="Date the workpaper was reviewed")
    workpaper_type: str = Field(..., description="Type of workpaper")
    tax_issue: str = Field(..., description="Tax issue addressed in the workpaper")
    tax_periods: List[str] = Field(..., description="Tax periods covered")
    conclusion: str = Field(..., description="Conclusion reached in the workpaper")
    supporting_documents: Optional[List[str]] = Field(None, description="Supporting documents referenced")
    calculations: Optional[Dict[str, Any]] = Field(None, description="Key calculations in the workpaper")
    assumptions: Optional[List[str]] = Field(None, description="Key assumptions made")
    risks_identified: Optional[List[str]] = Field(None, description="Risks identified in the analysis")
    follow_up_items: Optional[List[str]] = Field(None, description="Items requiring follow-up")
    notes: Optional[str] = Field(None, description="Additional notes")

class TaxProvisionDocument(AnalyticalDocument, FinancialDocument):
    """Tax provision or accrual documentation"""
    provision_period: Optional[str] = Field(None, description="Period covered by the provision (e.g., Q1 2023)")
    provision_type: Optional[str] = Field(None, description="Type of provision (e.g., Annual, Quarterly, Interim)")
    provision_methodology: Optional[str] = Field(None, description="Methodology used for the provision")
    current_tax_expense: Optional[float] = Field(None, description="Current tax expense recorded")
    deferred_tax_expense: Optional[float] = Field(None, description="Deferred tax expense recorded")
    total_tax_expense: Optional[float] = Field(None, description="Total tax expense recorded")
    effective_tax_rate: Optional[float] = Field(None, description="Effective tax rate for the period")
    rate_reconciliation: Optional[Dict[str, float]] = Field(None, description="Reconciliation of statutory to effective rate")
    permanent_differences: Optional[Dict[str, float]] = Field(None, description="Permanent differences by type")
    temporary_differences: Optional[Dict[str, float]] = Field(None, description="Temporary differences by type")
    valuation_allowances: Optional[Dict[str, float]] = Field(None, description="Valuation allowances by type")
    unrecognized_tax_benefits: Optional[float] = Field(None, description="Unrecognized tax benefits (FIN 48/ASC 740-10)")
    uncertain_tax_positions: Optional[List[Dict[str, Any]]] = Field(None, description="Details of uncertain tax positions")
    deferred_tax_assets: Optional[Dict[str, float]] = Field(None, description="Deferred tax assets by type")
    deferred_tax_liabilities: Optional[Dict[str, float]] = Field(None, description="Deferred tax liabilities by type")
    net_operating_losses: Optional[Dict[str, float]] = Field(None, description="Net operating losses by jurisdiction")
    tax_credits: Optional[Dict[str, float]] = Field(None, description="Tax credits by type")
    prepared_in_accordance_with: Optional[str] = Field(None, description="Accounting standard used (e.g., GAAP, IFRS)")
    review_level: Optional[str] = Field(None, description="Level of review performed (e.g., Audited, Reviewed)")
    material_weakness_identified: Optional[bool] = Field(None, description="Whether material weaknesses were identified")
    remediation_plan: Optional[str] = Field(None, description="Plan to remediate any weaknesses identified")

class PropertyTaxDocument(ComplianceDocument):
    """Property tax related document"""
    property_address: Optional[str] = Field(None, description="Address of the property")
    property_id: Optional[str] = Field(None, description="Tax identifier for the property")
    property_type: Optional[str] = Field(None, description="Type of property (e.g., commercial, industrial)")
    assessment_date: Optional[date] = Field(None, description="Date of the property assessment")
    assessed_value: Optional[float] = Field(None, description="Assessed value of the property")
    market_value: Optional[float] = Field(None, description="Market value of the property")
    taxable_value: Optional[float] = Field(None, description="Taxable value after exemptions")
    millage_rate: Optional[float] = Field(None, description="Tax rate applied (mills)")
    tax_amount: Optional[float] = Field(None, description="Tax amount assessed")
    payment_due_date: Optional[date] = Field(None, description="Date payment is due")
    exemptions_applied: Optional[List[str]] = Field(None, description="Exemptions applied to the assessment")
    appeal_filed: Optional[bool] = Field(None, description="Whether an appeal has been filed")
    appeal_status: Optional[str] = Field(None, description="Status of any appeal")
    appeal_deadline: Optional[date] = Field(None, description="Deadline for filing an appeal")
    payment_status: Optional[str] = Field(None, description="Status of tax payment")
    special_assessments: Optional[List[Dict[str, Any]]] = Field(None, description="Special assessments applied")

class CustomsDocument(ComplianceDocument):
    """Customs and import tax related document"""
    import_jurisdiction: Optional[str] = Field(None, description="Jurisdiction of import")
    export_jurisdiction: Optional[str] = Field(None, description="Jurisdiction of export")
    imported_goods: Optional[List[str]] = Field(None, description="Goods being imported")
    harmonized_tariff_codes: Optional[List[str]] = Field(None, description="Harmonized tariff codes used")
    customs_value: Optional[float] = Field(None, description="Declared customs value")
    duties_paid: Optional[float] = Field(None, description="Amount of duties paid")
    import_taxes_paid: Optional[float] = Field(None, description="Amount of import taxes paid")
    preferential_treatment_claimed: Optional[bool] = Field(None, description="Whether preferential treatment was claimed")
    preferential_program: Optional[str] = Field(None, description="Preferential program used (e.g., USMCA/NAFTA)")
    certificate_of_origin: Optional[bool] = Field(None, description="Whether certificate of origin was provided")
    broker_used: Optional[str] = Field(None, description="Customs broker used")
    entry_date: Optional[date] = Field(None, description="Date of entry")
    liquidation_date: Optional[date] = Field(None, description="Date of liquidation")
    post_entry_adjustments: Optional[List[Dict[str, Any]]] = Field(None, description="Post-entry adjustments made")
    customs_audit_status: Optional[str] = Field(None, description="Status of any customs audit")
    transfer_pricing_impact: Optional[str] = Field(None, description="Impact of transfer pricing on customs value")
