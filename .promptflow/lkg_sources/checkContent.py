from promptflow import tool

@tool
def check_content(query: str) -> dict:
    # List of potentially problematic terms to filter
    problematic_terms = ["retard", "fuck", "fucker", "nigger", "nigga"]

    # Add geopolitical sensitive topics
    sensitive_topics = ["genocide", "gaza", "palestine", "israel", "war crime", 
                        "ethnic cleansing", "terrorism", "hamas", "hezbollah"]
    
    query_lower = query.lower()
    
    # Check for explicitly problematic terms
    for term in problematic_terms:
        if term in query_lower:
            return {
                "is_safe": False,
                "original_query": query,
                "safe_message": "I'm sorry, but I cannot process content that may violate content policies. Please ask something else."
            }
    
    # Check for sensitive geopolitical topics
    for topic in sensitive_topics:
        if topic in query_lower:
            return {
                "is_safe": True,  # Still technically "safe" but marked as sensitive
                "is_sensitive": True, # New flag for sensitive topics
                "original_query": query,
                "safe_message": "I'm unable to process queries about geopolitical conflicts. I'd be happy to help with other questions."
            }
    
    return {
        "is_safe": True,
        "is_sensitive": False,
        "original_query": query,
        "safe_message": None
    }