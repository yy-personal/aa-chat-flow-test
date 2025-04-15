from promptflow import tool

@tool
def merge_responses(safe_response: str = None, generateReply_output: str = None, 
                   content_check_result: dict = None) -> str:
    # If content is unsafe, use safe_response
    if content_check_result and not content_check_result.get("is_safe", True):
        return safe_response or "I'm sorry, but I cannot process this request."
    
    # Otherwise use the LLM-generated response
    return generateReply_output or "I apologize, but I couldn't generate a response. Please try again."