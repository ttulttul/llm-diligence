import os
import instructor
from anthropic import Anthropic
from joblib import Memory

# Set up cache directory
cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.cache')
os.makedirs(cache_dir, exist_ok=True)
memory = Memory(cache_dir, verbose=0)

@memory.cache
def cached_llm_invoke(model_name: str, system_message: str, user_content: list, max_tokens: int, 
                     response_model, api_key: str):
    """Cached function to invoke the LLM."""
    anthropic_client = Anthropic(api_key=api_key)
    client = instructor.from_anthropic(
        anthropic_client,
        mode=instructor.Mode.ANTHROPIC_TOOLS
    )
    
    return client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_content},
        ],
        max_tokens=max_tokens,
        response_model=response_model,
    )
