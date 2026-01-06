// This file contains methods related to drawing (and calculating sizes) of specific structures in a score section.
// The methods in this file understand that they are acting on different types of SVG nodes, however this should call on the svgUtils to create and manipulate the actual nodes.

import {attachDefinition, hasDefinition, createPath, createCenteredText, createGroup, createCircle, createUse, translate} from "./svgUtils.js";
import {Symbols, SvgInstruction} from "../symbols.js";

export function drawRest(svg, container, ticks, dots, right, centerY) {
    // Draws a rest with the given number of ticks and dots to the container.
    // If ticks is zero then a crotchet rest is drawn.
    
    if (ticks === 0) {
        // This is a crotchet rest
        createPath(svg, container, `M${right - 5} ${centerY - 5} l5 5 l-4 2 l4 3`);
        drawDots(svg, container, dots, right, centerY + 2);
    } else {
        // This is not a crotchet rest

        // Draw rest
        const pathParts = new Array();
        // Rest base:
        pathParts.push(`M${right} ${centerY - 2 * ticks / 2 - 1.5} l${-2 * ticks - 3} ${2 * ticks + 3}`);
        // Rest ticks:
        pathParts.push(`M${right - 2} ${centerY - 2 * ticks / 2 + 2 - 1.5}`);
        for (let n=0; n<ticks; n++) {
            pathParts.push("l-2 -2 m0 4");
        }
        // Create path
        const path = pathParts.join(" ");
        createPath(svg, container, path);
        
        // Draw dots
        drawDots(svg, container, dots, right - 2 * ticks, centerY + 2 * ticks / 2 - 2);
    }
}
export function getRestSize(ticks, dots) {
    // Gets the size of a rest with the given number of ticks and dots.
    // If ticks is zero then a crotchet rest is used.
    // Returns {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float}.
    if (ticks === 0) {
        // This is a crotchet rest
        return {sizeLeft: 5, sizeUp: 5, sizeRight: 0, sizeDown: 5};
    } else {
        // This is a crotchet rest
        return {sizeLeft: 2  * ticks + 3, sizeUp: 2 * ticks / 2 + 1.5, sizeRight: 0, sizeDown: 2 * ticks / 2 + 1.5};
    }
}



export function drawDots(svg, container, dots, x, y) {
    // Draws the given number of dots to the container.
    // StartX and startY is the top-left corner of the bounding box containing the dots as returned by getDotsSize.

    for (let n=0; n<dots; n++) {
        createCircle(svg, container, 1, x + 2 + 4*n, y + 2);
    }
}
export function getDotsSize(dots) {
    // Gets the size of the given number of dots when rendered together.
    // Returns {width: float, height: float}.
    return {width: dots * 4, height: 4};
}

export function calculateBeamSize(fullBeams, brokenBeams, dots) {
    // Calculates the height and minimum width required to draw the specified beams and dots after stem.
    // BrokenBeams is the same as specified in RenderInstruction.
    // minWidth is the minimum stem to stem spacing.
    // returns {minWidth: float, height: float}
    
    const brokenBeamWidth = (brokenBeams != 0) ? 7 : 0;  // 7 = 5 for beam + 2 padding
    const dotSize = getDotsSize(dots);

    let minWidth;
    let height;
    if (brokenBeams < 0) {
        // Dots below broken beams
        minWidth = Math.max(brokenBeamWidth, dotSize.width)
        height = (fullBeams + brokenBeams) * 2 + dotSize.height;
    } else {
        // Dots on same level as broken beams
        minWidth = brokenBeamWidth + dotSize.width;
        height = fullBeams * 2 + Math.max(brokenBeams * 2, dotSize.height);
    }
    
    return {minWidth, height};
}

export function drawBeams(svg, container, fullBeams, brokenBeams, dots, startX, startY, endX, endY) {
    // Draws the given beams and dots to the container. The top beam will go from (startX, startY) to (endX, endY) and subsequent beams will be placed below this.
    // BrokenBeams is the same as specified in RenderInstruction.

    const pathParts = new Array();

    // Create path for full beams
    for (let n=0; n<fullBeams; n++) {
        pathParts.push(`M${startX} ${startY + 2*n} L${endX} ${endY + 2*n}`);
    }
    // Create path for broken beams
    for (let n=fullBeams; n<fullBeams + brokenBeams; n++) {
        const x1 = (brokenBeams < 0) ? startX : endX - 5;
        const x2 = (brokenBeams < 0) ? 5 : endX;
        pathParts.push(`M${x1} ${startY + 2*n} L${x2} ${endY + 2*n}`);
    }
    
    // Create actual node
    const path = pathParts.join(" ");
    createPath(svg, container, path);
    
    // Draw dots
    if (brokenBeams < 0) {
        drawDots(svg, container, dots, startX, startY + 2 * (fullBeams + brokenBeams));
    } else {
        drawDots(svg, container, dots, startX, startY + 2 * fullBeams);
    }
}

export function getContractSize(ratio, hooks) {
    // Calculates the minimum width, and the sizeUp and sizeDown, of a contract.
    // returns {minWidth: float, sizeUp: float, sizeDown: float}.

    // TODO: This properly
    return {minWidth: 5, sizeUp: 2.5, sizeDown: 2.5};
}
export function drawContract(svg, container, ratio, hooks, startX, endX, centerY) {
    // Draws the given contract to the container.
    
    const textWidth = 5;  // TODO: This properly
    const textHeight = 5;  // TODO: This properly
    
    const centerX = (startX + endX) / 2;
    const height = Math.max(textHeight, 2 * 2);  // Hook height * 2 = 2 * 2
    
    // Create hooks
    if (hooks) {
        createPath(svg, container, `M${startX} ${centerY + 2} l0 -2 L${centerX - textWidth / 2} ${centerY} M${centerX + textWidth / 2} ${centerY} L${endX} ${centerY} l0 2`);
    }
    
    // Create text
    createCenteredText(svg, container, ratio, centerX, centerY);
}

export function getFlagSize(flags, dots) {
    // Calculates the size of the flags and dots when drawn after a stem.
    // This returns {width: float, height: float}
    
    const flagWidth = (flags != 0) ? 5 : 0; 
    const dotWidth = getDotsSize(dots).width;

    const maxWidth = Math.max(flagWidth, dotWidth);
    
    return {width: maxWidth, height: 10};  // TODO: Add proper height calculation
}

export function drawFlags(svg, container, flags, dots, flagStartX, flagStartY) {
    // Draws the given number of flags and dots to the container.
    // The first flag will be drawn at (flagStartX, flagStartY) and subsequent flags will be drawn below.

    // Draw flags
    const pathParts = new Array();
    for (let n=0; n<flags; n++) {
        pathParts.push(`M${flagStartX} ${flagStartY + 2 * n} l5 2`);
    }
    const path = pathParts.join(" ");
    createPath(svg, container, path);
    
    // Draw dots
    drawDots(svg, container, dots, flagStartX, flagStartY + 2 * flags)
}


const SYMBOL_DEFINITIONS = "symbol_definitions";  // The definitionType when handling definitions relating to symbols
export function drawSymbolAt(svg, container, symbolId, x, y) {
    // Draws the symbol with the given id to the given node (container) at the given coordinates.
    // Any required definitions will be added to the given svg. It is expected that cont is a (indirect) child of svg.
    
    // Make sure the definition of this symbol has been added
    // We must also ensure we have any definitions for indirect requisites (symbol parts, etc) added too
    const requisites = [symbolId]; 
    while (requisites.length !== 0) {
        const id = requisites.pop();
        
        if (hasDefinition(svg, SYMBOL_DEFINITIONS, id)) continue;  // If we have the definition then we have its requisites too
        
        // Attach the definition for id, and add any requisites to the array to be processed
        const {group, requisites: newRequisites} = createSymbolGroup(svg, id);
        attachDefinition(svg, SYMBOL_DEFINITIONS, id, group);
        requisites.push(...newRequisites);
    }
    
    // Create and add a node which calls on the definition
    createUse(svg, container, SYMBOL_DEFINITIONS, symbolId, translate(x, y));
}


function createSymbolGroup(svg, symbolId) {
    // Creates a svg group node for the given symbol. Also returns any requisite symbols (parts, etc).
    // Expects the requisites to be added under the type SYMBOL_DEFINITIONS.
    // Returns {group: SvgNode, requisites: Set<symbolId>}.

    // Figure out how to draw the given symbol
    const svgInstructions = Symbols.getSymbolInstructions(symbolId);
    
    // Create a group node that will contain the executed svg instructions
    const symbolContainer = createGroup(svg, null);
    
    // Convert the svg instructions to actual nodes and add them to the container
    const parentNode = new Array(symbolContainer);  // Since we can push and pop transformations, we need a stack
    const requisites = new Set();
    for (let i=0; i<svgInstructions.length; i++) {
        const instr = svgInstructions[i].computeSubstitutions();
        
        const currentParent = parentNode[parentNode.length - 1];  // Add node to the last parentNode (as that was most recently pushed)
        
        // Convert instr into a node
        if (instr.type === SvgInstruction.PATH) {
            createPath(svg, currentParent, instr.path);
        } else if (instr.type === SvgInstruction.CIRCLE) {
            createCircle(svg, currentParent, instr.r, instr.cx, instr.cy);
        } else if (instr.type === SvgInstruction.USE) {
            createUse(svg, currentParent, SYMBOL_DEFINITIONS, instr.id);
            requisites.add(instr.id);
            
        // These two are special
        } else if (instr.type === SvgInstruction.PUSH_TRANSFORM) {
            const newGroup = createGroup(svg, currentParent, instr.transform);
            parentNode.push(newGroup);  // We want the following instructions to be inside this group so the transformation applies to them
        } else if (instr.type === SvgInstruction.POP_TRANSFORM) {
            if (parentNode.length <= 1) throw "SvgInstruction tried to pop when nothing in stack";  // <= 1 as the 0th item is the symbolContainer
            parentNode.pop();  // We no longer need the last transformation (which was stored by the last group)
            
        } else {
            throw "Unknown type " + type;
        }
    }
    
    if (parentNode.length > 1) throw "SvgInstructions did not clean stack";  // There were more push instructions than pop instructions
    
    // Return
    return {group: symbolContainer, requisites: Object.freeze(requisites)};
}

export function drawStem(svg, container, x, topY, bottomY) {
    // Draws a stem into the container with endpoints (x, topY) and (x, bottomY).
    createPath(svg, container, `M${x} ${topY} L${x} ${bottomY}`);
}
