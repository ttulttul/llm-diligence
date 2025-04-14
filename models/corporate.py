from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import Field, BaseModel
from datetime import date, datetime
from .base import DiligentizerModel

class CorporateJurisdiction(str, Enum):
    """Common corporate jurisdictions"""
    CANADA_FEDERAL = "Canada Federal (CBCA)"
    BRITISH_COLUMBIA = "British Columbia"
    ONTARIO = "Ontario"
    ALBERTA = "Alberta"
    QUEBEC = "Quebec"
    US_DELAWARE = "Delaware"
    US_CALIFORNIA = "California"
    US_NEVADA = "Nevada"
    US_WYOMING = "Wyoming"
    UK = "United Kingdom"
    OTHER = "Other"

class ShareClass(str, Enum):
    """Common share class designations"""
    COMMON = "common"
    PREFERRED = "preferred"
    CLASS_A = "class a"
    CLASS_B = "class b"
    CLASS_C = "class c"
    VOTING = "voting"
    NON_VOTING = "non-voting"
    OTHER = "other"

class ShareRights(BaseModel):
    """Rights, privileges, restrictions and conditions attached to shares"""
    share_class: Optional[ShareClass] = Field(None, description="Class designation")
    voting_rights: Optional[bool] = Field(None, description="Whether shares have voting rights")
    dividend_rights: Optional[str] = Field(None, description="Description of dividend rights")
    liquidation_rights: Optional[str] = Field(None, description="Rights upon liquidation or dissolution")
    conversion_rights: Optional[str] = Field(None, description="Conversion rights if applicable")
    redemption_rights: Optional[str] = Field(None, description="Redemption rights if applicable")
    additional_rights: Optional[str] = Field(None, description="Additional rights or conditions")

class DirectorInfo(BaseModel):
    """Information about a corporate director"""
    name: str = Field(..., description="Director's full name")
    address: Optional[str] = Field(None, description="Director's address")
    position: Optional[str] = Field(None, description="Director's position or title if specified")
    appointment_date: Optional[date] = Field(None, description="Date of appointment")

class IncorporatorInfo(BaseModel):
    """Information about a corporate incorporator/founder"""
    name: str = Field(..., description="Incorporator's full name")
    address: Optional[str] = Field(None, description="Incorporator's address")
    signature_present: Optional[bool] = Field(None, description="Whether signature is present on document")

class ShareTransferRestriction(BaseModel):
    """Share transfer restrictions"""
    restriction_type: Optional[str] = Field(None, description="Type of transfer restriction")
    description: str = Field(..., description="Description of the restriction")
    approval_required_by: Optional[List[str]] = Field(None, description="Whose approval is required for transfers")

class CorporateDocument(DiligentizerModel):
    """Base class for all corporate entity documents"""
    company_name: Optional[str] = Field(None, description="Name of the company")
    jurisdiction: Optional[CorporateJurisdiction] = Field(None, description="Jurisdiction of the document")
    document_date: Optional[date] = Field(None, description="Date of the document")
    document_type: Optional[str] = Field(None, description="Type of corporate document")

class CorporateRegistrationDocument(CorporateDocument):
    """Base class for entity registration documents"""
    registration_number: Optional[str] = Field(None, description="Official registration or file number")
    registered_address: Optional[str] = Field(None, description="Registered office address")
    entity_type: Optional[str] = Field(None, description="Type of entity (e.g., Corporation, LLC)")
    registration_date: Optional[date] = Field(None, description="Date of registration or incorporation")
    status: Optional[str] = Field(None, description="Status of the entity (e.g., Active, Dissolved)")

class ArticlesOfIncorporation(CorporateRegistrationDocument):
    """Articles of Incorporation or similar founding document"""
    incorporators: List[IncorporatorInfo] = Field(default_factory=list, description="Incorporators/founders of the entity")
    authorized_shares: Optional[Dict[str, Union[int, str]]] = Field(None, description="Authorized share structure")
    share_classes: List[ShareRights] = Field(default_factory=list, description="Share classes with their rights")
    share_transfer_restrictions: List[ShareTransferRestriction] = Field(default_factory=list, description="Restrictions on share transfers")
    min_directors: Optional[int] = Field(None, description="Minimum number of directors")
    max_directors: Optional[int] = Field(None, description="Maximum number of directors")
    business_restrictions: Optional[str] = Field(None, description="Restrictions on business activities")
    other_provisions: Optional[List[str]] = Field(None, description="Other provisions or restrictions")
    private_company: Optional[bool] = Field(None, description="Whether the company is private/not offering to public")
    borrowing_powers: Optional[bool] = Field(None, description="Whether directors have borrowing powers")
    pre_organization_shares: Optional[bool] = Field(None, description="Whether pre-organization shares were authorized")

class CanadianArticlesOfIncorporation(ArticlesOfIncorporation):
    """Canadian Articles of Incorporation (federal or provincial)"""
    cbca_governed: Optional[bool] = Field(None, description="Whether governed by Canada Business Corporations Act")
    french_name: Optional[str] = Field(None, description="French version of the company name if applicable")
    registered_office_province: Optional[str] = Field(None, description="Province where registered office is located")
    director_residency_compliant: Optional[bool] = Field(None, description="Whether director Canadian residency requirements are met")

class USArticlesOfIncorporation(ArticlesOfIncorporation):
    """US Articles of Incorporation or Certificate of Incorporation"""
    state_of_incorporation: Optional[str] = Field(None, description="State of incorporation")
    close_corporation: Optional[bool] = Field(None, description="Whether incorporated as a close corporation")
    benefit_corporation: Optional[bool] = Field(None, description="Whether incorporated as a benefit corporation")
    franchise_tax_paid: Optional[bool] = Field(None, description="Whether franchise tax was paid")
    indemnification_provisions: Optional[bool] = Field(None, description="Whether director indemnification is provided")
    limited_liability_statement: Optional[bool] = Field(None, description="Whether limited liability statement is included")

class CertificateOfIncorporation(CorporateRegistrationDocument):
    """Certificate issued by authority confirming incorporation"""
    issuing_authority: Optional[str] = Field(None, description="Government body that issued the certificate")
    corporation_number: Optional[str] = Field(None, description="Official corporation number")
    effective_date: Optional[date] = Field(None, description="Effective date of incorporation if different from registration")
    corporate_existence_duration: Optional[str] = Field(None, description="Duration of corporate existence if not perpetual")
    certificate_issued_date: Optional[date] = Field(None, description="Date the certificate was issued")

class CorporateAmendment(CorporateRegistrationDocument):
    """Amendment to corporate registration or structure"""
    amendment_type: Optional[str] = Field(None, description="Type of amendment (e.g., name change, share structure)")
    amendment_description: Optional[str] = Field(None, description="Description of the amendment")
    previous_name: Optional[str] = Field(None, description="Previous name if this is a name change")
    effective_date: Optional[date] = Field(None, description="Date amendment takes effect")
    director_approval_date: Optional[date] = Field(None, description="Date directors approved the amendment")
    shareholder_approval_date: Optional[date] = Field(None, description="Date shareholders approved the amendment")
    approval_votes_percentage: Optional[float] = Field(None, description="Percentage of votes approving the amendment")

class ArticlesOfOrganization(CorporateRegistrationDocument):
    """Articles of Organization for LLC or similar entity"""
    members: List[str] = Field(default_factory=list, description="Initial members of the LLC")
    managers: List[str] = Field(default_factory=list, description="Managers of the LLC if manager-managed")
    member_managed: Optional[bool] = Field(None, description="Whether the LLC is member-managed")
    perpetual_duration: Optional[bool] = Field(None, description="Whether the LLC has perpetual duration")
    purpose: Optional[str] = Field(None, description="Purpose of the LLC")
    dissolution_terms: Optional[str] = Field(None, description="Terms for dissolution")

class CorporateBylaws(CorporateDocument):
    """Corporate bylaws document"""
    adoption_date: Optional[date] = Field(None, description="Date bylaws were adopted")
    meeting_requirements: Optional[Dict[str, str]] = Field(None, description="Requirements for corporate meetings")
    officer_positions: Optional[List[str]] = Field(None, description="Officer positions established")
    director_terms: Optional[str] = Field(None, description="Terms of director service")
    amendment_process: Optional[str] = Field(None, description="Process for amending bylaws")
    quorum_requirements: Optional[Dict[str, str]] = Field(None, description="Quorum requirements for meetings")
    fiscal_year: Optional[str] = Field(None, description="Definition of fiscal year")
    indemnification_provisions: Optional[str] = Field(None, description="Indemnification provisions for directors/officers")

class AnnualReport(CorporateDocument):
    """Annual report or return filed with corporate registry"""
    filing_year: Optional[str] = Field(None, description="Year for which the report is filed")
    filing_date: Optional[date] = Field(None, description="Date the report was filed")
    current_directors: List[DirectorInfo] = Field(default_factory=list, description="List of current directors")
    registered_office: Optional[str] = Field(None, description="Current registered office address")
    mailing_address: Optional[str] = Field(None, description="Mailing address if different from registered office")
    business_activities: Optional[str] = Field(None, description="Current business activities")
    current_status: Optional[str] = Field(None, description="Current status of the corporation")
    shares_issued: Optional[Dict[str, int]] = Field(None, description="Number of shares issued by class")
    annual_fee_paid: Optional[bool] = Field(None, description="Whether annual fee was paid")

class ShareholderAgreement(CorporateDocument):
    """Shareholder agreement document"""
    parties: List[str] = Field(default_factory=list, description="Parties to the agreement")
    effective_date: Optional[date] = Field(None, description="Effective date of the agreement")
    key_provisions: Optional[List[str]] = Field(None, description="Key provisions of the agreement")
    transfer_restrictions: Optional[str] = Field(None, description="Share transfer restrictions")
    right_of_first_refusal: Optional[bool] = Field(None, description="Whether right of first refusal exists")
    tag_along_rights: Optional[bool] = Field(None, description="Whether tag-along rights exist")
    drag_along_rights: Optional[bool] = Field(None, description="Whether drag-along rights exist")
    dispute_resolution: Optional[str] = Field(None, description="Dispute resolution mechanisms")
    non_compete_provisions: Optional[bool] = Field(None, description="Whether non-compete provisions exist")
    dividend_policy: Optional[str] = Field(None, description="Dividend policy if specified")
    termination_provisions: Optional[str] = Field(None, description="Provisions for termination")

class DirectorResolution(CorporateDocument):
    """Directors' resolution document"""
    resolution_type: Optional[str] = Field(None, description="Type of resolution (ordinary, special, consent)")
    resolution_date: Optional[date] = Field(None, description="Date resolution was passed")
    resolution_text: Optional[str] = Field(None, description="Text of the resolution")
    directors_present: List[str] = Field(default_factory=list, description="Directors present at the meeting")
    unanimous: Optional[bool] = Field(None, description="Whether resolution was unanimous")
    meeting_date: Optional[date] = Field(None, description="Date of the meeting where resolution was passed")
    resolution_topic: Optional[str] = Field(None, description="Topic or subject of the resolution")
    voting_results: Optional[Dict[str, int]] = Field(None, description="Results of the vote if not unanimous")

class ShareholderResolution(CorporateDocument):
    """Shareholders' resolution document"""
    resolution_type: Optional[str] = Field(None, description="Type of resolution (ordinary, special)")
    resolution_date: Optional[date] = Field(None, description="Date resolution was passed")
    resolution_text: Optional[str] = Field(None, description="Text of the resolution")
    required_majority: Optional[str] = Field(None, description="Required majority for approval")
    voting_results: Optional[Dict[str, Any]] = Field(None, description="Results of the vote")
    meeting_date: Optional[date] = Field(None, description="Date of the meeting where resolution was passed")
    resolution_topic: Optional[str] = Field(None, description="Topic or subject of the resolution")
    unanimous: Optional[bool] = Field(None, description="Whether resolution was passed unanimously")

class CorporateMinutes(CorporateDocument):
    """Minutes of corporate meetings"""
    meeting_type: Optional[str] = Field(None, description="Type of meeting (board, annual, special)")
    meeting_date: Optional[date] = Field(None, description="Date of the meeting")
    meeting_location: Optional[str] = Field(None, description="Location of the meeting")
    attendees: List[str] = Field(default_factory=list, description="Persons attending the meeting")
    chair: Optional[str] = Field(None, description="Person chairing the meeting")
    secretary: Optional[str] = Field(None, description="Person acting as secretary")
    quorum_present: Optional[bool] = Field(None, description="Whether quorum was present")
    resolutions_passed: Optional[List[str]] = Field(None, description="Resolutions passed at the meeting")
    adjournment_time: Optional[str] = Field(None, description="Time of adjournment")
    next_meeting_date: Optional[date] = Field(None, description="Date of next scheduled meeting")

class ShareCertificate(CorporateDocument):
    """Share certificate document"""
    certificate_number: Optional[str] = Field(None, description="Certificate number")
    shareholder_name: Optional[str] = Field(None, description="Name of the shareholder")
    share_class: Optional[ShareClass] = Field(None, description="Class of shares")
    number_of_shares: Optional[int] = Field(None, description="Number of shares represented")
    issue_date: Optional[date] = Field(None, description="Date of issuance")
    consideration: Optional[str] = Field(None, description="Consideration paid for shares")
    restrictive_legend: Optional[str] = Field(None, description="Text of any restrictive legend")
    transfer_restrictions: Optional[bool] = Field(None, description="Whether transfer restrictions are noted")
    certificate_cancelled: Optional[bool] = Field(None, description="Whether certificate has been cancelled")

class DispositionOfBusinessDocument(CorporateDocument):
    """Document related to disposition of business assets or shares"""
    transaction_type: Optional[str] = Field(None, description="Type of transaction (asset sale, share sale, merger)")
    transaction_date: Optional[date] = Field(None, description="Date of the transaction")
    parties: List[str] = Field(default_factory=list, description="Parties to the transaction")
    assets_transferred: Optional[List[str]] = Field(None, description="Assets transferred if asset sale")
    shares_transferred: Optional[Dict[str, int]] = Field(None, description="Shares transferred if share sale")
    consideration: Optional[str] = Field(None, description="Consideration for the transaction")
    transaction_value: Optional[float] = Field(None, description="Value of the transaction")
    board_approval_date: Optional[date] = Field(None, description="Date of board approval")
    shareholder_approval_date: Optional[date] = Field(None, description="Date of shareholder approval")
    regulatory_approvals: Optional[List[str]] = Field(None, description="Required regulatory approvals")
    closing_conditions: Optional[List[str]] = Field(None, description="Conditions for closing")

class CorporateDissolution(CorporateDocument):
    """Document related to corporate dissolution or winding up"""
    dissolution_type: Optional[str] = Field(None, description="Type of dissolution (voluntary, involuntary)")
    dissolution_date: Optional[date] = Field(None, description="Effective date of dissolution")
    reason_for_dissolution: Optional[str] = Field(None, description="Reason for dissolution")
    directors_at_dissolution: List[str] = Field(default_factory=list, description="Directors at time of dissolution")
    liabilities_addressed: Optional[bool] = Field(None, description="Whether all liabilities have been addressed")
    assets_distributed: Optional[bool] = Field(None, description="Whether all assets have been distributed")
    tax_clearance_obtained: Optional[bool] = Field(None, description="Whether tax clearance was obtained")
    dissolution_approved_by: Optional[str] = Field(None, description="Who approved the dissolution")
    dissolution_filing_date: Optional[date] = Field(None, description="Date dissolution was filed with authority")