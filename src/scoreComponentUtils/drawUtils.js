// This file contains methods related to drawing (and calculating sizes) of specific structures in a score section.
// The methods in this file understand that they are acting on different types of SVG nodes, however this should call on the svgUtils to create and manipulate the actual nodes.

import {attachDefinition, hasDefinition, createPath, createGroup, createCircle, createUse, translate} from "./svgUtils.js";
import {Symbols, SvgInstruction} from "../symbols.js";

function drawAndGetSizeRest(ticks, dots) {
    // Draws a rest with the given number of ticks and dots.
    // If ticks is zero then a crotchet rest is drawn.
    // Returns {svg, size: {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float}}.
    // This is combined into a single method to reduce duplicated code.
    
    return {svg: null, size: {sizeLeft: 5, sizeUp: 5, sizeRight: 0, sizeDown: 5}};  // TODO: Get actual data
}
export function drawRest(ticks, dots) {
    // See drawAndGetSizeRest
    // Returns the svg.
    return drawAndGetSizeRest(ticks, dots).svg;
}
export function getRestSize(ticks, dots) {
    // See drawAndGetSizeRest
    // Returns {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float}.
    return drawAndGetSizeRest(ticks, dots).size;
}


export function drawDots(dots) {
    // TODO: This
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

export function getContractSize(ratio, hooks) {
    // Calculates the minimum width, and the sizeUp and sizeDown, of a contract.
    // returns {minWidth: float, sizeUp: float, sizeDown: float}.

    // TODO: This properly
    return {minWidth: 5, sizeUp: 2.5, sizeDown: 2.5};
}

export function getFlagSize(flags, dots) {
    // Calculates the size of the flags and dots when drawn after a stem.
    // This returns {width: float, height: float}
    
    const flagWidth = (flags != 0) ? 5 : 0; 
    const dotWidth = getDotsSize(dots).width;

    const maxWidth = Math.max(flagWidth, dotWidth);
    
    return {width: maxWidth, height: 10};  // TODO: Add proper height calculation
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
    console.log(svgInstructions);
    
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
