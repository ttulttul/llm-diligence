from pydantic import Field, EmailStr, HttpUrl, validator, constr, BaseModel
from typing import List, Dict, Optional, Union, Set, Tuple, Any
from datetime import date, datetime
from enum import Enum
from uuid import UUID
import re
from .base import DiligentizerModel


# Common Enums and Base Models

class DocumentStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_UPDATE = "requires_update"


class ConfidentialityLevel(str, Enum):
    PUBLIC = "public"
    CONFIDENTIAL = "confidential"
    HIGHLY_CONFIDENTIAL = "highly_confidential"
    RESTRICTED = "restricted"


class DocumentMetadata(BaseModel):
    """Base metadata for all diligence documents"""
    document_id: str = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Document title")
    description: Optional[str] = Field(None, description="Brief description of document")
    created_date: datetime = Field(..., description="Date document was created")
    last_updated: datetime = Field(..., description="Last modification date")
    owner: str = Field(..., description="Document owner or responsible party")
    status: DocumentStatus = Field(DocumentStatus.PENDING, description="Current document status")
    confidentiality: ConfidentialityLevel = Field(ConfidentialityLevel.CONFIDENTIAL, description="Document confidentiality level")
    comments: Optional[str] = Field(None, description="Additional notes or comments")
    file_path: Optional[str] = Field(None, description="Path to the actual file")


# ------------------------------------------------------------------------------
# 1. BUSINESS DUE DILIGENCE MODELS
# ------------------------------------------------------------------------------

class CompanyOverview(DiligentizerModel):
    """Company overview presentation document"""
    metadata: DocumentMetadata
    year_founded: int = Field(..., description="Year the company was founded")
    business_model: str = Field(..., description="Description of business model")
    target_market: str = Field(..., description="Description of target market")
    competitive_positioning: str = Field(..., description="Market positioning relative to competitors")
    key_differentiators: List[str] = Field(..., description="Core competitive advantages")
    executive_team: List[Dict[str, str]] = Field(..., description="List of executives with names and titles")
    company_history: str = Field(..., description="Brief history of the company")
    organizational_structure: str = Field(..., description="Description of company structure")
    locations: List[str] = Field(..., description="Company office locations")
    product_portfolio: List[str] = Field(..., description="List of products and services")


class IncomeStatement(DiligentizerModel):
    """Historical income statement document"""
    metadata: DocumentMetadata
    fiscal_year: int = Field(..., description="Fiscal year of statement")
    period_start: date = Field(..., description="Start date of reporting period")
    period_end: date = Field(..., description="End date of reporting period")
    currency: str = Field(..., description="Currency of financial figures")
    revenue: float = Field(..., description="Total revenue for period")
    cost_of_revenue: float = Field(..., description="Cost of revenue")
    gross_profit: float = Field(..., description="Gross profit")
    operating_expenses: Dict[str, float] = Field(..., description="Operating expenses by category")
    operating_income: float = Field(..., description="Operating income")
    other_income_expenses: Dict[str, float] = Field(..., description="Other income and expenses")
    income_before_tax: float = Field(..., description="Income before tax")
    tax_expense: float = Field(..., description="Tax expense")
    net_income: float = Field(..., description="Net income")
    ebitda: float = Field(..., description="Earnings before interest, taxes, depreciation and amortization")
    is_audited: bool = Field(..., description="Whether statement is audited")
    accounting_standard: str = Field(..., description="Accounting standard used (GAAP, IFRS)")


class EmployeeCensus(DiligentizerModel):
    """Employee roster document"""
    metadata: DocumentMetadata
    as_of_date: date = Field(..., description="Census data collection date")
    total_employees: int = Field(..., description="Total number of employees")
    employees: List[Dict[str, Any]] = Field(..., description="List of employee records")

    model_config = {
        "json_schema_extra": {
            "example": {
                "employees": [
                    {
                        "id": "EMP001",
                        "name": "John Doe",
                        "title": "Software Engineer",
                        "department": "Engineering",
                        "location": "San Francisco",
                        "hire_date": "2018-05-15",
                        "employment_type": "Full-time",
                        "base_salary": 120000,
                        "bonus_eligible": True,
                        "manager": "Jane Smith",
                        "equity_grants": [{"type": "RSU", "amount": 1000, "grant_date": "2020-01-01"}]
                    }
                ]
            }
        }
    }


class CustomerContract(DiligentizerModel):
    """Customer agreement document"""
    metadata: DocumentMetadata
    customer_name: str = Field(..., description="Name of customer")
    contract_id: str = Field(..., description="Unique contract identifier")
    effective_date: date = Field(..., description="Contract start date")
    expiration_date: date = Field(..., description="Contract end date")
    renewal_type: str = Field(..., description="Auto-renewal, manual, etc.")
    products_services: List[str] = Field(..., description="Products/services covered")
    annual_contract_value: float = Field(..., description="Annual value of contract")
    total_contract_value: float = Field(..., description="Total value over term")
    payment_terms: str = Field(..., description="Payment frequency and terms")
    termination_provisions: str = Field(..., description="Termination clauses")
    sla_terms: Optional[Dict[str, Any]] = Field(None, description="Service level agreement terms")
    change_of_control_provisions: Optional[str] = Field(None, description="Change of control provisions")
    non_standard_terms: Optional[List[str]] = Field(None, description="Any non-standard terms")


class SalesBookingData(DiligentizerModel):
    """Sales booking record document"""
    metadata: DocumentMetadata
    time_period: str = Field(..., description="Time period of data (Q1 2023, etc.)")
    total_bookings: float = Field(..., description="Total bookings value")
    new_vs_expansion: Dict[str, float] = Field(..., description="Split between new and expansion bookings")
    bookings_by_product: Dict[str, float] = Field(..., description="Bookings broken down by product")
    bookings_by_region: Dict[str, float] = Field(..., description="Bookings broken down by region")
    bookings_by_sales_rep: Dict[str, float] = Field(..., description="Bookings by sales representative")
    average_sales_cycle: float = Field(..., description="Average days from lead to close")
    win_rate: float = Field(..., description="Percentage of opportunities won")


class PricingBook(DiligentizerModel):
    """Product pricing documentation"""
    metadata: DocumentMetadata
    effective_date: date = Field(..., description="Effective date of pricing")
    products: List[Dict[str, Any]] = Field(..., description="Product pricing details")
    discount_authority_matrix: Dict[str, Any] = Field(..., description="Discount approval levels")
    special_pricing_terms: Optional[List[str]] = Field(None, description="Special pricing programs")

    model_config = {
        "json_schema_extra": {
            "example": {
                "products": [
                    {
                        "name": "Product X",
                        "sku": "PRD-X-STD",
                        "base_price": 10000,
                        "unit": "per user/year",
                        "tiers": [
                            {"min": 1, "max": 49, "price": 10000},
                            {"min": 50, "max": 199, "price": 8500},
                            {"min": 200, "max": None, "price": 7000}
                        ],
                        "add_ons": [
                            {"name": "Premium Support", "price": 2000}
                        ]
                    }
                ]
            }
        }
    }


# ------------------------------------------------------------------------------
# 2. ACCOUNTING DUE DILIGENCE MODELS
# ------------------------------------------------------------------------------

class FinancialStatementDD(DiligentizerModel):
    """Formal financial statement document"""
    metadata: DocumentMetadata
    statement_type: str = Field(..., description="Income statement, balance sheet, cash flow")
    fiscal_year: int = Field(..., description="Fiscal year of statement")
    period_start: date = Field(..., description="Start date of reporting period")
    period_end: date = Field(..., description="End date of reporting period")
    is_audited: bool = Field(..., description="Whether statement is audited")
    is_consolidated: bool = Field(..., description="Whether statement is consolidated")
    accounting_standard: str = Field(..., description="GAAP, IFRS, etc.")
    currency: str = Field(..., description="Currency of financial figures")
    statement_data: Dict[str, Any] = Field(..., description="Financial statement data")
    notes: Optional[List[str]] = Field(None, description="Financial statement notes")
    auditor: Optional[str] = Field(None, description="Auditing firm if applicable")


class AccountsReceivableAging(DiligentizerModel):
    """AR aging report document"""
    metadata: DocumentMetadata
    as_of_date: date = Field(..., description="Report date")
    total_ar: float = Field(..., description="Total accounts receivable")
    aging_buckets: Dict[str, float] = Field(..., description="AR by aging bucket")
    customer_details: List[Dict[str, Any]] = Field(..., description="Customer-level AR details")
    bad_debt_reserve: float = Field(..., description="Reserve for bad debt")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "aging_buckets": {
                    "current": 500000,
                    "1-30 days": 100000,
                    "31-60 days": 50000,
                    "61-90 days": 25000,
                    "over 90 days": 10000
                }
            }
        }
    }


class DeferredRevenueSchedule(DiligentizerModel):
    """Deferred revenue calculation document"""
    metadata: DocumentMetadata
    as_of_date: date = Field(..., description="Schedule date")
    total_deferred_revenue: float = Field(..., description="Total deferred revenue")
    current_portion: float = Field(..., description="Amount recognized within 12 months")
    long_term_portion: float = Field(..., description="Amount recognized beyond 12 months")
    detail_by_customer: List[Dict[str, Any]] = Field(..., description="Customer-level breakdown")
    revenue_recognition_policy: str = Field(..., description="Description of policy")


# ------------------------------------------------------------------------------
# 3. TAX DUE DILIGENCE MODELS
# ------------------------------------------------------------------------------

class TaxReturn(DiligentizerModel):
    """Tax return document"""
    metadata: DocumentMetadata
    tax_year: int = Field(..., description="Tax year")
    tax_type: str = Field(..., description="Income, sales, property, etc.")
    jurisdiction: str = Field(..., description="Tax jurisdiction")
    filing_status: str = Field(..., description="Filing status")
    filing_date: date = Field(..., description="Date filed")
    extended_due_date: Optional[date] = Field(None, description="Extended deadline if applicable")
    prepared_by: str = Field(..., description="Preparer name/firm")
    total_tax_liability: float = Field(..., description="Total tax liability")
    payments_made: float = Field(..., description="Total payments made")
    balance_due_or_refund: float = Field(..., description="Remaining balance or refund")
    is_amended: bool = Field(False, description="Whether this is an amended return")
    under_audit: bool = Field(False, description="Whether under audit")


class TaxContingencyDocument(DiligentizerModel):
    """Tax contingency disclosure document"""
    metadata: DocumentMetadata
    contingency_type: str = Field(..., description="Type of tax contingency")
    tax_years_affected: List[int] = Field(..., description="Tax years affected")
    jurisdictions: List[str] = Field(..., description="Affected jurisdictions")
    estimated_exposure: Optional[float] = Field(None, description="Estimated financial exposure")
    probability_assessment: str = Field(..., description="Likely, possible, remote")
    description: str = Field(..., description="Description of contingency")
    mitigation_strategy: Optional[str] = Field(None, description="Strategy to address")
    reserve_amount: Optional[float] = Field(None, description="Reserved amount if any")


# ------------------------------------------------------------------------------
# 4. SAAS DUE DILIGENCE MODELS
# ------------------------------------------------------------------------------

class ServiceLevelAgreement(DiligentizerModel):
    """SLA document"""
    metadata: DocumentMetadata
    service_covered: str = Field(..., description="Service covered by SLA")
    effective_date: date = Field(..., description="SLA effective date")
    uptime_commitment: float = Field(..., description="Uptime percentage commitment")
    response_time_commitments: Dict[str, str] = Field(..., description="Response time by severity")
    measurement_methodology: str = Field(..., description="How metrics are measured")
    exclusions: List[str] = Field(..., description="Excluded events/scenarios")
    penalty_provisions: Optional[Dict[str, Any]] = Field(None, description="Penalties for non-compliance")
    reporting_frequency: str = Field(..., description="How often SLA metrics are reported")


class DisasterRecoveryPlan(DiligentizerModel):
    """DR plan document"""
    metadata: DocumentMetadata
    last_updated: date = Field(..., description="Last plan update date")
    recovery_time_objective: str = Field(..., description="RTO commitment")
    recovery_point_objective: str = Field(..., description="RPO commitment")
    critical_systems: List[str] = Field(..., description="Systems covered by plan")
    backup_methodology: str = Field(..., description="Backup approach")
    backup_frequency: str = Field(..., description="How often backups occur")
    backup_retention: str = Field(..., description="How long backups are kept")
    recovery_site_details: Dict[str, str] = Field(..., description="Recovery site information")
    testing_frequency: str = Field(..., description="How often DR is tested")
    last_test_date: date = Field(..., description="Date of last DR test")
    last_test_results: str = Field(..., description="Results of last test")


class SecurityComplianceDocument(DiligentizerModel):
    """Security and compliance documentation"""
    metadata: DocumentMetadata
    compliance_frameworks: List[str] = Field(..., description="Relevant frameworks (SOC2, ISO27001, etc.)")
    certification_status: Dict[str, Any] = Field(..., description="Status of certifications")
    last_audit_date: date = Field(..., description="Date of last compliance audit")
    audit_firm: Optional[str] = Field(None, description="Firm that conducted audit")
    major_findings: Optional[List[str]] = Field(None, description="Major audit findings")
    remediation_status: Optional[str] = Field(None, description="Status of remediation efforts")
    security_controls: Dict[str, Any] = Field(..., description="Key security controls")
    penetration_test_results: Optional[Dict[str, Any]] = Field(None, description="Recent pen test results")
    security_incidents: Optional[List[Dict[str, Any]]] = Field(None, description="Recent security incidents")


class ApplicationArchitecture(DiligentizerModel):
    """Application architecture document"""
    metadata: DocumentMetadata
    application_name: str = Field(..., description="Application name")
    architecture_type: str = Field(..., description="Monolithic, microservices, etc.")
    deployment_model: str = Field(..., description="SaaS, on-prem, hybrid")
    technology_stack: Dict[str, List[str]] = Field(..., description="Tech stack by layer")
    third_party_components: List[Dict[str, str]] = Field(..., description="3rd party components")
    data_storage: Dict[str, Any] = Field(..., description="Data storage approach")
    scalability_provisions: str = Field(..., description="How app scales")
    multi_tenancy_approach: Optional[str] = Field(None, description="Multi-tenancy design")
    diagram_references: Optional[List[str]] = Field(None, description="References to architecture diagrams")


# ------------------------------------------------------------------------------
# 5. TECH DUE DILIGENCE MODELS
# ------------------------------------------------------------------------------

class NetworkArchitecture(DiligentizerModel):
    """Network architecture document"""
    metadata: DocumentMetadata
    network_topology: str = Field(..., description="Network topology description")
    primary_providers: List[str] = Field(..., description="Primary network providers")
    bandwidth_capacity: Dict[str, str] = Field(..., description="Bandwidth by location")
    redundancy_provisions: str = Field(..., description="Network redundancy approach")
    network_security_controls: List[str] = Field(..., description="Security controls")
    vpn_infrastructure: Optional[Dict[str, Any]] = Field(None, description="VPN details")
    internal_segmentation: str = Field(..., description="Network segmentation approach")
    diagram_references: Optional[List[str]] = Field(None, description="References to network diagrams")


class InternalApplicationInventory(DiligentizerModel):
    """Internal application inventory document"""
    metadata: DocumentMetadata
    as_of_date: date = Field(..., description="Inventory date")
    applications: List[Dict[str, Any]] = Field(..., description="List of internal applications")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "applications": [
                    {
                        "name": "Financial System",
                        "vendor": "Oracle",
                        "version": "12.1",
                        "deployment": "Cloud",
                        "business_function": "Finance",
                        "criticality": "High",
                        "users": 25,
                        "annual_cost": 150000,
                        "contract_expiration": "2023-12-31",
                        "integration_points": ["HR System", "CRM"]
                    }
                ]
            }
        }
    }


class HelpdeskMetrics(DiligentizerModel):
    """Helpdesk performance metrics document"""
    metadata: DocumentMetadata
    time_period: str = Field(..., description="Reporting period")
    total_tickets: int = Field(..., description="Total tickets in period")
    tickets_by_category: Dict[str, int] = Field(..., description="Tickets by category")
    tickets_by_priority: Dict[str, int] = Field(..., description="Tickets by priority")
    avg_response_time: Dict[str, float] = Field(..., description="Avg response time by priority")
    avg_resolution_time: Dict[str, float] = Field(..., description="Avg resolution time by priority")
    sla_compliance_rate: float = Field(..., description="Percentage meeting SLA")
    satisfaction_score: Optional[float] = Field(None, description="User satisfaction score")
    recurring_issues: Optional[List[str]] = Field(None, description="Common recurring issues")


# ------------------------------------------------------------------------------
# 6. LEGAL DUE DILIGENCE MODELS
# ------------------------------------------------------------------------------

class CorporateStructure(DiligentizerModel):
    """Corporate structure document"""
    metadata: DocumentMetadata
    parent_entity: Dict[str, Any] = Field(..., description="Parent company details")
    subsidiaries: List[Dict[str, Any]] = Field(..., description="Subsidiary information")
    ownership_percentages: Dict[str, float] = Field(..., description="Ownership by entity")
    incorporation_jurisdictions: Dict[str, str] = Field(..., description="Jurisdictions by entity")
    board_composition: Dict[str, List[str]] = Field(..., description="Board members by entity")
    organizational_chart_reference: Optional[str] = Field(None, description="Reference to org chart")


class IntellectualPropertyInventory(DiligentizerModel):
    """IP inventory document"""
    metadata: DocumentMetadata
    patents: List[Dict[str, Any]] = Field(..., description="Patent details")
    trademarks: List[Dict[str, Any]] = Field(..., description="Trademark details")
    copyrights: List[Dict[str, Any]] = Field(..., description="Copyright details")
    trade_secrets: List[Dict[str, Any]] = Field(..., description="Trade secret details")
    ip_assignment_status: str = Field(..., description="Status of employee/contractor IP assignments")
    third_party_licenses: List[Dict[str, Any]] = Field(..., description="3rd party licenses")
    open_source_usage: Dict[str, Any] = Field(..., description="Open source usage and compliance")
    ip_litigation_history: Optional[List[Dict[str, Any]]] = Field(None, description="IP litigation history")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "patents": [
                    {
                        "title": "Method for data encryption",
                        "filing_date": "2018-06-15",
                        "issue_date": "2020-08-22",
                        "patent_number": "US12345678",
                        "jurisdiction": "United States",
                        "status": "Granted",
                        "inventors": ["Jane Smith", "John Doe"],
                        "assignee": "Company Name, Inc."
                    }
                ]
            }
        }
    }


class MaterialContractSummary(DiligentizerModel):
    """Material contract summary document"""
    metadata: DocumentMetadata
    contract_type: str = Field(..., description="Loan, lease, partnership, etc.")
    counterparty: str = Field(..., description="Other party to contract")
    effective_date: date = Field(..., description="Contract effective date")
    termination_date: Optional[date] = Field(None, description="Termination date if fixed")
    value: Optional[float] = Field(None, description="Contract value if applicable")
    key_obligations: List[str] = Field(..., description="Key obligations")
    termination_provisions: str = Field(..., description="How contract can be terminated")
    change_of_control_provisions: str = Field(..., description="Change of control clauses")
    assignment_provisions: str = Field(..., description="Assignment provisions")
    exclusivity_provisions: Optional[str] = Field(None, description="Exclusivity terms")
    notable_restrictions: Optional[List[str]] = Field(None, description="Notable restrictions")


class EmploymentAgreement(DiligentizerModel):
    """Employment agreement document"""
    metadata: DocumentMetadata
    employee_name: str = Field(..., description="Employee name")
    position: str = Field(..., description="Employee position/title")
    effective_date: date = Field(..., description="Agreement effective date")
    term_type: str = Field(..., description="At-will, fixed term, etc.")
    compensation_terms: Dict[str, Any] = Field(..., description="Compensation details")
    benefits_eligibility: Dict[str, bool] = Field(..., description="Benefits eligibility")
    confidentiality_provisions: bool = Field(..., description="Has confidentiality terms")
    non_compete_provisions: Optional[Dict[str, Any]] = Field(None, description="Non-compete terms")
    non_solicitation_provisions: Optional[Dict[str, Any]] = Field(None, description="Non-solicitation terms")
    ip_assignment_provisions: bool = Field(..., description="Has IP assignment terms")
    termination_provisions: Dict[str, Any] = Field(..., description="Termination terms")
    severance_provisions: Optional[Dict[str, Any]] = Field(None, description="Severance terms")
    dispute_resolution: str = Field(..., description="Dispute resolution method")


# Due Diligence Data Room Structure

class DueDiligenceDataRoom(DiligentizerModel):
    """Complete due diligence data room model"""
    # Business Due Diligence
    company_overview: Optional[CompanyOverview] = None
    income_statements: Optional[List[IncomeStatement]] = None
    employee_census: Optional[EmployeeCensus] = None
    customer_contracts: Optional[List[CustomerContract]] = None
    sales_booking_data: Optional[List[SalesBookingData]] = None
    pricing_books: Optional[List[PricingBook]] = None
    
    # Accounting Due Diligence
    financial_statements: Optional[List[FinancialStatementDD]] = None
    accounts_receivable_aging: Optional[List[AccountsReceivableAging]] = None
    deferred_revenue_schedules: Optional[List[DeferredRevenueSchedule]] = None
    
    # Tax Due Diligence
    tax_returns: Optional[List[TaxReturn]] = None
    tax_contingency_documents: Optional[List[TaxContingencyDocument]] = None
    
    # SaaS Due Diligence
    service_level_agreements: Optional[List[ServiceLevelAgreement]] = None
    disaster_recovery_plans: Optional[List[DisasterRecoveryPlan]] = None
    security_compliance_documents: Optional[List[SecurityComplianceDocument]] = None
    application_architecture_documents: Optional[List[ApplicationArchitecture]] = None
    
    # Tech Due Diligence
    network_architecture_documents: Optional[List[NetworkArchitecture]] = None
    internal_application_inventory: Optional[List[InternalApplicationInventory]] = None
    helpdesk_metrics: Optional[List[HelpdeskMetrics]] = None
    
    # Legal Due Diligence
    corporate_structure: Optional[CorporateStructure] = None
    intellectual_property_inventory: Optional[IntellectualPropertyInventory] = None
    material_contract_summaries: Optional[List[MaterialContractSummary]] = None
    employment_agreements: Optional[List[EmploymentAgreement]] = None
