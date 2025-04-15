from promptflow import tool

@tool
def check_content(query: str) -> dict:
    # List of potentially problematic terms to filter
    problematic_terms = ["retard", "offensive", "slur", "racist", "sexist"]
    
    query_lower = query.lower()
    for term in problematic_terms:
        if term in query_lower:
            return {
                "is_safe": False,
                "original_query": query,
                "safe_message": "I'm sorry, but I cannot process content that may violate content policies. Please ask something else."
            }
    
    return {
        "is_safe": True,
        "original_query": query,
        "safe_message": None
    }