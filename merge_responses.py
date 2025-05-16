from promptflow import tool
import json
from typing import Optional, Dict, Any

@tool
def merge_responses(safe_response: str = None, generateReply_output: str = None, 
                   content_check_result: dict = None) -> str:
    """
    Intelligent response merging with fallback mechanisms and enhanced error handling.
    
    Args:
        safe_response: Response from safety module
        generateReply_output: Output from LLM generation
        content_check_result: Results from content check
        
    Returns:
        Final merged response
    """
    # Basic null checks - make sure we have something to return
    if not safe_response and not generateReply_output and not content_check_result:
        return "I apologize, but I encountered a technical issue processing your request. Could you please try again?"
    
    # Initialize result tracking
    result_source = "normal"
    result = None
    
    # Handle unsafe content with highest priority
    if content_check_result and not content_check_result.get("is_safe", True):
        result_source = "unsafe"
        result = safe_response or "I'm sorry, but I cannot process this request due to content policy restrictions."
    
    # Handle sensitive content next
    elif content_check_result and content_check_result.get("is_sensitive", False):
        result_source = "sensitive"
        category = content_check_result.get("content_category", "general")
        
        # Customize response based on sensitive content category
        if category == "geopolitical":
            result = "I'm unable to process queries about geopolitical conflicts. I'd be happy to help with other questions."
        elif category == "controversial":
            result = "This topic requires nuanced discussion beyond my current capabilities. I'd be happy to help with other topics."
        else:
            result = safe_response or "I'm not able to adequately address this sensitive topic. Could we discuss something else?"
    
    # Check for obvious error patterns in the LLM output
    elif not generateReply_output or is_error_response(generateReply_output):
        result_source = "error_fallback"
        # Different error handling based on detected patterns
        if not generateReply_output:
            result = "I apologize, but I couldn't generate a complete response. Could you rephrase your question?"
        elif "I apologize" in generateReply_output and "not found" in generateReply_output:
            # Likely a "not found in documents" error
            result = "I don't have enough information to answer this question completely. Could you provide more details or ask a different question?"
        else:
            # Generic error with the original error message
            result = generateReply_output
        
        # Override for sensitive keywords
        if content_check_result and "original_query" in content_check_result:
            query = content_check_result.get("original_query", "").lower()
            sensitive_keywords = ["genocide", "gaza", "israel", "palestine", "war crime"]
            
            if any(keyword in query for keyword in sensitive_keywords):
                result_source = "sensitive_fallback"
                result = "I'm unable to process queries about geopolitical conflicts. I'd be happy to help with other questions."
    
    # Use the standard LLM response if available and no issues detected
    else:
        result_source = "standard"
        result = generateReply_output
    
    # Add response diagnostic if in development mode
    # In production, you would disable this or use a feature flag
    debug_mode = False
    if debug_mode:
        # Only add in development environments
        debug_info = {
            "result_source": result_source,
            "has_content_check": content_check_result is not None,
            "has_safe_response": safe_response is not None and len(safe_response) > 0,
            "has_llm_response": generateReply_output is not None and len(generateReply_output) > 0
        }
        
        # Add debug info at the end in a hidden HTML comment
        result += f"\n\n<!-- Debug: {json.dumps(debug_info)} -->"
    
    return result or "I apologize, but I couldn't generate a response. Please try again with a different question."

def is_error_response(text: str) -> bool:
    """
    Check if the text appears to be an error message from the LLM.
    
    Args:
        text: The text to check
        
    Returns:
        True if text appears to be an error response
    """
    if not text:
        return True
        
    # Common error phrases to check for
    error_phrases = [
        "I apologize, but I couldn't find",
        "The requested information is not available",
        "I don't have enough information",
        "I couldn't process your request",
        "I'm sorry, I don't have access to"
    ]
    
    # Check for obvious error indicators
    for phrase in error_phrases:
        if phrase.lower() in text.lower():
            return True
            
    # Check for extremely short responses (likely errors)
    if len(text.split()) < 5:
        return True
        
    return False