from promptflow import tool

@tool
def safe_response(content_check_result: dict) -> str:
    if content_check_result and not content_check_result.get("is_safe", True):
        return content_check_result.get("safe_message", "I'm sorry, but I cannot process content that may violate content policies. Please ask something else.")
    return "I'm sorry, but I cannot process this request. Please try asking something else."