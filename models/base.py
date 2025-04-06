from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Base class for all models if needed
class DiligentizerModel(BaseModel):
    """Base class for all diligentizer models"""
    source_filename: Optional[str] = Field(None, description="The filename of the source PDF document")
    analyzed_at: Optional[datetime] = Field(None, description="Timestamp when the document was analyzed")
    llm_model: Optional[str] = Field(None, description="The LLM model used for analysis (e.g. Claude model name)")
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override model_dump to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        # Convert datetime objects to ISO format strings
        if data.get("analyzed_at") is not None and isinstance(data["analyzed_at"], datetime):
            data["analyzed_at"] = data["analyzed_at"].isoformat()
        return data
