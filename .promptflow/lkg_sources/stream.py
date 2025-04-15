from promptflow import tool

@tool
def stream(paragraph: str) -> str:
    for word in paragraph.split(" "):
        yield word + " "