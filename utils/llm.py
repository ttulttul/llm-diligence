import os
import instructor
from instructor.multimodal import PDF
from anthropic import Anthropic
import json
import hashlib
import diskcache
import functools
from pydantic import BaseModel

def get_claude_model_name():
    """Get the Claude model name from environment variable or use default."""
    return os.environ.get("CLAUDE_MODEL_NAME", "claude-3-7-sonnet-20250219")

# Set up cache directory
cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.cache')
os.makedirs(cache_dir, exist_ok=True)
cache = diskcache.Cache(cache_dir)

def _generate_cache_key(model_name, system_message, user_content, max_tokens, response_model):
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
    
    # Include model class name as part of the key
    model_class_name = response_model.__name__
    
    key_parts = [model_name, system_message, content_str, str(max_tokens), model_class_name]
    combined = "||".join(key_parts)
    return hashlib.md5(combined.encode()).hexdigest()

def format_content_for_anthropic(content):
    """Format content properly for the Anthropic API."""
    if isinstance(content, list):
        formatted_content = []
        for item in content:
            if isinstance(item, str):
                formatted_content.append({"type": "text", "text": item})
            elif isinstance(item, instructor.multimodal.PDF):
                formatted_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": item.data
                    }
                })
            else:
                # Already formatted content
                formatted_content.append(item)
        return formatted_content
    else:
        # Simple text content
        return [{"type": "text", "text": content}]

def cached_llm_invoke(model_name: str, system_message: str, user_content: list, max_tokens: int, 
                     response_model, api_key: str):
    """Function to invoke the LLM with caching support for Pydantic models."""
    # Generate a cache key for this specific request
    cache_key = _generate_cache_key(model_name, system_message, user_content, max_tokens, response_model)
    
    # Check if the result is already cached
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        # Deserialize the cached result
        return response_model.model_validate_json(cached_result)
    
    # Initialize Anthropic client
    anthropic_client = Anthropic(api_key=api_key)
    
    # Format the content properly for the API
    formatted_content = format_content_for_anthropic(user_content)
    
    # Set up instructor client
    client = instructor.from_anthropic(
        anthropic_client,
        mode=instructor.Mode.ANTHROPIC_TOOLS
    )
    
    # Make the API call with instructor
    result = client.chat.completions.create(
        model=model_name,
        system=system_message,
        messages=[
            {"role": "user", "content": formatted_content}
        ],
        max_tokens=max_tokens,
        response_model=response_model
    )
    
    # Cache the result
    serialized_result = result.model_dump_json()
    cache.set(cache_key, serialized_result)
    
    return result
