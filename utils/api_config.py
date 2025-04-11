"""
Utility functions for loading API credentials from environment variables.
This module can be imported in Jupyter notebooks and Python scripts.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_api_keys():
    """
    Get API keys from environment variables.
    
    Returns:
        dict: Dictionary containing API keys
    """
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "typecast_api_key": os.getenv("TYPECAST_API_KEY"),
        "typecast_actor_id": os.getenv("TYPECAST_ACTOR_ID", "606c6b127b9f53b4cd1743f5")  # Default Korean voice
    }

def get_openai_client():
    """
    Initialize and return an OpenAI client using environment variables.
    
    Returns:
        OpenAI: Initialized OpenAI client
    """
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        return OpenAI(api_key=api_key)
    except ImportError:
        print("Error: OpenAI package not installed. Install with: pip install openai")
        return None

def get_typecast_headers():
    """
    Get headers for Typecast API requests.
    
    Returns:
        dict: Headers for Typecast API requests
    """
    typecast_api_key = os.getenv("TYPECAST_API_KEY")
    if not typecast_api_key:
        raise ValueError("TYPECAST_API_KEY environment variable is not set")
    
    return {
        'Authorization': f'Bearer {typecast_api_key}',
        'Content-Type': 'application/json'
    }
