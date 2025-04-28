from promptflow import tool

@tool
def merge_responses(safe_response: str = None, generateReply_output: str = None, 
                   content_check_result: dict = None) -> str:
    # If content is unsafe, use safe_response
    if content_check_result and not content_check_result.get("is_safe", True):
        return safe_response or "I'm sorry, but I cannot process this request."
    
    # If content is sensitive (new condition)
    if content_check_result and content_check_result.get("is_sensitive", False):
        return "I'm unable to process queries about geopolitical conflicts. I'd be happy to help with other questions."
    
    # Check if there was an error in the search process
    if not generateReply_output or generateReply_output.startswith("I apologize"):
        # Look for keywords in original query to provide more specific response
        query = content_check_result.get("original_query", "").lower() if content_check_result else ""
        sensitive_keywords = ["genocide", "gaza", "israel", "palestine", "war crime"]
        
        if any(keyword in query for keyword in sensitive_keywords):
            return "I'm unable to process queries about geopolitical conflicts. I'd be happy to help with other questions."
    
    # Otherwise use the LLM-generated response
    return generateReply_output or "I apologize, but I couldn't generate a response, please provide more details and try again."