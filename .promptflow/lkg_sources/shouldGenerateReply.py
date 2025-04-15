from promptflow import tool

@tool
def should_use_citation_mode(query: str) -> bool:
    # List of generation-related keywords/phrases
    generation_keywords = ["generate", "create", "write", "compose", "draft", 
                          "make up", "invent", "produce a", "give me a"]
    
    query_lower = query.lower()
    
    # Check if query contains generation keywords
    for keyword in generation_keywords:
        if keyword in query_lower:
            return False  # Don't use citation mode for generation requests
            
    return True  # Use citation mode (in-domain) for information requests