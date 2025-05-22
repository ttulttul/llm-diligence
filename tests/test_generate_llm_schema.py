import json
from datetime import date

from analysis.analyzer import generate_llm_schema
from pydantic import BaseModel

class SampleModel(BaseModel):
    some_date: date
    some_text: str


def test_generate_llm_schema_includes_date_type():
    schema = generate_llm_schema(SampleModel, as_json=True)
    assert schema['some_date']['type'] == 'string(date)'
    assert schema['some_text']['type'] == 'string'
