from pydantic import BaseModel, Field
from typing import Optional

# Base class for all models if needed
class DiligentizerModel(BaseModel):
    """Base class for all diligentizer models"""
    source_filename: Optional[str] = Field(None, description="The filename of the source PDF document")
