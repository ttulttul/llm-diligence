import os
from pydantic import BaseModel, Field
from typing import Optional
import instructor
from anthropic import Anthropic
from instructor.multimodal import PDF

# Define a Pydantic model for a software license agreement
class SoftwareLicenseAgreement(BaseModel):
    licensor: str = Field(..., description="The party granting the license")
    licensee: str = Field(..., description="The party receiving the license")
    term_duration: str = Field(..., description="The duration of the license agreement")
    change_of_control: str = Field(..., description="The clause explaining what happens on a change of control of either party")

# Retrieve your Anthropic API key (make sure to set the environment variable)
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("Please set the ANTHROPIC_API_KEY environment variable.")

# Initialize the Anthropic client and Instructor with tool support
anthropic_client = Anthropic(api_key=API_KEY)
client = instructor.from_anthropic(
    anthropic_client,
    mode=instructor.Mode.ANTHROPIC_TOOLS  # Use Anthropic's tool calling API for structured output
)

# Load the PDF file for analysis (ensure "software_license.pdf" exists in your working directory)
pdf_input = PDF.from_path("software_license.pdf")

# Prepare a prompt that instructs the model to extract key details from the license agreement.
# The instructions include a description of the expected JSON format.
prompt = (
    "You are a legal document analyst. Analyze the following software license agreement "
    "and extract the key details. Your output must be valid JSON matching this exact schema: "
    "{"
    "  \"licensor\": \"<string: the party granting the license>\", "
    "  \"licensee\": \"<string: the party receiving the license>\", "
    "  \"term_duration\": \"<string: duration of the agreement, e.g., '2 years', 'perpetual'>\", "
    "  \"change_of_control\": \"<string: what happens on a change of control of either party>\""
    "}. "
    "Output only the JSON."
)

try:
    # Call Claude 3.7 Sonnet with the prompt and the PDF content.
    response = client.chat.completions.create(
        model="claude-3.7-sonnet",  # Use Claude 3.7 Sonnet for hybrid reasoning
        messages=[
            {"role": "system", "content": "You are a legal analyst."},
            {"role": "user", "content": [prompt, pdf_input]},
        ],
        max_tokens=1000,
        response_model=SoftwareLicenseAgreement,  # Automatically parse output into our Pydantic model
    )

    # Print the structured result as formatted JSON.
    print("Extracted Software License Agreement Details:")
    print(response.model_dump_json(indent=2))
except Exception as e:
    print(f"An error occurred during analysis: {e}")
