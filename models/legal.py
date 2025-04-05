from enum import Enum
from pydantic import Field
from .base import DiligentizerModel

class ChangeOfControlRestriction(str, Enum):
    NO_RESTRICTIONS = "no restrictions"
    CUSTOMER_CONSENT = "customer consent required"
    VENDOR_CONSENT = "vendor consent required"
    BOTH_PARTIES_CONSENT = "both parties consent required"

class SoftwareLicenseAgreement(DiligentizerModel):
    licensor: str = Field(..., description="The party granting the license")
    licensee: str = Field(..., description="The party receiving the license")
    start_date: str = Field(..., description="The start date of the license agreement")
    end_date: str = Field(..., description="The end date of the license agreement")
    auto_renews: bool = Field(..., description="Whether the license automatically renews after the end date")
    change_of_control: ChangeOfControlRestriction = Field(..., description="The restriction type for change of control")
