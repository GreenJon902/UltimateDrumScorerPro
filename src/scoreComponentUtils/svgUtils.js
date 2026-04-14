// This file contains methods relating to the creation and manipulation of HTML SVG node things.
// These methods should have no concept of any other ideas in the UDSP project, instead they are purely for interacting with nodes and stuff.


function hasDefsNode(svg, definitionType) {
    // Returns true if a <defs> node with the given type has already been created.
    // Note: this is not a child of the defs node, it is the defs node itself.
    
    return svg.querySelector(`[data-definition-type=${definitionType}]`) !== null;
}

function getDefsNode(svg, definitionType) {
    // Gets the <defs> node with the given definitionType.
    // Note: this is not a child of the defs node, it is the defs node itself.
    // If a node with the given type does not exist then it will be greated.
    
    if (hasDefsNode(svg, definitionType)) {
        // Defs node already exists so just return that
        return svg.querySelector(`[data-definition-type=${definitionType}]`);
    } else {
        // Create new defs node 'cause it doesn't exist
        const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
        defs.setAttribute("data-definition-type", definitionType);
        svg.appendChild(defs);
        return defs;
    }
    
}

export function attachDefinition(svg, definitionType, id, node) {
    // Adds a definition for the given node with the given id to the given svg.
    // The definitionType (a string) is just a name used to separate defintiions with different purposes.
    // If a definition with the given id already exists then an error is thrown.
    // If node has an id then an error is thrown, as this will need to be overwritten.
    
    
    // Ensure a definition with this id is not already defined
    if (hasDefinition(svg, definitionType, id)) throw `Definition of type ${definitionType} and id ${id} already exists`;
    
    // Ensure node has no pre-existing id
    if (node.id !== "") throw `Definition node ${definitionType} ${id} ${node} already has an id`;
    
    // Add the definition
    const defs = getDefsNode(svg, definitionType);
    node.id = id;
    defs.appendChild(node);
}

export function hasDefinition(svg, definitionType, id) {
    // Checks whether a definition of the given type and id has already been defined.
    // Returns true if it has, and false if it hasn't.
    
    if (!hasDefsNode(svg, definitionType)) return false;  // If no defs node then there can't be a definition
                                                          // Check if it exists first so we don't create a new node unnecessarily
    
    const defs = getDefsNode(svg, definitionType);
    return defs.querySelector(`#${id}`) !== null;
}

export function createUse(svg, container, definitionType, id, transform) {
    // Creates a use node for the definition with the given type and id.
    // If transform is undefined then it is ignored, otherwise it should be a valid svg transform string.
    // The node will be added to the given container node.

    const node = document.createElementNS("http://www.w3.org/2000/svg", "use");
    node.setAttribute("href", "#" + id);
    if (transform !== undefined) node.setAttribute("transform", transform);
    container.appendChild(node);
}

export function createPath(svg, container, path, transform) {
    // Creates a path node with the given path string.
    // If transform is undefined then it is ignored, otherwise it should be a valid svg transform string.
    // The node will be added to the given container node.

    const node = document.createElementNS("http://www.w3.org/2000/svg", "path");
    node.setAttribute("d", path);
    if (transform !== undefined) node.setAttribute("transform", transform);
    container.appendChild(node);
}

export function createCircle(svg, container, r, cx, cy, transform) {
    // Creates a circle node with the given radius and centre coordinated.
    // If transform is undefined then it is ignored, otherwise it should be a valid svg transform string.
    // The node will be added to the given container node.

    const node = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    node.setAttribute("r", r);
    node.setAttribute("cx", cx);
    node.setAttribute("cy", cy);
    if (transform !== undefined) node.setAttribute("transform", transform);
    container.appendChild(node);
}

export function createGroup(svg, container, transform) {
    // Creates a use node for the definition with the given type and id.
    // If transform is undefined then it is ignored, otherwise it should be a valid svg transform string.
    // If the container node is not null then it will be added to it, otherwise it won't.
    // The created group will be returned.
    
    const node = document.createElementNS("http://www.w3.org/2000/svg", "g");
    if (transform !== undefined) node.setAttribute("transform", transform);
    if (container !== null) container.appendChild(node);
    return node;
}

export function translate(x, y) {
    // Creates a transform string that translates a node by the given x and y distance.
    // Transforms can be joined using string addition.
    return `translate(${x}, ${y})`;
}

export function createCenteredText(svg, container, text, centerX, centerY) {
    // Creates a text node in the container with the given text that is centered on (centerX, centerY).
    // This will return the created node, as well as adding it.
    
    const node = document.createElementNS("http://www.w3.org/2000/svg", "text");
    node.setAttribute("x", centerX);
    node.setAttribute("y", centerY);
    node.setAttribute("dominant-baseline", "middle");  // Center in Y
    node.setAttribute("text-anchor", "middle");  // Center in X
    node.textContent = text;
    node.style.fontSize = "5px";  // Use px as that is scaled to mm due to the SVG viewbox size
    node.style.fontStyle = "italic";
    node.style.fontWeight = "bold";
    container.appendChild(node);
    
    return node;
}
