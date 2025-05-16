from promptflow import tool
import re
from typing import Dict, Any, List, Tuple, Optional

@tool
def should_use_citation_mode(query: str) -> bool:
    """
    Improved version of the citation mode classifier that maintains the original function signature.
    
    Args:
        query: The user query
        
    Returns:
        Boolean indicating whether to use citation mode
    """
    if not query:
        return True
        
    query_lower = query.lower()
    
    # 1. Analysis based on query characteristics
    query_type, confidence = classify_query(query_lower)
    
    # Use citation mode by default for informational queries
    if query_type in ["creative", "generative", "instructional"]:
        return False
    
    # For conversational queries, citation mode depends on the intent
    if query_type == "conversational":
        # Simple greetings or thank you messages should not use citation mode
        if is_simple_greeting_or_thanks(query_lower):
            return False
    
    # For all other queries (primarily informational), use citation mode
    return True

def classify_query(query: str) -> Tuple[str, float]:
    """
    Classify the query into different types with confidence scores.
    
    Args:
        query: User query
        
    Returns:
        Tuple of (query_type, confidence_score)
    """
    # Define pattern sets for different query types
    patterns = {
        "generative": {
            "patterns": [
                r'\b(generate|create|write|compose|draft|make up|invent|produce)\b',
                r'\bgive me (a|an|some) [a-z]+ (of|about|for|on)\b',
                r'\bwrite (a|an) (story|email|letter|report|poem|article|blog post)\b'
            ],
            "keywords": [
                "generate", "create", "write", "compose", "draft", "make", 
                "invent", "song", "poem", "story", "article", "blog", "essay"
            ]
        },
        "instructional": {
            "patterns": [
                r'\bhow (do|can|would|should|to) (i|you|we|one)\b',
                r'\bsteps (for|to)\b',
                r'\b(explain|guide|teach) (me|us) (how|about)\b',
                r'\binstructions (for|on)\b'
            ],
            "keywords": [
                "how to", "steps", "guide", "instruction", "tutorial", "teach me", 
                "explain how", "show me how", "procedure"
            ]
        },
        "conversational": {
            "patterns": [
                r'^(hi|hello|hey|greetings|good morning|good afternoon|good evening)',
                r'^how are you',
                r'^what(\s|\')?s up',
                r'(thanks|thank you|appreciate it)',
                r'(nice|great|awesome|good job|well done)'
            ],
            "keywords": [
                "hello", "hi", "hey", "thanks", "thank you", "appreciate", 
                "how are you", "nice chatting", "good talking"
            ]
        }
    }
    
    # Check each type
    for query_type, pattern_set in patterns.items():
        # Check regex patterns
        for pattern in pattern_set["patterns"]:
            if re.search(pattern, query, re.IGNORECASE):
                # Strong confidence if pattern matches
                return query_type, 0.9
        
        # Check keywords
        for keyword in pattern_set["keywords"]:
            if keyword in query:
                # Moderate confidence for keyword match
                return query_type, 0.7
    
    # Default to informational with medium confidence
    return "informational", 0.6

def is_simple_greeting_or_thanks(query: str) -> bool:
    """
    Detect if the query is just a simple greeting or thanks.
    
    Args:
        query: The user query
        
    Returns:
        True if query is just a greeting or thanks
    """
    greeting_patterns = [
        r'^(hi|hello|hey|greetings)(!|\.|)$',
        r'^(good morning|good afternoon|good evening)(!|\.|)$',
        r'^how are you(\?|!|\.|)$',
        r'^what(\s|\')?s up(\?|!|\.|)$',
        r'^(thanks|thank you|appreciate it)(!|\.|)$',
        r'^(nice|great|awesome|good job|well done)(!|\.|)$'
    ]
    
    # Check if the query matches any simple greeting pattern
    for pattern in greeting_patterns:
        if re.match(pattern, query, re.IGNORECASE):
            return True
    
    # If query is very short (1-3 words) and contains greeting keywords
    words = query.split()
    if len(words) <= 3:
        greeting_words = {"hi", "hello", "hey", "thanks", "thank", "thx", 
                         "cool", "nice", "great", "awesome"}
        if any(word.lower() in greeting_words for word in words):
            return True
    
    return False