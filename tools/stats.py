import os
import re

def getJsCode(strip=True, html=True) -> list[str]:
    """
    Gets every line of js code in ../src/. 
    If strip is true then the lines will be stripped (of whitespace at the starts and ends).
    If html is true then the js code between <script> tags in .html files will be included.
    """

    lines = []

    for (root, dirs, files) in os.walk("../src"):
        for file in files:
            path = os.path.join(root, file)
            if file.endswith(".js"): 
                for line in open(path, "r").read().split("\n"):
                    if strip:
                        line = line.strip()
                    lines.append(line)
            elif file.endswith(".html"):
                for match in re.finditer(r"<script.*?>(.*)<\/script>", open(path, "r").read(), re.MULTILINE | re.DOTALL):
                    match = match.groups()[0]
                    for line in match.split("\n"):
                        if strip:
                            line = line.strip()
                        lines.append(line)
                 
    return lines
    

# Get total js line count
print("Total:", len(getJsCode()))
print("Whitespace:", sum([line == "" for line in getJsCode()]))
print("Non-Whitespace:", sum([line != "" for line in getJsCode()]))
print("Comment(Start):", sum([line.startswith("//") for line in getJsCode()]))
print("Comment(Start+Contain):", sum(["//" in line for line in getJsCode()]))
print("Non-Comment(Start):", sum([not line.startswith("//") for line in getJsCode()]))
print("Code:", sum([line != "" and not line.startswith("//") for line in getJsCode()]))
