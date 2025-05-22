from pydantic import Field, BaseModel
from typing import List, Optional
from datetime import date

from .contracts import Agreement 

class StockOptionGrantDetails(BaseModel):
    """Details of the stock option grant itself."""
    granted_shares_count: int = Field(..., description="Total number of shares optioned to the participant as per the agreement or schedule.")
    share_class: str = Field(..., description="Class of shares underlying the option (e.g., 'common shares', 'preferred shares').")
    exercise_price_per_share: float = Field(..., description="Price per share to exercise the option.")
    exercise_price_currency: str = Field(..., description="Currency of the exercise price (e.g., 'CAD', 'USD').")
    # option_period_description is covered by Agreement.term_description
    minimum_exercise_tranche_shares: Optional[int] = Field(None, description="Minimum number of shares that can be exercised at one time, if specified.")

class StockOptionVestingDetails(BaseModel):
    """Details regarding the vesting schedule of the granted options."""
    vesting_schedule_summary: str = Field(..., description="A summary description of the vesting schedule (e.g., '1/12th vests on Options Start Date, then 1/12th monthly').")
    # Further structured fields can be added if more granular parsing is desired, e.g.:
    # initial_vest_fraction_or_count: Optional[str] = Field(None, description="Fraction or count of shares vesting initially.")
    # initial_vest_date_description: Optional[str] = Field(None, description="Description of the initial vesting date or event (e.g., 'Options Start Date', 'Completion of 1 year of service').")
    # subsequent_vest_frequency: Optional[str] = Field(None, description="Frequency of subsequent vesting tranches (e.g., 'monthly', 'quarterly', 'annually').")
    # cliff_period_description: Optional[str] = Field(None, description="Description of any cliff vesting period (e.g., '1-year cliff').")

class StockOptionPostTerminationRules(BaseModel):
    """Rules governing option exercise after termination of participant's eligibility or death."""
    on_cessation_as_eligible_person_summary: str = Field(..., description="Summary of rules if participant ceases to be an eligible person (excluding death), detailing exercise window and conditions.")
    exercise_window_after_cessation_days: Optional[int] = Field(None, description="Number of days to exercise options after ceasing to be an eligible person (e.g., 30 days).")
    on_death_of_participant_summary: str = Field(..., description="Summary of rules if participant dies, detailing who can exercise and the exercise window.")
    exercise_window_after_death_description: Optional[str] = Field(None, description="Period for exercise after participant's death (e.g., '1 year', 'remainder of Option Period or 1 year, whichever is shorter').")

class CompanyRepurchaseRights(BaseModel):
    """Details of the company's right to repurchase shares issued upon option exercise."""
    repurchase_conditions_summary: str = Field(..., description="Summary of conditions under which the company can repurchase issued shares.")
    repurchase_trigger_event_description: Optional[str] = Field(None, description="Specific event triggering the company's repurchase right (e.g., 'Participant ceases to be Eligible Person within 2 years of agreement date').")
    repurchase_window_after_trigger_days: Optional[int] = Field(None, description="Time window for the company to exercise its repurchase right after the trigger event (e.g., 180 days).")
    repurchase_price_description: str = Field(..., description="Description of the price at which the company can repurchase shares (e.g., 'original exercise price', 'fair market value', 'amount paid by Participant').")


class StockOptionAgreement(Agreement):
    """
    A legal agreement granting an individual (participant) the right to purchase a certain
    number of company shares at a predetermined price (exercise price) over a specified period,
    often subject to vesting conditions. This model captures key terms related to stock options,
    including grant details, vesting schedules, exercise rules, and conditions upon termination
    of employment or service.

    The base 'Agreement' class fields are utilized as follows:
    - `agreement_title`: Title of the stock option agreement.
    - `agreement_date`: The "Options Start Date" or similar effective grant date.
    - `effective_date`: Date the agreement becomes legally effective, may be same as `agreement_date` or signature date.
    - `parties`: List containing the grantor company and the participant.
    - `governing_law`: Jurisdiction whose laws govern the agreement.
    - `term_description`: Description of the overall option period during which options can be exercised.
    """
    
    grantor_company_name: str = Field(..., description="Name of the company granting the stock options.")
    grantor_company_jurisdiction: Optional[str] = Field(None, description="Jurisdiction of incorporation for the grantor company (e.g., 'Canada', 'Delaware').")
    participant_name: str = Field(..., description="Name of the individual or entity receiving the option grant.")
    participant_role_description: Optional[str] = Field(None, description="Role or status of the participant relevant to eligibility (e.g., 'Employee', 'Director', 'Consultant', 'Eligible Person as defined in Plan').")

    referenced_stock_option_plan_name: Optional[str] = Field(None, description="Name or identifier of the overarching stock option plan this agreement falls under (e.g., '2023 Equity Incentive Plan', 'the Plan' as defined in the agreement).")
    
    grant_details: StockOptionGrantDetails = Field(..., description="Specifics of the option grant, such as number of shares and exercise price.")
    vesting_details: StockOptionVestingDetails = Field(..., description="Details of the vesting schedule applicable to the granted options.")
    
    exercise_conditions_summary: Optional[str] = Field(None, description="Summary of the procedure for exercising the option (e.g., notice requirements, payment methods).")
    shareholder_rights_pre_exercise_explicitly_denied: bool = Field(True, description="Indicates if the agreement explicitly states that the participant has no shareholder rights (e.g., voting, dividends) for unexercised options.")
    
    post_termination_rules: StockOptionPostTerminationRules = Field(..., description="Rules regarding option exercisability upon termination of the participant's service or in case of death.")
    
    company_repurchase_rights: Optional[CompanyRepurchaseRights] = Field(None, description="Details of any rights the company has to repurchase shares acquired by the participant through option exercise.")
    
    assignability_by_participant_summary: str = Field(..., description="Summary of the participant's ability (or restrictions thereon) to assign or transfer the option or shares acquired.")
    
    # Specific clauses often found in stock option agreements
    regulatory_approval_clause_present: bool = Field(True, description="Indicates if the agreement mentions that the grant or exercise is subject to regulatory approvals.")
    participant_tax_acknowledgement_clause_present: bool = Field(True, description="Indicates if the agreement includes an acknowledgement by the participant regarding tax consequences and non-reliance on company tax advice.")
    time_is_of_essence_clause_present: bool = Field(True, description="Indicates if a 'time is of the essence' clause is present in the agreement.")

    consideration_from_participant_description: Optional[str] = Field(None, description="Description of any nominal or other consideration paid by the participant for the grant of the option itself (e.g., '$10').")

    schedules_referenced: Optional[List[str]] = Field(default_factory=list, description="List of schedules attached to or referenced by the agreement by name or letter (e.g., 'Schedule A - Terms of Option').")

    class Config:
        extra = 'allow' # Allows for any additional fields encountered in specific agreements that are not explicitly part of this model structure.
        # Example: if a document has unique terms in a schedule, they can be captured without breaking the model.
