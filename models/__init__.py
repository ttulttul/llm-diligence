# This file makes the models directory a Python package
import json
from datetime import datetime, date

# Custom JSON encoder that can handle model serialization
class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

from .base import DiligentizerModel
from .contracts import EmploymentContract
from .financial import FinancialStatement
from .legal import (
    SoftwareLicenseAgreement, LicenseGrantType, LicenseScope,
    WarrantyType, LiabilityLimit, DisputeResolutionMethod,
    AcceptanceMechanism, ChangeOfControlRestriction, PricePeriod,
    TerminationProvision, ExclusivityType, RevenueRecognitionType,
    ServiceLevelAgreementType, DataPrivacyRegime, NonCompeteType,
    SourceCodeEscrowType, TransitionServiceType, MaterialAdverseChangeType,
    AssignmentProvisionType
)
from .due_diligence import (
    # Enums
    DocumentStatus, ConfidentialityLevel,
    # Base classes
    DocumentMetadata,
    # Business Due Diligence
    CompanyOverview, IncomeStatement, EmployeeCensus, 
    CustomerContract, SalesBookingData, PricingBook,
    # Accounting Due Diligence
    FinancialStatementDD, AccountsReceivableAging, DeferredRevenueSchedule,
    # Tax Due Diligence
    TaxReturn, TaxContingencyDocument,
    # SaaS Due Diligence
    ServiceLevelAgreement, DisasterRecoveryPlan, 
    SecurityComplianceDocument, ApplicationArchitecture,
    # Tech Due Diligence
    NetworkArchitecture, InternalApplicationInventory, HelpdeskMetrics,
    # Legal Due Diligence
    CorporateStructure, IntellectualPropertyInventory,
    MaterialContractSummary, EmploymentAgreement,
    # Complete Data Room
    DueDiligenceDataRoom
)
from .auto import AutoModel
