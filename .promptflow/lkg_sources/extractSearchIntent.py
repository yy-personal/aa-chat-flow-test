from promptflow import tool
from typing import List
from ragcore.extractSearchIntent import extract_search_intent_core

@tool
def extract_search_intent(intent, query: str = "") -> List:
    # Add error handling for None intent
    if intent is None:
        print("Warning: Received None intent in extract_search_intent")
        return ["general information"]  # Default fallback when intent is None
    
    try:
        intent_list = extract_search_intent_core(intent)
        
        # Your existing fallback logic for empty arrays
        if not intent_list and query:
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
        
        return intent_list
    except Exception as e:
        # Log the error for debugging
        print(f"Error in extract_search_intent: {str(e)}")
        
        # For sensitive topic queries, return a specific empty or neutral response
        sensitive_keywords = ["genocide", "gaza", "war", "conflict"]
        if query and any(keyword in query.lower() for keyword in sensitive_keywords):
            return []  # Return empty to trigger appropriate message downstream
        
        # General fallback for other errors
        return ["general information"]