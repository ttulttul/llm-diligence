from pydantic import BaseModel, Field, field_serializer
from typing import Optional, Dict, Any, List, Type
from datetime import datetime, date
import json
import importlib
import inspect
import pkgutil
import sys

# Base class for all models
class DiligentizerModel(BaseModel):
    """The foundational model for all document analysis, providing core metadata about analyzed documents.
    This serves as the base class for all specialized document models in the system, tracking essential
    information such as the source document, analysis timestamp, and LLM model used for extraction."""
    source_filename: Optional[str] = Field(None, description="The filename of the source PDF document")
    analyzed_at: Optional[datetime] = Field(None, description="Timestamp when the document was analyzed")
    llm_model: Optional[str] = Field(None, description="The LLM model used for analysis (e.g. Claude model name)")
    
    @field_serializer('analyzed_at')
    def serialize_datetime(self, dt: Optional[datetime], _info):
        """Serialize datetime field to ISO format string"""
        if dt is None:
            return None
        return dt.isoformat()
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override model_dump to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        return data

# Party to an Agreement
class AgreementParty(BaseModel):
    party_name: Optional[str] = Field(None, description="The name of a party to an agreement")

# Base class for all agreements
class Agreement(DiligentizerModel):
    """A legal document establishing rights and obligations between parties, including effective dates and governing law.
    This base class captures the fundamental elements common to all types of agreements, providing
    a foundation for more specialized agreement types like licenses, employment contracts, etc."""
    effective_date: Optional[date] = Field(None, description="The date when the agreement becomes effective")
    parties: List[AgreementParty] = Field(None, description="The parties involved in the agreement")
    governing_law: Optional[str] = Field(None, description="The jurisdiction's laws governing the agreement")

# Base class for customer agreements
class CustomerAgreement(Agreement):
    """A contractual arrangement where a provider delivers services or products to a customer under specific terms and conditions.
    This model represents commercial agreements between service/product providers and their customers,
    capturing key relationship details like term dates, renewal provisions, and party identification."""
    provider_name: str = Field(..., description="The name of the service provider entity")
    customer_name: str = Field(..., description="The name of the customer entity")
    start_date: Optional[date] = Field(None, description="The start date of the agreement")
    end_date: Optional[date] = Field(None, description="The end date of the agreement")
    auto_renews: Optional[bool] = Field(None, description="Whether the agreement automatically renews")

# Base class for license agreements
class LicenseAgreement(Agreement):
    """A legal agreement granting permission to use intellectual property or assets under specified conditions and restrictions.
    This model represents agreements that grant usage rights to intellectual property or other assets,
    capturing the licensor-licensee relationship and the scope and limitations of the granted rights."""
    licensor: str = Field(..., description="The party granting the license")
    licensee: str = Field(..., description="The party receiving the license")
    license_scope: Optional[str] = Field(None, description="The scope of the license grant")
    license_restrictions: Optional[List[str]] = Field(None, description="Restrictions on the license")

# Base class for employment agreements
class EmploymentAgreement(Agreement):
    """A contract establishing the relationship between employer and employee, including work terms, compensation, and obligations.
    This model represents the formal agreement between an employer and employee, capturing essential
    employment details such as parties involved, start date, and compensation structure."""
    employer: str = Field(..., description="The employer entity")
    employee: str = Field(..., description="The employee name")
    start_date: Optional[date] = Field(None, description="Employment start date")
    compensation_description: Optional[str] = Field(None, description="Description of compensation terms")

# Base class for all financial documents
class FinancialDocument(DiligentizerModel):
    """A document containing financial information, reporting, or analysis for an organization over a specific period.
    This model serves as the foundation for all financial document types, capturing common elements
    such as the company name, fiscal period, and currency used in the financial reporting."""
    company_name: Optional[str] = Field(None, description="Name of the company or entity")
    fiscal_year: Optional[str] = Field(None, description="Fiscal year or period of the document")
    currency: Optional[str] = Field(None, description="Currency used in the financial document")

def get_available_models() -> Dict[str, Type[DiligentizerModel]]:
    """Discover all available models in the models package."""
    models_dict = {}
    
    # Import the models package
    import models
    
    # Walk through all modules in the models package
    for _, module_name, _ in pkgutil.iter_modules(models.__path__, models.__name__ + '.'):
        # Import the module
        module = importlib.import_module(module_name)
        
        # Find all DiligentizerModel subclasses in the module
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, DiligentizerModel) and 
                obj != DiligentizerModel and
                obj.__module__ == module_name):  # Check if the class was defined in this module
                # Store the model with a friendly name: module_modelname
                friendly_name = f"{module_name.split('.')[-1]}_{name}"
                models_dict[friendly_name] = obj
                
    return models_dict
