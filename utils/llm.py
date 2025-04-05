import os
import instructor
from instructor.multimodal import PDF
from anthropic import Anthropic
from joblib import Memory
import json
import hashlib

def get_claude_model_name():
    """Get the Claude model name from environment variable or use default."""
    return os.environ.get("CLAUDE_MODEL_NAME", "claude-3-7-sonnet-20250219")

# Set up cache directory
cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.cache')
os.makedirs(cache_dir, exist_ok=True)
memory = Memory(cache_dir, verbose=0)

def _generate_cache_key(model_name, system_message, user_content, max_tokens):
    """Generate a unique cache key for the request parameters."""
    # Convert user_content to a stable string representation if it's a list
    if isinstance(user_content, list):
        # Use a custom default function to handle PosixPath objects
        def default_serializer(obj):
            import pathlib
            if isinstance(obj, pathlib.Path):
                return str(obj)
            return str(obj)
            
        content_str = json.dumps(user_content, sort_keys=True, default=default_serializer)
    else:
        content_str = str(user_content)
        
    key_parts = [model_name, system_message, content_str, str(max_tokens)]
    combined = "||".join(key_parts)
    return hashlib.md5(combined.encode()).hexdigest()

# Cache the raw LLM response without Pydantic model conversion
@memory.cache
def _cached_raw_llm_call(cache_key, model_name, system_message, user_content, max_tokens, api_key):
    """Cached function that makes the raw LLM call without Pydantic conversion."""
    anthropic_client = Anthropic(api_key=api_key)
    
    # Format the content properly for the API
    if isinstance(user_content, list):
        # For multimodal content, ensure each item is properly formatted
        formatted_content = []
        for item in user_content:
            if isinstance(item, str):
                formatted_content.append({"type": "text", "text": item})
            elif isinstance(item, instructor.multimodal.PDF):  # PDF object from instructor.multimodal
                # Let instructor handle the PDF formatting for Anthropic API
                formatted_content.append(item)
            else:
                # Already formatted content
                formatted_content.append(item)
    else:
        # Simple text content
        formatted_content = [{"type": "text", "text": user_content}]
    
    response = anthropic_client.messages.create(
        model=model_name,
        system=system_message,
        messages=[
            {"role": "user", "content": formatted_content},
        ],
        max_tokens=max_tokens,
    )
    
    # Extract and return the response content as a string
    return response.content[0].text

def cached_llm_invoke(model_name: str, system_message: str, user_content: list, max_tokens: int, 
                     response_model, api_key: str):
    """Function to invoke the LLM with caching support for Pydantic models."""
    # Generate a cache key for this specific request
    cache_key = _generate_cache_key(model_name, system_message, user_content, max_tokens)
    
    # Get the raw text response from cache or make a new call
    raw_response = _cached_raw_llm_call(
        cache_key, 
        model_name, 
        system_message, 
        user_content, 
        max_tokens, 
        api_key
    )
    
    # Convert the raw response to the Pydantic model
    anthropic_client = Anthropic(api_key=api_key)
    client = instructor.from_anthropic(
        anthropic_client,
        mode=instructor.Mode.ANTHROPIC_TOOLS
    )
    
    # Use instructor to parse the raw text into the desired model
    return client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "assistant", "content": raw_response}
        ],
        response_model=response_model,
        max_tokens=1  # Just need enough to parse, not generate new content
    )
