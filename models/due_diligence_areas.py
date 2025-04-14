from enum import Enum
from typing import List, Dict, Optional
from pydantic import Field
from .base import DiligentizerModel

class DiligenceAreaType(str, Enum):
    """Main categories of due diligence"""
    BUSINESS = "business"
    FINANCIAL = "financial"
    ACCOUNTING = "accounting"
    TAX = "tax"
    TECHNICAL = "technical"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    COMMERCIAL = "commercial"
    REGULATORY = "regulatory"
    HUMAN_RESOURCES = "human_resources"
    INFORMATION_TECHNOLOGY = "information_technology"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    ENVIRONMENTAL = "environmental"
    INSURANCE = "insurance"
    REAL_ESTATE = "real_estate"

class BusinessDiligenceSubArea(str, Enum):
    """Sub-areas within Business due diligence"""
    COMPANY_OVERVIEW = "company_overview"
    MARKET_ANALYSIS = "market_analysis"
    COMPETITIVE_LANDSCAPE = "competitive_landscape"
    BUSINESS_MODEL = "business_model"
    GROWTH_STRATEGY = "growth_strategy"
    CUSTOMER_BASE = "customer_base"
    SALES_PIPELINE = "sales_pipeline"
    PRICING_STRATEGY = "pricing_strategy"
    MARKETING_STRATEGY = "marketing_strategy"
    PRODUCT_ROADMAP = "product_roadmap"

class FinancialDiligenceSubArea(str, Enum):
    """Sub-areas within Financial due diligence"""
    FINANCIAL_STATEMENTS = "financial_statements"
    REVENUE_RECOGNITION = "revenue_recognition"
    CASH_FLOW = "cash_flow"
    CAPITAL_STRUCTURE = "capital_structure"
    DEBT_FINANCING = "debt_financing"
    EQUITY_FINANCING = "equity_financing"
    FINANCIAL_PROJECTIONS = "financial_projections"
    FINANCIAL_CONTROLS = "financial_controls"
    WORKING_CAPITAL = "working_capital"
    PROFITABILITY_ANALYSIS = "profitability_analysis"

class AccountingDiligenceSubArea(str, Enum):
    """Sub-areas within Accounting due diligence"""
    ACCOUNTING_POLICIES = "accounting_policies"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    ACCOUNTS_PAYABLE = "accounts_payable"
    INVENTORY = "inventory"
    FIXED_ASSETS = "fixed_assets"
    DEFERRED_REVENUE = "deferred_revenue"
    AUDIT_HISTORY = "audit_history"
    INTERNAL_CONTROLS = "internal_controls"
    FINANCIAL_REPORTING = "financial_reporting"
    ACCOUNTING_SYSTEMS = "accounting_systems"

class TaxDiligenceSubArea(str, Enum):
    """Sub-areas within Tax due diligence"""
    INCOME_TAX = "income_tax"
    SALES_TAX = "sales_tax"
    PROPERTY_TAX = "property_tax"
    INTERNATIONAL_TAX = "international_tax"
    TAX_COMPLIANCE = "tax_compliance"
    TAX_PLANNING = "tax_planning"
    TAX_DISPUTES = "tax_disputes"
    TAX_CREDITS = "tax_credits"
    TRANSFER_PRICING = "transfer_pricing"
    TAX_STRUCTURE = "tax_structure"

class TechnicalDiligenceSubArea(str, Enum):
    """Sub-areas within Technical due diligence"""
    ARCHITECTURE = "architecture"
    SCALABILITY = "scalability"
    RELIABILITY = "reliability"
    SECURITY = "security"
    CODE_QUALITY = "code_quality"
    TECHNICAL_DEBT = "technical_debt"
    DEVELOPMENT_PROCESSES = "development_processes"
    TESTING_PRACTICES = "testing_practices"
    DEPLOYMENT_PRACTICES = "deployment_practices"
    MONITORING_PRACTICES = "monitoring_practices"

class LegalDiligenceSubArea(str, Enum):
    """Sub-areas within Legal due diligence"""
    CORPORATE_DOCUMENTS = "corporate_documents"
    FINANCING = "financing"
    FINANCIAL = "financial"
    TAX = "tax"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    INFORMATION_TECHNOLOGY = "information_technology"
    MATERIAL_CONTRACTS = "material_contracts"
    EMPLOYEES = "employees"
    PRIVACY = "privacy"
    LITIGATION = "litigation"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    REAL_PROPERTY = "real_property"
    ENVIRONMENTAL = "environmental"
    INSURANCE = "insurance"

class OperationalDiligenceSubArea(str, Enum):
    """Sub-areas within Operational due diligence"""
    SUPPLY_CHAIN = "supply_chain"
    MANUFACTURING = "manufacturing"
    QUALITY_CONTROL = "quality_control"
    LOGISTICS = "logistics"
    CUSTOMER_SERVICE = "customer_service"
    FACILITIES = "facilities"
    EQUIPMENT = "equipment"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    CAPACITY_PLANNING = "capacity_planning"
    VENDOR_MANAGEMENT = "vendor_management"

class CommercialDiligenceSubArea(str, Enum):
    """Sub-areas within Commercial due diligence"""
    CUSTOMER_CONTRACTS = "customer_contracts"
    VENDOR_CONTRACTS = "vendor_contracts"
    PARTNERSHIP_AGREEMENTS = "partnership_agreements"
    DISTRIBUTION_AGREEMENTS = "distribution_agreements"
    LICENSING_AGREEMENTS = "licensing_agreements"
    SALES_TERMS = "sales_terms"
    PURCHASE_TERMS = "purchase_terms"
    CUSTOMER_CONCENTRATION = "customer_concentration"
    VENDOR_CONCENTRATION = "vendor_concentration"
    MARKET_POSITION = "market_position"

class RegulatoryDiligenceSubArea(str, Enum):
    """Sub-areas within Regulatory due diligence"""
    INDUSTRY_REGULATIONS = "industry_regulations"
    PERMITS_AND_LICENSES = "permits_and_licenses"
    COMPLIANCE_PROGRAMS = "compliance_programs"
    REGULATORY_FILINGS = "regulatory_filings"
    REGULATORY_INVESTIGATIONS = "regulatory_investigations"
    REGULATORY_CORRESPONDENCE = "regulatory_correspondence"
    REGULATORY_CHANGES = "regulatory_changes"
    REGULATORY_RISKS = "regulatory_risks"
    REGULATORY_REPORTING = "regulatory_reporting"
    REGULATORY_AUDITS = "regulatory_audits"

class HumanResourcesDiligenceSubArea(str, Enum):
    """Sub-areas within Human Resources due diligence"""
    EMPLOYMENT_AGREEMENTS = "employment_agreements"
    COMPENSATION_PLANS = "compensation_plans"
    BENEFIT_PLANS = "benefit_plans"
    EQUITY_INCENTIVE_PLANS = "equity_incentive_plans"
    EMPLOYEE_HANDBOOK = "employee_handbook"
    HR_POLICIES = "hr_policies"
    LABOR_RELATIONS = "labor_relations"
    WORKFORCE_DEMOGRAPHICS = "workforce_demographics"
    EMPLOYEE_TURNOVER = "employee_turnover"
    TALENT_ACQUISITION = "talent_acquisition"

class ITDiligenceSubArea(str, Enum):
    """Sub-areas within Information Technology due diligence"""
    IT_INFRASTRUCTURE = "it_infrastructure"
    IT_SECURITY = "it_security"
    IT_OPERATIONS = "it_operations"
    IT_GOVERNANCE = "it_governance"
    IT_STRATEGY = "it_strategy"
    IT_PROJECTS = "it_projects"
    IT_BUDGET = "it_budget"
    IT_VENDORS = "it_vendors"
    IT_COMPLIANCE = "it_compliance"
    DISASTER_RECOVERY = "disaster_recovery"

class IPDiligenceSubArea(str, Enum):
    """Sub-areas within Intellectual Property due diligence"""
    PATENTS = "patents"
    TRADEMARKS = "trademarks"
    COPYRIGHTS = "copyrights"
    TRADE_SECRETS = "trade_secrets"
    IP_LICENSES = "ip_licenses"
    IP_LITIGATION = "ip_litigation"
    IP_STRATEGY = "ip_strategy"
    IP_PORTFOLIO = "ip_portfolio"
    IP_PROTECTION = "ip_protection"
    OPEN_SOURCE = "open_source"

class DiligenceAreaMapping(DiligentizerModel):
    """A comprehensive mapping of due diligence areas and their sub-areas.
    This model provides a structured categorization of all possible due diligence topics
    that might be relevant in M&A, investment, or compliance contexts.
    
    It organizes the complex landscape of due diligence into logical categories and subcategories,
    enabling systematic assessment across business, financial, legal, technical, and operational
    domains. The model supports document classification, due diligence planning, and comprehensive
    coverage tracking, ensuring thorough examination of all relevant areas during transaction
    assessment or compliance reviews."""
    
    # Main diligence areas with their sub-areas
    business: List[BusinessDiligenceSubArea] = Field(
        default_factory=lambda: list(BusinessDiligenceSubArea),
        description="Business due diligence sub-areas"
    )
    
    financial: List[FinancialDiligenceSubArea] = Field(
        default_factory=lambda: list(FinancialDiligenceSubArea),
        description="Financial due diligence sub-areas"
    )
    
    accounting: List[AccountingDiligenceSubArea] = Field(
        default_factory=lambda: list(AccountingDiligenceSubArea),
        description="Accounting due diligence sub-areas"
    )
    
    tax: List[TaxDiligenceSubArea] = Field(
        default_factory=lambda: list(TaxDiligenceSubArea),
        description="Tax due diligence sub-areas"
    )
    
    technical: List[TechnicalDiligenceSubArea] = Field(
        default_factory=lambda: list(TechnicalDiligenceSubArea),
        description="Technical due diligence sub-areas"
    )
    
    legal: List[LegalDiligenceSubArea] = Field(
        default_factory=lambda: list(LegalDiligenceSubArea),
        description="Legal due diligence sub-areas"
    )
    
    operational: List[OperationalDiligenceSubArea] = Field(
        default_factory=lambda: list(OperationalDiligenceSubArea),
        description="Operational due diligence sub-areas"
    )
    
    commercial: List[CommercialDiligenceSubArea] = Field(
        default_factory=lambda: list(CommercialDiligenceSubArea),
        description="Commercial due diligence sub-areas"
    )
    
    regulatory: List[RegulatoryDiligenceSubArea] = Field(
        default_factory=lambda: list(RegulatoryDiligenceSubArea),
        description="Regulatory due diligence sub-areas"
    )
    
    human_resources: List[HumanResourcesDiligenceSubArea] = Field(
        default_factory=lambda: list(HumanResourcesDiligenceSubArea),
        description="Human Resources due diligence sub-areas"
    )
    
    information_technology: List[ITDiligenceSubArea] = Field(
        default_factory=lambda: list(ITDiligenceSubArea),
        description="Information Technology due diligence sub-areas"
    )
    
    intellectual_property: List[IPDiligenceSubArea] = Field(
        default_factory=lambda: list(IPDiligenceSubArea),
        description="Intellectual Property due diligence sub-areas"
    )
    
    # Document mapping - maps document types to diligence areas
    document_to_area_mapping: Dict[str, List[DiligenceAreaType]] = Field(
        default_factory=dict,
        description="Mapping of document types to relevant diligence areas"
    )
    
    # Custom mappings for specific use cases
    custom_mappings: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Custom mappings for specific diligence contexts"
    )
    
    @classmethod
    def get_default_mapping(cls) -> "DiligenceAreaMapping":
        """
        Returns a default instance with all areas and sub-areas populated,
        and a basic document mapping.
        """
        mapping = cls()
        
        # Add some basic document mappings as examples
        mapping.document_to_area_mapping = {
            "financial_statement": [DiligenceAreaType.FINANCIAL, DiligenceAreaType.ACCOUNTING],
            "employment_contract": [DiligenceAreaType.LEGAL, DiligenceAreaType.HUMAN_RESOURCES],
            "patent": [DiligenceAreaType.LEGAL, DiligenceAreaType.INTELLECTUAL_PROPERTY],
            "tax_return": [DiligenceAreaType.TAX],
            "customer_contract": [DiligenceAreaType.COMMERCIAL, DiligenceAreaType.LEGAL],
            "software_license": [DiligenceAreaType.LEGAL, DiligenceAreaType.INFORMATION_TECHNOLOGY],
            "service_level_agreement": [DiligenceAreaType.TECHNICAL, DiligenceAreaType.COMMERCIAL],
            "corporate_bylaws": [DiligenceAreaType.LEGAL],
            "privacy_policy": [DiligenceAreaType.LEGAL, DiligenceAreaType.REGULATORY],
            "security_audit": [DiligenceAreaType.INFORMATION_TECHNOLOGY, DiligenceAreaType.TECHNICAL]
        }
        
        return mapping
