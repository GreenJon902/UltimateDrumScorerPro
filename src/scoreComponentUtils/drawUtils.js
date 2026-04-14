// This file contains methods related to drawing (and calculating sizes) of specific structures in a score section.
// The methods in this file understand that they are acting on different types of SVG nodes, however this should call on the svgUtils to create and manipulate the actual nodes.
// 
// Just some notes on conventions:
//     - Padding should be added by the spacing-engine (decode.js). So getSize functions should return the smallest possible box that will contain the svg nodes (apart from where it makes sense to, e.g. beams take into account the stroke-width of stems). 
//           - However sizes should take into account stroke-width, and therefore bounding boxes should contain every pixel drawn to by the drawFunction.
//     - Anchor is just a name to refer to the coordinate around which each thing will be drawn, and around which sizes and measured from.

import {attachDefinition, hasDefinition, createPath, createCenteredText, createGroup, createCircle, createUse, translate} from "./svgUtils.js";
import {Symbols, SvgInstruction, splitSymbolId} from "../symbols.js";
import {calculateRenderedTextSize} from "./textUtils.js";

const SW = 1;  // Stroke width is 1mm
const SR = SW / 2;  // Stroke radius / distance of edge of line from centre of line

export function drawRest(svg, container, ticks, dots, anchorX, anchorY) {  
    // Draws a rest with the given number of ticks and dots to the container.
    // If ticks is zero then a crotchet rest is drawn.
    // The given anchorX is the right hand side of the rest (this does not include dots, or take stroke width into account). The given anchorY is the Y coordinate to centre the rest on.
    
    if (ticks === 0) {
        // This is a crotchet rest
        createPath(svg, container, `M${anchorX - 5} ${anchorY - 5} l5 5 l-4 2 l4 3`);
        drawDots(svg, container, dots, anchorX + 1, anchorY + 3);
    } else {
        // This is not a crotchet rest

        // Draw rest
        const pathParts = new Array();
        // Rest base:
        pathParts.push(`M${anchorX} ${anchorY - 2 * ticks / 2 - 1.5} l${-2 * ticks - 3} ${2 * ticks + 3}`);
        // Rest ticks:
        pathParts.push(`M${anchorX - 2} ${anchorY - 2 * ticks / 2 + 2 - 1.5}`);
        for (let n=0; n<ticks; n++) {
            pathParts.push("l-2 -2 m0 4");
        }
        // Create path
        const path = pathParts.join(" ");
        createPath(svg, container, path);
        
        // Draw dots
        drawDots(svg, container, dots, anchorX - 2 * ticks + 2, anchorY + 2 * ticks / 2);
    }
}
export function getRestSize(ticks, dots) {
    // Gets the size of a rest with the given number of ticks and dots.
    // If ticks is zero then a crotchet rest is used.
    // 
    // Returns {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float} which are the distances this extends from the anchor-position (see corresponding draw function).
    // The side-sizes take into account the stroke width (i.e. Every pixel drawn in this rest will be within this bounding box).
    
    const dotSize = getDotsSize(dots);

    if (ticks === 0) {
        // This is a crotchet rest
        return {
            sizeLeft: 5 + SR,
            sizeRight: Math.max(SR, 1 + dotSize.sizeRight),  // We want the rightmost of the right-of-rest or right-of-dots
            sizeUp: 5 + SR,
            sizeDown: 5 + SR  // The dots' height should be contained within the height of the rest
        };   
    } else {
        // This is not a crotchet rest
        return {
            sizeLeft: 2  * ticks + 3 + SR, 
            sizeRight: Math.max(SR, -2 * ticks + 2 + dotSize.sizeRight), // Max of right-of-rest or right-of-dots
            sizeUp: 2 * ticks / 2 + 1.5 + SR, 
            sizeDown: 2 * ticks / 2 + 1.5 + SR
        };
    }
}



export function drawDots(svg, container, dots, anchorX, anchorY) {
    // Draws the given number of dots to the container.
    // The anchorX and anchorY are the centre of the first/left-most dot.
    // 
    // Specifically: We draw dots of radius 1mm, between which we have a spacing of 1mm. However you can use getDotsSize to get a rectangular bounding box.

    for (let n=0; n<dots; n++) {
        createCircle(svg, container, 1, anchorX + 3*n, anchorY);  // 3 * n as 1mm for right radius of left dot, 1mm spacing, 1mm for right's radius
    }
}
export function getDotsSize(dots) {
    // Gets the size of the given number of dots when rendered together.
    // 
    // Returns {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float} which are the distances this extends from the anchor-position (see corresponding draw function).
    // Every pixel drawn will be within this bounding box.
    // You can assume that sizeLeft, sizeUp, and sizeDown will be 1 whenever there are dots, and 0 when there dots == 0.
    
    if (dots === 0) return {sizeLeft: 0, sizeRight: 0, sizeUp: 0, sizeDown: 0};  // No dots so return no size
    
    return {
        sizeLeft: 1,
        sizeRight: 3*(dots-1) + 1,  // For n dots we draw (n-1) times: 1mm right of dot, 1mm spacing, 1mm left of next dot. Then add one more for the right of the last dot
        sizeUp: 1,
        sizeDown: 1
    }; 
}


export function drawBeams(svg, container, fullBeams, brokenBeams, dots, anchor1X, anchor1Y, anchor2X, anchor2Y) {
    // Draws the given beams and dots to the container. The top beam will go from (anchor1X, anchor1Y) to (anchor2X, anchor2Y) and subsequent beams will be placed below this. These anchors are where it attaches to the stem, and should be the actual stem coordinate (aka not adjusted for stem stroke width).
    // Anchor1X should be left-of/smaller-than anchor2X.
    // BrokenBeams is the same as specified in RenderInstruction.

    const beamCount = fullBeams + Math.abs(brokenBeams);  // Total number of beams and broken-beams

    const pathParts = new Array();

    // Create path for full beams
    for (let n=0; n<fullBeams; n++) {
        pathParts.push(`M${anchor1X} ${anchor1Y + 2*n} L${anchor2X} ${anchor2Y + 2*n}`);
    }
    // Create path for broken beams
    for (let n=fullBeams; n<beamCount; n++) {
        const x1 = (brokenBeams < 0) ? anchor1X : anchor2X - 5;
        const x2 = (brokenBeams < 0) ? anchor1X + 5 : anchor2X;
        pathParts.push(`M${x1} ${anchor1Y + 2*n} L${x2} ${anchor2Y + 2*n}`);
    }
    
    // Create actual node
    const path = pathParts.join(" ");
    createPath(svg, container, path);
    
    // Draw dots
    const dotsSize = getDotsSize(dots);
    const dotsAnchorX = (anchor1X + SR) + 1 + dotsSize.sizeLeft;  // (right-of-stem) + 1mm padding + sizeLeft
    if (brokenBeams < 0 || dotsAnchorX + dotsSize.sizeRight + 1 > anchor2X - 5 - SR) {  // If brokenBeams on left or dots won't fit under right brokenBeams
        drawDots(svg, container, dots, dotsAnchorX, anchor1Y + (SR + 1 + SR)*(beamCount-1) + SR + 2);  // We want the top of the dots to be one below the bottom of the beam. The stroke width of the beam is 1mm, so its edge is 0.5mm from the y level of the beam
    } else {
        drawDots(svg, container, dots, dotsAnchorX, anchor1Y + 2 * fullBeams + 1);
    }
}
export function getBeamSize(fullBeams, brokenBeams, dots) {
    // Calculates the height and minimum width required to draw the specified beams and dots after stem.
    // BrokenBeams is the same as specified in RenderInstruction.
    // 
    // Note this will always return accounting for stroke-width, even if there are no beams (so it cannot return sizeUp 0).
    // 
    // Returns {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float, minAnchorWidth: float}:
    //     sizeLeft is measured from the anchor1/the-left-anchor, and sizeRight from anchor2/the-right-anchor.
    //     sizeUp is measured from the highest anchor (as they may be slanted).
    //     sizeDown is measured from the lowest anchor (as they may be slanted) (this may be slightly larger than necessary in the case that broken beams are on the side of the higher anchor).
    //     minAnchorWidth is the minimum distance between the anchors (so the distance between stem's-x-coordinate (this function already accounts for the stems stroke width)).
    // Every pixel drawn will be within this bounding box.
    // You can assume sizeLeft, sizeUp and sizeRight will always be STROKE_WIDTH/2==1mm.
    
    const brokenBeamWidth = (brokenBeams != 0) ? 5 + SR + 1 : 0;  // (5+SR) for beam + 1 padding
    const dotsSize = getDotsSize(dots);

    // TODO: Figure out if dots are below or on same level as broken-beams (we'll need to know final width?)
    // For now assume they are underneath broken beams
    const minAnchorWidth = Math.max(
        SR + 1,  // If no dots and no broken-beams, then say 1mm between inside edges of stems
        brokenBeamWidth,  
        SR + 1 + dotsSize.sizeLeft + dotsSize.sizeRight  // Account for stroke-width of the stem on the left, + 1mm padding between stem and dots, then add width of dots
    );  
    const sizeDown = 2*(fullBeams+Math.abs(brokenBeams)-1) + SR + ((dots !== 0) ? 1 : 0) + dotsSize.sizeUp + dotsSize.sizeDown;  // We have 2 between the coordinates the beams are drawn at, then SR of bottom beam, then 1mm padding (if there are dots), then height of dots (when applicable, will be zero otherwise)
    
    return {
        sizeLeft: SR,
        sizeRight: SR, 
        sizeUp: SR,
        sizeDown: sizeDown,
        minAnchorWidth: minAnchorWidth
    };
}

export function drawContract(svg, container, ratio, hooks, startX, endX, centerY) {
    // Draws the given contract to the container.
    
    const size = calculateRenderedTextSize(createCenteredText, ratio);
    const textWidth = size.sizeLeft + size.sizeRight;
    const textHeight = size.sizeDown + size.sizeUp;
    
    const centerX = (startX + endX) / 2;
    const height = Math.max(textHeight, 2);  // Hook height is 2
    
    // Create hooks
    if (hooks) {
        createPath(svg, container, `M${startX} ${centerY + 2} l0 -2 L${centerX - textWidth / 2 - 1} ${centerY} M${centerX + textWidth / 2 + 1} ${centerY} L${endX} ${centerY} l0 2`);  // Add and subtract one to the inner x-coordinates as padding
    }
    
    // Create text
    createCenteredText(svg, container, ratio, centerX, centerY);
}
export function getContractSize(ratio, hooks) {
    // Calculates the minimum width, and the sizeUp and sizeDown, of a contract.
    // returns {minWidth: float, sizeUp: float, sizeDown: float}.

    const size = calculateRenderedTextSize(createCenteredText, ratio);
    return {minWidth: 5 + size.sizeLeft + size.sizeRight, 
            sizeUp: size.sizeUp, 
            sizeDown: Math.max(2.5, size.sizeDown)
    };
}

export function drawFlags(svg, container, flags, dots, anchorX, anchorY) {
    // Draws the given number of flags and dots to the container. The number of flags can be zero, in which case this is just a stem.
    // The first flag will be drawn descending to the right from (anchorX, anchorY) and subsequent flags will be drawn below.
    // This anchor position should be the stem-coordinate (so should not take into account stem stroke-width).

    // Draw flags
    if (flags !== 0) {  // If there are no flags, then this will just create an empty path
        const pathParts = new Array();
        for (let n=0; n<flags; n++) {
            pathParts.push(`M${anchorX} ${anchorY + 2 * n} l5 2`);
        }
        const path = pathParts.join(" ");
        createPath(svg, container, path);
    }
    
    // Draw dots
    const dotsSize = getDotsSize(dots);
    const dotsAnchorX = (anchorX + SR) + 1 + dotsSize.sizeLeft;  // (right-of-stem) + 1mm padding + sizeLeft
    const dotsAnchorY = anchorY + 2 * flags + SR + 0.5 + dotsSize.sizeUp;  // Bottom of flags + 1mm padding + radius of dots. We keep this padding even if there are no flags cause I think it makes sense
    drawDots(svg, container, dots, dotsAnchorX, dotsAnchorY);
}
export function getFlagSize(flags, dots) {
    // Calculates the size of the flags and dots when drawn after a stem.
    // 
    // Returns {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float} which are the distances this extends from the anchor-position (see corresponding draw function).
    // Every pixel drawn will be within this bounding box.
    
    const flagRight = (flags !== 0) ? 5 + SR : 0; 
    const dotsSize = getDotsSize(dots);
    const dotsRight = (dots !== 0) ? SR + 1 + (dotsSize.sizeLeft + dotsSize.sizeRight) : 0;  // SR of stem + 1mm padding + width of dots

    const maxRight = Math.max(flagRight, dotsRight);
    
    const flagSR = (flags !== 0) ? SR : 0;  // We only need to account for stroke-width for flags if there are actually flags

    return {
        sizeLeft: flagSR,
        sizeRight: maxRight,
        sizeUp: flagSR,
        sizeDown: 2 * flags + flagSR + ((dots !== 0) ? (0.5 + dotsSize.sizeUp + dotsSize.sizeDown) : 0)
    };
}


export function drawDrumAt(svg, container, drumId, x, y) {
    // Draws the drum with the given id to the given node (container) at the given coordinates..
    // Any required definitions will be added to the given svg. It is expected that container is a (indirect) child of svg.
    
    const baseId = splitSymbolId(drumId).base;
     
    drawSymbolAt(svg, container, drumId, x, y, {
        size_left: Symbols.getDrumSizeLeft(drumId),  // Underscores is what the substitution names use
        size_up: Symbols.getDrumSizeUp(drumId),
        size_right: Symbols.getDrumSizeRight(drumId),
        size_down: Symbols.getDrumSizeDown(drumId),
        base_size_left: Symbols.getDrumSizeLeft(baseId),
        base_size_right: Symbols.getDrumSizeRight(baseId),
        base_size_up: Symbols.getDrumSizeUp(baseId),
        base_size_down: Symbols.getDrumSizeDown(baseId)
    });
}
export function getDrumSize(drumId) {
    // Returns the given drums {size_left, size_right, size_up, size_down} after adjusting for stroke width.
    return {
        sizeLeft: Symbols.getDrumSizeLeft(drumId) + SR,
        sizeUp: Symbols.getDrumSizeUp(drumId) + SR,
        sizeRight: Symbols.getDrumSizeRight(drumId) + SR,
        sizeDown: Symbols.getDrumSizeDown(drumId) + SR,
    }
}

export function drawDecorationAt(svg, container, decorationId, x, y, computedHeight, drumCenterY) {
    // Draws the decoration with the given id to the given node (container) at the given coordinates..
    // Any required definitions will be added to the given svg. It is expected that container is a (indirect) child of svg.
    // The computedHeight is the height to draw the decoration, this should satisfy all the constraints. This should not have been adjusted for stroke-width.
    drawSymbolAt(svg, container, decorationId, x, y, {
        width: Symbols.getDecorationWidth(decorationId),
        height: computedHeight,
        drum_center_y: drumCenterY
    });
}
export function getDecorationSize(decoId, computedHeight) { 
    // Returns the given decortaions {sizeLeft, sizeRight, sizeUp, sizeDown} after adjusting for stroke-width.
    // If computedHeight is not given then only sizeLeft and sizeRight are returned.
    // The computed height is the height before adjusting for stroke-width. This will be shared equally between sizeUp and sizeDown.
    if (computedHeight === null || computedHeight === undefined) {
        computedHeight = NaN;
    }
    return {
        sizeLeft: Symbols.getDecorationWidth(decoId) + SR,  
        sizeRight: SR,
        sizeUp: computedHeight / 2 + SR, 
        sizeDown: computedHeight / 2 + SR
    };
}

function createRequisiteName(symbolId, substitutions) {
    // Creates the id to use for the svg def for the given symbol pared with the given substitutions.
    // This will only take into account substitutions that are actually used.
    // Only the global variables should be given, the local variables should already be stored in the SvgInstruction.
    
    // Local substs are in the instruction, global are given as a param, so combined
    let allSubstitutions = Object.assign({}, ...Symbols.getSymbolInstructions(symbolId).map(
        instr => instr.addSubstitutions(substitutions).getSubstitutions()
    ));
    
    // Clean substitution values
    allSubstitutions = Object.fromEntries(Object.entries(allSubstitutions).map(
        entr => [entr[0], String(entr[1]).replaceAll(".", "d")] 
    ));

    // Get names of substitutions used by any instruction as a sorted array using each substName only once
    const usedSubstitutionNames = new Array(...new Set(Iterator.concat(
        ...Array.from(Symbols.getSymbolInstructions(symbolId)).map(instr => instr.getUsedSubstitionNames())
    ))).sort();

    return [symbolId, ...usedSubstitutionNames.map(name => `${name}_${allSubstitutions[name]}`)].join("__");
}

const SYMBOL_DEFINITIONS = "symbol_definitions";  // The definitionType when handling definitions relating to symbols
function drawSymbolAt(svg, container, symbolId, x, y, substitutions) {  
    // Draws the symbol with the given id to the given node (container) at the given coordinates.
    // Any required definitions will be added to the given svg. It is expected that container is a (indirect) child of svg.
    // The given substitutions - {string: float} - should contain all (global) variables required for the type of the given symbol. These will be applied to all requisites too.
    
    // Make sure the definition of this symbol has been added
    // We must also ensure we have any definitions for indirect requisites (symbol parts, etc) added too
    const requisites = [symbolId]; 
    while (requisites.length !== 0) {
        const newSymbolId = requisites.pop();
        const defId = createRequisiteName(newSymbolId, substitutions);
        
        if (hasDefinition(svg, SYMBOL_DEFINITIONS, defId)) continue;  // If we have the definition then we don't need to add it (and it's requisites must already be added to, so can be ignored here)
        
        // Attach the definition for id, and add any requisites to the array to be processed
        const {group, requisites: newRequisites} = createSymbolGroup(svg, newSymbolId, substitutions);
        attachDefinition(svg, SYMBOL_DEFINITIONS, defId, group);
        requisites.push(...newRequisites);
    }
    
    // Create and add a node which calls on the definition
    createUse(svg, container, SYMBOL_DEFINITIONS, createRequisiteName(symbolId, substitutions), translate(x, y));
}


function createSymbolGroup(svg, symbolId, substitutions) {
    // Creates a svg group node for the given symbol. Also returns any requisite symbols (parts, etc). Also returns any substitution-names / parameters that this used.
    // Expects the requisites to be added under the type SYMBOL_DEFINITIONS.
    // The given substitutions - {string: float} - should contain all variables required for the type of the given symbol. These will be applied to all requisites too.
    // Returns {group: SvgNode, requisites: Set<symbolId>, substitutions: Set<string>}.

    // Figure out how to draw the given symbol
    const svgInstructions = Symbols.getSymbolInstructions(symbolId);
    
    // Create a group node that will contain the executed svg instructions
    const symbolContainer = createGroup(svg, null);
    
    // Convert the svg instructions to actual nodes and add them to the container
    const parentNode = new Array(symbolContainer);  // Since we can push and pop transformations, we need a stack
    const requisites = new Set();
    for (let i=0; i<svgInstructions.length; i++) {
        const instr = svgInstructions[i].addSubstitutions(substitutions).computeSubstitutions();
        
        const currentParent = parentNode[parentNode.length - 1];  // Add node to the last parentNode (as that was most recently pushed)
        
        // Convert instr into a node
        if (instr.type === SvgInstruction.PATH) {
            createPath(svg, currentParent, instr.path);
        } else if (instr.type === SvgInstruction.CIRCLE) {
            createCircle(svg, currentParent, instr.r, instr.cx, instr.cy);
        } else if (instr.type === SvgInstruction.USE) {
            createUse(svg, currentParent, SYMBOL_DEFINITIONS, createRequisiteName(instr.id, substitutions));
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
export function getStemSize() {
    // Returns the stem's {sizeLeft, sizeRight} after adjusting for stroke-width.
    
    return {sizeLeft: SR, sizeRight: SR};
}

export function getTimeSignatureSize(numerator, denomenator) {
    // Get the rendered size of a time-signature with the given top and bottom numbers.
    // The anchorY is the y-level between the numbers.
    // Returns {size_up, size_down, size_left, size_right};
    
    // For now we just place both on top of eachother
    const numSize = calculateRenderedTextSize(createCenteredText, numerator);
    const denSize = calculateRenderedTextSize(createCenteredText, denomenator);
    return {sizeUp: (numSize.sizeUp + numSize.sizeDown) * 0.6, 
            sizeDown: (denSize.sizeUp + denSize.sizeDown) * 0.6,
            sizeLeft: Math.max(numSize.sizeLeft, denSize.sizeLeft),
            sizeRight: Math.max(numSize.sizeRight, denSize.sizeRight)};
}
export function drawTimeSignature(svg, container, numerator, denomenator, x, y) {
    // Draws the given time-signature to the container (which is a child or is the svg).
    // The anchorY is the y-level between the numbers.
    // The given coordinates are given to createCenteredText.
    
    // For now we just place both on top of eachother
    const numSize = calculateRenderedTextSize(createCenteredText, numerator);
    const denSize = calculateRenderedTextSize(createCenteredText, denomenator);
    createCenteredText(svg, container, numerator, x, y - numSize.sizeDown * 0.6);  // Multiply by some factor to put text closer together
    createCenteredText(svg, container, denomenator, x, y + denSize.sizeUp * 0.6);
}
