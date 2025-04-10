from promptflow import tool

@tool
def stream(paragraph: str) -> str:
    if paragraph is None:
        paragraph = ""
    for word in paragraph.split(" "):
        yield word + " "