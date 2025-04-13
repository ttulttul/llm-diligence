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
    """Base class for all diligentizer models"""
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

# Base class for all agreements
class Agreement(DiligentizerModel):
    """Base class for all types of agreements and contracts"""
    effective_date: Optional[date] = Field(None, description="The date when the agreement becomes effective")
    parties: Optional[List[str]] = Field(None, description="The parties involved in the agreement")
    governing_law: Optional[str] = Field(None, description="The jurisdiction's laws governing the agreement")

# Base class for all financial documents
class FinancialDocument(DiligentizerModel):
    """Base class for all financial documents and statements"""
    company_name: Optional[str] = Field(None, description="Name of the company or entity")
    fiscal_year: Optional[str] = Field(None, description="Fiscal year or period of the document")
    currency: Optional[str] = Field(None, description="Currency used in the financial document")

# Base class for all due diligence documents
class DueDiligenceDocument(DiligentizerModel):
    """Base class for all due diligence related documents"""
    document_id: Optional[str] = Field(None, description="Unique identifier for the document")
    confidentiality_level: Optional[str] = Field(None, description="Level of confidentiality of the document")
    owner: Optional[str] = Field(None, description="Document owner or responsible party")

def get_available_models() -> Dict[str, Type[DiligentizerModel]]:
    """Discover all available models in the models package."""
    models_dict = {}
    
    # Import the models package
    import models
    
    # Walk through all modules in the models package
    for _, module_name, _ in pkgutil.iter_modules(models.__path__, models.__name__ + '.'):
        # Skip the base module
        if module_name.endswith('.base'):
            continue
            
        # Import the module
        module = importlib.import_module(module_name)
        
        # Find all DiligentizerModel subclasses in the module
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, DiligentizerModel) and 
                obj != DiligentizerModel):
                # Store the model with a friendly name: module_modelname
                friendly_name = f"{module_name.split('.')[-1]}_{name}"
                models_dict[friendly_name] = obj
                
    return models_dict
