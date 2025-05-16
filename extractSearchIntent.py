from promptflow import tool
from typing import List, Optional
from ragcore.extractSearchIntent import extract_search_intent_core
import logging
import re

@tool
def extract_search_intent(intent, query: str = "") -> List:
    """Extract search intents from LLM output with robust error handling and fallbacks.
    
    Args:
        intent: The output from the rewriteIntent LLM tool
        query: The original user query
        
    Returns:
        List of search intent strings
    """
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("extract_search_intent")
    
    # Add error handling for None intent
    if intent is None:
        logger.warning("Received None intent in extract_search_intent")
        return create_fallback_intents(query)
    
    try:
        # Try to extract intents using the core function
        intent_list = extract_search_intent_core(intent)
        
        # If we got an empty list but have a query, generate fallback intents
        if not intent_list and query:
            logger.info(f"No intents extracted, using fallback logic for query: {query}")
            return create_fallback_intents(query)
        
        # Check for quality of extracted intents
        intent_list = validate_and_improve_intents(intent_list, query)
        
        # Apply length limits to avoid overly long intents that might cause problems
        intent_list = [intent[:250] for intent in intent_list]
        
        return intent_list
    
    except Exception as e:
        logger.error(f"Error in extract_search_intent: {str(e)}")
        
        # For sensitive topic queries, return an empty list to trigger appropriate downstream handling
        if is_sensitive_topic(query):
            logger.info(f"Sensitive topic detected in query: {query}")
            return []
        
        # General fallback for other errors
        return create_fallback_intents(query)

def create_fallback_intents(query: str) -> List[str]:
    """Generate fallback search intents when the primary extraction fails."""
    if not query:
        return ["general information"]
    
    # Check if this is a generation request
    generation_keywords = ["generate", "create", "write", "compose", "make", "draft"]
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in generation_keywords):
        # This is a generation request with an empty search intent
        # Add fallback query based on what they're trying to generate
        if "paragraph" in query_lower:
            return ["example paragraphs", "paragraph templates"]
        elif "text" in query_lower:
            return ["text examples", "sample text content"]
        elif "story" in query_lower:
            return ["story examples", "creative writing samples"]
        elif "email" in query_lower:
            return ["email templates", "professional email examples"]
        else:
            # Generic fallback for other generation requests
            return ["content creation examples", "writing templates"]
    
    # For general queries, extract key nouns and generate intents
    # Strip out common question words and stop words for a cleaner search
    cleaned_query = re.sub(r'^(what|how|who|when|where|why|is|are|can|could|would|should|do)\s+', '', query_lower)
    
    # If query is very short (1-2 words), use as is
    if len(cleaned_query.split()) <= 2:
        return [cleaned_query]
    
    # For longer queries, generate variations
    return [
        query.strip(),  # Original query
        cleaned_query.strip(),  # Cleaned query
        " ".join(cleaned_query.split()[:3])  # First 3 words of cleaned query
    ]

def validate_and_improve_intents(intent_list: List[str], query: str) -> List[str]:
    """Validate and potentially improve the extracted intents."""
    if not intent_list:
        return intent_list
    
    # Filter out any empty strings
    intent_list = [intent for intent in intent_list if intent.strip()]
    
    # Ensure each intent has substance (minimum word count)
    intent_list = [intent for intent in intent_list if len(intent.split()) >= 2]
    
    # If we filtered everything out, use the original query
    if not intent_list and query:
        return [query]
    
    return intent_list

def is_sensitive_topic(query: str) -> bool:
    """Check if query contains sensitive topics that should be handled specially."""
    if not query:
        return False
        
    sensitive_keywords = ["genocide", "gaza", "israel", "palestine", "war crime", 
                          "terrorism", "terrorist", "suicide bomb", "ethnic cleansing"]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in sensitive_keywords)
