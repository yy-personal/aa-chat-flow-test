from promptflow import tool
from typing import List
from ragcore.formatReplyInputs import format_generate_reply_inputs_core

@tool
def format_generate_reply_inputs(query: str, history: List, chunks: List, max_conversation_tokens: int, max_tokens: int, content_check_result: dict = None) -> object:
  # If content is unsafe, return a safe alternative
  if content_check_result and not content_check_result.get("is_safe", True):
      # Create a safe alternative input that won't trigger the API's content filter
      return {
        'query': "Please respond with a polite message saying you cannot process this request.",
        'conversation': "",
        'documentation': '{"retrieved_documents": []}'
      }
  
  # Normal processing for safe content
  return format_generate_reply_inputs_core(query, history, chunks, max_conversation_tokens, max_tokens)