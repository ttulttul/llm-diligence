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
