import {Symbols, SvgInstruction} from "../symbols.js";

function createSymbolGroup(symbolId) {
    // Creates a svg group node for the given symbol. Also returns any requisite symbols (parts, etc).
    // Returns {group: SvgNode, requisites: Set<symbolId>}.

    // Figure out how to draw the given symbol
    const svgInstructions = Symbols.getSymbolInstructions(symbolId);
    console.log(svgInstructions);
    
    // Create a group node that will contain the executed svg instructions
    const symbolContainer = document.createElementNS("http://www.w3.org/2000/svg", "g");
    
    // Convert the svg instructions to actual nodes and add them to the container
    const parentNode = new Array(symbolContainer);  // Since we can push and pop transformations, we need a stack
    const requisites = new Set();
    for (let i=0; i<svgInstructions.length; i++) {
        const instr = svgInstructions[i].computeSubstitutions();
        
        let node;
        // Convert instr into a node
        if (instr.type === SvgInstruction.PATH) {
            node = document.createElementNS("http://www.w3.org/2000/svg", "path");
            node.setAttribute("d", instr.path);
        } else if (instr.type === SvgInstruction.CIRCLE) {
            node = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            node.setAttribute("r", instr.r);
            node.setAttribute("cx", instr.cx);
            node.setAttribute("cy", instr.cy);
        } else if (instr.type === SvgInstruction.USE) {
            node = document.createElementNS("http://www.w3.org/2000/svg", "use");
            node.setAttribute("href", "#" + instr.id);
            requisites.add(instr.id);
            
        // These two are special
        } else if (instr.type === SvgInstruction.PUSH_TRANSFORM) {
            node = document.createElementNS("http://www.w3.org/2000/svg", "g");
            node.setAttribute("transform", instr.transform);
            parentNode.push(node);
            continue;  // Continue as there is no node to add to the last parent node on this iteration
        } else if (instr.type === SvgInstruction.POP_TRANSFORM) {
            if (parentNode.length <= 1) throw "SvgInstruction tried to pop when nothing in stack";  // <= 1 as the 0th item is the symbolContainer
            node = parentNode.pop();
            
        } else {
            throw "Unknown type " + type;
        }
        
        // Add node to the last parentNode (as that was most recently pushed)
        parentNode[parentNode.length - 1].appendChild(node);
    }
    
    if (parentNode.length > 1) throw "SvgInstructions did not clean stack";  // There were more push instructions than pop instructions
    
    // Return
    return {group: symbolContainer, requisites: Object.freeze(requisites)};
    
}


function attachSymbol(svg, symbolId) {
    // Adds a definition for the given symbolId inside of the svg.
    // These are placed inside a defs node with "data-symbol-defs", with the given symbolId as their ids.
    
    // Get defs node
    let _defs = svg.querySelector("[data-symbol-defs]");
    if (_defs === null) {
        _defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
        _defs.setAttribute("data-symbol-defs", "");
        svg.appendChild(_defs);
    }
    const defs = _defs;
    
    // Check if the given symbol is already attached
    if (defs.querySelector("#" + symbolId) !== null) return;
    
    // Attatch this new symbol and any requisites
    const {group, requisites} = createSymbolGroup(symbolId);
    group.setAttribute("id", symbolId);
    defs.appendChild(group);
    requisites.forEach(r => attachSymbol(svg, r));
}

function drawSymbol(svg, symbolId, x, y) {
    // Draws the symbol with the given id to the given svg at the given coordinates.
    
    // Make sure the definition of this symbol has been added
    attachSymbol(svg, symbolId);
    
    // Create and add a node which calls on the definition
    const node = document.createElementNS("http://www.w3.org/2000/svg", "use");
    node.setAttribute("href", "#" + symbolId);
    node.setAttribute("transform", `translate(${x} ${y})`);
    svg.appendChild(node);
}


export function renderScoreComponentFromInstructionsAndSpacing(svg, instructions, spacing) {
    // svg: SVG
    // instructions: Array<RenderInstruction>
    // spacing: {
    //     instructionXs: [float],  // The x-coordinate of a stem, or the right edge of a rest or decoration, or the location of a contract hook (when required).
    //     drumYs: {str: float},  // A map from drum-id to anchor (the location where the symbol attaches to the stem) y-level.
    //     restCenterYs: [float],  // The y line that rests should be centred on. The index corresponds to the number of previous REST instructions.
    //     contractCenterYs: [float],  // The y line that contracts should be centred on. The index corresponds to the number of previous CONTRACT_START instructions.
    //     stemTopYs: [float],  // The y-level that should be the top of each stem. The index corresponds to the number of previous stems drawn.
    //     decorationCenterYs: [float]  // The y-level that decorations should be centres on. The index corresponds to the number of previous DECORATION instructions.
    // }
    //
    // Renders the given instructions to the given svg using the given spacing data.
    
    for (let instrI = 0; instrI < instructions.length; instrI++) {
        const instr = instructions[instrI];

        if (instr.hasDrums) {
            instr.drums.forEach(drumId => {
                const x = spacing.instructionXs[instrI];
                const y = spacing.drumYs[drumId];
                
                drawSymbol(svg, drumId, x, y);
            });
        }
    }

}
