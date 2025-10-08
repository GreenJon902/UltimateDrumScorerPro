export function createSvgText(container, textContent, fontSize) {
    // Creates a svg text node with the given attributes.
    // It is added to the container, and is returned.
    // Font size is in mm tall.
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.innerHTML = textContent;
    text.style.fontSize = fontSize + "px";  // SVG will scale px to mm for us
    container.appendChild(text);
    return text;
}


export function updateSvgText(container, what, newValue) {
    // Updates the given attribute (what - "text", "fontSize") for the given component to the new value.
    // This works on SVGs created by createInitialTextComponent.
    
    if (what === "text") {
        svg.querySelector("text").innerHTML = newValue;
    } else if (what === "fontSize") {
        svg.querySelector("text").style.fontSize = newValue + "px";  // SVG will scale px to mm for us
    } else {
        throw "Unknown what"
    }
}

