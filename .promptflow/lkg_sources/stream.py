from promptflow import tool

@tool
def stream(paragraph: str) -> str:
    if not paragraph:
        yield "I'm sorry, but I couldn't process your request."
        return
        
    for word in paragraph.split(" "):
        yield word + " "