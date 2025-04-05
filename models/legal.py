from pydantic import Field
from .base import DiligentizerModel

class SoftwareLicenseAgreement(DiligentizerModel):
    licensor: str = Field(..., description="The party granting the license")
    licensee: str = Field(..., description="The party receiving the license")
    term_duration: str = Field(..., description="The duration of the license agreement")
    change_of_control: str = Field(..., description="The clause explaining what happens on a change of control of either party")
