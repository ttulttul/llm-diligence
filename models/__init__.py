# This file makes the models directory a Python package
import json
from datetime import datetime, date

# Custom JSON encoder that can handle model serialization
class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

from .base import DiligentizerModel, FinancialDocument
from .contracts import (
    Agreement,
    AgreementParty,
    CommercialAgreement,
    CustomerAgreement,
    LicenseAgreement,
    EmploymentAgreement
)
from .contracts import EmploymentContract
from .financial import FinancialStatement
from .tax import (
    TaxDocument, ComplianceDocument, AnalyticalDocument, TaxAuthorityDocument,
    ProfessionalTaxAdvisoryDocument, TaxReturn, CorporateTaxReturn, PassthroughTaxReturn,
    TaxAssessment, TaxDispute, ProfessionalTaxOpinion, TaxRuling, TaxNotice,
    TaxSettlement, TaxRiskAssessment, TaxReservesAnalysis, TaxAudit, TaxPlanningDocument,
    TaxIncentiveDocument, TransferPricingDocument, TaxComplianceCalendar,
    TaxAuthorityCorrespondence, AuditHistory, AuditWorkpaper, TaxProvisionDocument,
    PropertyTaxDocument, CustomsDocument
)
from .legal import (
    SoftwareLicenseAgreement, LicenseGrantType, LicenseScope,
    WarrantyType, LiabilityLimit, DisputeResolutionMethod,
    AcceptanceMechanism, ChangeOfControlRestriction, PricePeriod,
    TerminationProvision, ExclusivityType, RevenueRecognitionType,
    ServiceLevelAgreementType, DataPrivacyRegime, NonCompeteType,
    SourceCodeEscrowType, TransitionServiceType, MaterialAdverseChangeType,
    AssignmentProvisionType
)
from .cloud import CloudServiceType, CloudServiceAgreement
from .due_diligence_areas import (
    # Main diligence area enum
    DiligenceAreaType,
    # Sub-area enums
    BusinessDiligenceSubArea,
    FinancialDiligenceSubArea,
    AccountingDiligenceSubArea,
    TaxDiligenceSubArea,
    TechnicalDiligenceSubArea,
    LegalDiligenceSubArea,
    OperationalDiligenceSubArea,
    CommercialDiligenceSubArea,
    RegulatoryDiligenceSubArea,
    HumanResourcesDiligenceSubArea,
    ITDiligenceSubArea,
    IPDiligenceSubArea,
    # Main mapping model
    DiligenceAreaMapping
)
from .auto import AutoModel
