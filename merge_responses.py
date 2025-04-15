from promptflow import tool

@tool
def merge_responses(safe_response: str = None, generateReply_output: str = None) -> str:
    # Return whichever response is not None
    # If generateReply_output is available, use that, otherwise use safe_response
    if generateReply_output is not None:
        return generateReply_output
    return safe_response or "I'm sorry, but I cannot process this request."