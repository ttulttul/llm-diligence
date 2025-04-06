from pydantic import BaseModel, Field, field_serializer
from typing import Optional, Dict, Any
from datetime import datetime
import json

# Base class for all models if needed
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
