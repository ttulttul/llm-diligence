from enum import Enum
from typing import Optional
from pydantic import Field
from .base import DiligentizerModel

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

class SoftwareLicenseAgreement(DiligentizerModel):
    licensor: str = Field(..., description="The party granting the license")
    licensee: str = Field(..., description="The party receiving the license")
    start_date: str = Field(..., description="The start date of the license agreement")
    end_date: str = Field(..., description="The end date of the license agreement")
    auto_renews: bool = Field(..., description="Whether the license automatically renews after the end date")
    change_of_control: ChangeOfControlRestriction = Field(..., description="The restriction type for change of control")
    minimum_price: float = Field(..., description="The minimum price of the license")
    price_period: PricePeriod = Field(..., description="The period for which the price applies")
    pre_payment_requirement: Optional[float] = Field(None, description="The pre-payment requirement amount, None if no pre-payment required")
    termination_provisions: TerminationProvision = Field(..., description="The provisions for terminating the agreement")
