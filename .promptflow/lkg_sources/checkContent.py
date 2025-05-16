from promptflow import tool
import re
from typing import Dict, Any, List, Tuple

@tool
def check_content(query: str) -> Dict[str, Any]:
    """
    Enhanced content checking system with multi-tier classification and context awareness.
    
    Args:
        query: The user query to check
        
    Returns:
        Dict containing safety assessment and handling instructions
    """
    # Initialize result with default safe values
    result = {
        "is_safe": True,
        "is_sensitive": False,
        "original_query": query,
        "safe_message": None,
        "severity_level": 0,  # 0=safe, 1=caution, 2=sensitive, 3=unsafe
        "content_category": "general",
        "handling_strategy": "normal"
    }
    
    if not query or query.strip() == "":
        return result
    
    query_lower = query.lower()
    
    # Multi-tier classification system
    severity, category = classify_content(query_lower)
    result["severity_level"] = severity
    result["content_category"] = category
    
    # Determine handling based on severity
    if severity >= 3:
        result["is_safe"] = False
        result["handling_strategy"] = "block"
        result["safe_message"] = "I'm sorry, but I cannot process content that may violate content policies. Please ask something else."
    elif severity == 2:
        result["is_sensitive"] = True
        result["handling_strategy"] = "caution"
        
        # Customize message based on category
        if category == "geopolitical":
            result["safe_message"] = "I'm unable to process queries about geopolitical conflicts. I'd be happy to help with other questions."
        elif category == "controversial":
            result["safe_message"] = "This topic requires nuanced discussion that's beyond my current capabilities. I'd be happy to help with other questions."
        else:
            result["safe_message"] = "I'm not able to adequately address this sensitive topic. Could we discuss something else?"
    
    return result

def classify_content(text: str) -> Tuple[int, str]:
    """
    Multi-tier content classification system.
    
    Returns:
        Tuple of (severity_level, category)
    """
    # Category definitions with terms and severity levels
    categories = {
        "explicit": {
            "terms": [
                "fuck", "fucker", "fucking", "motherfuck", "retard", "nigger", "nigga", 
                "faggot", "cunt", "cock", "dick", "pussy", "asshole", "bitch"
            ],
            "severity": 3,
            "whole_word_only": True  # Only match whole words to avoid false positives
        },
        "geopolitical": {
            "terms": [
                "genocide", "gaza", "palestine", "israel", "war crime", "ethnic cleansing", 
                "hamas", "hezbollah", "iran israel", "russia ukraine", "taiwan china"
            ],
            "severity": 2,
            "whole_word_only": False
        },
        "controversial": {
            "terms": [
                "abortion", "euthanasia", "suicide", "assisted dying", "gun control", 
                "gun rights", "mass shooting", "terrorist", "9/11 truth"
            ],
            "severity": 2,
            "whole_word_only": False
        },
        "potentially_harmful": {
            "terms": [
                "how to hack", "steal password", "bypass security", "make bomb", 
                "commit fraud", "social security number", "credit card hack"
            ],
            "severity": 3,
            "whole_word_only": False
        }
    }
    
    # Check each category
    for category, config in categories.items():
        for term in config["terms"]:
            if config["whole_word_only"]:
                # Match whole words only
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, text):
                    return config["severity"], category
            else:
                # Match anywhere
                if term in text:
                    return config["severity"], category
    
    # Default: safe, general content
    return 0, "general"