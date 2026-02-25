// This is a very basic implementation of spacing.
// Group instructions will not overlap in the x direction, even when it is possible to do so (kick on next subdiv could go under snare (in certain situations)).
// Beams, flags and dots are drawn over the highest drum. So if we need 10 half_beams over a kick, these will not descend into the drum y-space, but will instead push the rhythm notation parts up.
// Similarily, contracts will be drawn over the highest beam/flag/dot.
//
//
//

import {RenderInstruction} from "./compile.js";
import {getRestSize, getFlagSize, getDotsSize, getBeamSize, getContractSize, getDrumSize, getDecorationSize} from "./drawUtils.js";
import {Symbols} from "../symbols.js";

function getHeight(sizeInfo) {
    // sizeInfo: {sizeLeft: float, sizeUp: float, sizeDown: float, sizeRight: float}
    // returns: float
    //
    // Returns sizeUp + sizeDown.
    return sizeInfo.sizeUp + sizeInfo.sizeDown;
}

function getWidth(sizeInfo) {
    // sizeInfo: {sizeLeft: float, sizeUp: float, sizeDown: float, sizeRight: float}
    // returns: float
    //
    // Returns sizeUp + sizeDown.
    return sizeInfo.sizeLeft + sizeInfo.sizeRight;
}

function getRelativeDrumYs(vertGroupLinkedComponentInstructions) {
    // vertGroupLinkedComponentInstructions: Set<Array<RenderInstruction>>
    // 
    // Returns a map {str: float} from drumId to distance between that drum's anchorY and the anchorY of the highest drum.
    
    
    // Get all drum IDs that are used ---
    const allDrumIds = new Array().concat(
        ...new Array().concat(...vertGroupLinkedComponentInstructions)
            .filter(instr => [RenderInstruction.BEAM, RenderInstruction.BEAM_END, RenderInstruction.FLAG].includes(instr.type))
            .map(instr => Array.from(instr.drums))
    );
    // Get an array of the order of the drum ids that are used, ordered in where they are drawn top to bottom
    const orderedDrumIds = Symbols.getFullDrumVertOrder()
        .filter(id => allDrumIds.includes(id));
    

    // If no drum IDs are used then we can return an empty map
    if (orderedDrumIds.length === 0) return {};
    

    // Create a map of drums which are used in the same subdivision ---
    // Create empty sets for each id
    const drumCollisions = {};
    orderedDrumIds.forEach(id => {drumCollisions[id] = new Set()});
    // Populate arrays with other ids
    new Array().concat(...vertGroupLinkedComponentInstructions)
        .filter(instr => [RenderInstruction.BEAM, RenderInstruction.BEAM_END, RenderInstruction.FLAG].includes(instr.type))
        .map(instr => Array.from(instr.drums))
        .forEach(drums => 
            drums.forEach(a => drums.forEach(b => {  // Add each drum in drums to each drum in drums' set
                drumCollisions[a].add(b);
            }))
        );
    
    
    // Make a map of directRelativeDrumYs ---
    
    // We will have to apply Symbol-constraints in a specific order to avoid this situation:
    //     1: a is 10 above c, 2: a is 5 above b, 3: b is 5 above c.
    //     If we start with {a: 0, b: 0, c: 0}, and then apply 1 we get {a: 0, b: 0, c: 10}. Then after 2 and 3 we have {a: 0, b: 5, c: 10}. But if we choose a better order to apply the constraints in, we can get {a: 0, b: 5, c: 5}.

    const directRelativeDrumYs = [{id: orderedDrumIds[0], dist: getDrumSize(orderedDrumIds[0]).sizeUp}];  // [{id: drumId, dist: float}] where the distance is to the anchor above it. The order of items in this array should be in the order that symbols are drawn top to bottom  // The top of the first item should always be 0
    for (let i=1; i<orderedDrumIds.length; i++) {  // i is the index of the drum we are adding.  // Start with i=0 as we've already added item 0.
        const iid = orderedDrumIds[i];
        
        let distRequirement = 0;  // The distance from iid to the drum immediately above iid

        for (let j=0; j<directRelativeDrumYs.length; j++) {  // j is the index of the drum we are comparing to
            const jid = directRelativeDrumYs[j].id;
            
            const currentDist = [  // Distance of j's anchor from 0
                                    ...directRelativeDrumYs.slice(0, jid + 1).map(drdy => drdy.dist),
                                    0  // Add zero at the end so reduce works if slice returns no values
                                ].reduce((a, b) => (a + b));
            
            // Check Symbol-constraints between iid and jid
            const constraintMinDist = Symbols.getMinVertDistBetweenDrums(jid, iid);  // We know already that jid is "above" iid, so this will not crash
            if (constraintMinDist > currentDist) {
                distRequirement = constraintMinDist;
            }
            
            // Check if iid collides with jid
            if (drumCollisions[iid].has(jid)) {
                
                const iDrumSize = getDrumSize(iid);
                const jDrumSize = getDrumSize(jid);
                
                if (jDrumSize.sizeDown >= (currentDist - iDrumSize.sizeUp)) {
                    distRequirement = jDrumSize.sizeDown + iDrumSize.sizeUp;
                }
            }
        }
        
        

        // Add iid and distRequirement to directRelativeDrumYs
        directRelativeDrumYs.push({id: iid, dist: distRequirement});
    }
    
    // Make relative distances relative to highest drum
    const relativeDrumYs = {};
    for (let i=0; i<directRelativeDrumYs.length; i++) {
        let fullDist = 0;
        for (let j=0; j<=i; j++) {
            fullDist += directRelativeDrumYs[j].dist;
        }
        relativeDrumYs[directRelativeDrumYs[i].id] = fullDist;
    }
    
    return relativeDrumYs;
}

function getMaxHorizSizeOfDrums(drums) {
    // drums: Array<drum-id>
    //
    // Returns the maxiumum sizeLeft and sizeRight that the given drums have.
    // Returns {sizeLeft: float, sizeRight: float}.
    return {
        sizeLeft: Math.max(...Array.from(drums).map(id => getDrumSize(id).sizeLeft)),
        sizeRight: Math.max(...Array.from(drums).map(id => getDrumSize(id).sizeRight))
    };
}

function getInstructionXs(instructions) {
    // instructions: Array<RenderInstruction>
    // 
    // Calculates the x-coordinate data for each instruction.
    // For BEAMs, BEAM_ENDs and FLAGs: this is the anchor-x.
    // For RESTs and DECORATIONs: this is the right edge (of the rest, not the dots attached to the rest).
    // For CONTRACT_STARTs and CONTRACT_ENDs: this is the hook location (or where it would be, in the cases that it isn't drawn).
    // 
    // The index of the returned array corresponds to the index of the instruction.

    const instructionXs = new Array();
    let xTrackers = null;

    for (let i=0; i<instructions.length; i++) {
        const instr = instructions[i];
        
        // Get new X coordinate
        let instructionX;
        ({instructionX, trackers: xTrackers} = calculateInstructionX(instr, xTrackers));

        instructionXs.push(instructionX);
    }
    
    return instructionXs;
}

function calculateInstructionX(instr, trackers) {
    // instr: RenderInstruction
    // trackers: the return value from the last call of this function, or null if this is the first call
    //
    // Calculates the instructionX (see calculateScoreComponentSpacing return value) for this instruction.
    // This depends data that was calculated by previous calls of this function, which is saved in this "trackers" object. This first call of this function should have trackers as null, for all future calls it *must* be the value returned for the last instruction.
    //
    // return {instructionX: float, trackers}.
    
    // Handle trackers unpacking
    if (trackers === null) trackers = {x: 0, ryhthmRight: 0, drumSpaceRight: 0};  // Default value
    const {x: lastX, ryhthmRight: lastRyhthmRight, drumSpaceRight: lastDrumSpaceRight} = trackers;
    

    // Calculate the new x and tracker values
    let newX, newDrumSpaceRight, newRyhthmRight;
    if (instr.isContract) {
        newX = Math.max(lastX, lastRyhthmRight, lastDrumSpaceRight);
        newDrumSpaceRight = lastDrumSpaceRight;
        newRyhthmRight = lastRyhthmRight;
        // TODO: Process minimum width of a contract
        

    } else if (instr.hasDrums) {
        const drumsSize = getMaxHorizSizeOfDrums(instr.drums);
        
        // Select the (minimum) width of the rhythm part after the stem
        const ryhthmWidthPart = {
            [RenderInstruction.BEAM]: () => getBeamSize(instr.fullBeams, instr.brokenBeams, instr.dots).minAnchorWidth,
            [RenderInstruction.BEAM_END]: () => getWidth(getDotsSize(instr.dots)),
            [RenderInstruction.FLAG]: () => getWidth(getFlagSize(instr.flags, instr.dots))
        }[instr.type]();  // Do as lambda functions so we only call the one we want
        
        newX = Math.max(lastRyhthmRight, lastDrumSpaceRight + drumsSize.sizeLeft);
        newDrumSpaceRight = newX + drumsSize.sizeRight;
        newRyhthmRight = newX + ryhthmWidthPart; 
        

    } else if (instr.type === RenderInstruction.DECORATION) {
        const decorationSize = getDecorationSize(instr.decoration);
        
        newX = Math.max(lastRyhthmRight, lastDrumSpaceRight + decorationSize.sizeLeft);
        newDrumSpaceRight = newX + decorationSize.sizeRight;
        newRyhthmRight = lastRyhthmRight;  // Decorations don't impact rhthm stuff (though technically there should be no beams over decorations anyway)

        
    } else if (instr.type === RenderInstruction.REST) {
        const restSize = getRestSize(instr.ticks, instr.dots);
        
        newX = lastDrumSpaceRight + restSize.sizeLeft;
        newDrumSpaceRight = newX + restSize.sizeRight;  // Rests are drawn in drum-space
        newRyhthmRight = lastRyhthmRight;  // Rests are below bars so don't impact them
        // TODO: Using lastRyhthmRight, center the rest underneath the bars

        
    } else {
        throw "Unknown instruction type " + instr.type;
    }
    
    // Return new data
    const newTrackers = {x: newX, ryhthmRight: newRyhthmRight, drumSpaceRight: newDrumSpaceRight};
    return {instructionX: newX, trackers: newTrackers};
}

function calculateRestContractStemDeorationDrumYs(instructions, vertGroupLinkedComponentInstructions) {
    // instructions: Array<RenderInstruction>
    // vertGroupLinkedComponentInstructions: Set<Array<RenderInstruction>>
    // 
    // Calculates the drumYs, restCenterYs, contractCenterYs, decorationCenterYs, decorationHeights, drumCenterY and stemTopYs that are returned by calculateScoreComponentSpacing.
    // While this does not return heights for decorations, it does take their heights into account.
    
    // Calculate prerequisite data ---
    
    const relativeDrumYs = getRelativeDrumYs(vertGroupLinkedComponentInstructions);  // Relative to anchor of top drum
    const maxBeamFlagDotHeight = Math.max(
        // If there are no BEAM, FLAGs, or BEAM_ENDs then take 0
        ...instructions
            .filter(instr => instr.type === RenderInstruction.BEAM)
            .map(instr => getHeight(getBeamSize(instr.fullBeams, instr.brokenBeams, instr.dots))),
        ...instructions
            .filter(instr => instr.type === RenderInstruction.BEAM_END)
            .map(instr => getHeight(getBeamSize(0, 0, instr.dots))),
        ...instructions
            .filter(instr => instr.type === RenderInstruction.FLAG)
            .map(instr => getHeight(getFlagSize(instr.flags, instr.dots)))
    );
    const maxDecorationHeight = Math.max(
        0,  // If there are no decorations then take 0
        ...instructions
            .filter(instr => instr.type === RenderInstruction.DECORATION)
            .map(instr => getDecorationSize(instr.decoration).minHeight)
    );
    const maxDecorationMinAboveBars = Math.max(
        0,  // If there are no decorations then take 0
        ...instructions
            .filter(instr => instr.type === RenderInstruction.DECORATION)
            .map(instr => Symbols.getDecorationMinAboveBars(instr.decoration))
    );
    const maxDecorationMinAboveDrums = Math.max(
        0,  // If there are no decorations then take 0
        ...instructions
            .filter(instr => instr.type === RenderInstruction.DECORATION)
            .map(instr => Symbols.getDecorationMinAboveDrums(instr.decoration))
    );
    const maxDecorationMinBelowDrums = Math.max(
        0,  // If there are no decorations then take 0
        ...instructions
            .filter(instr => instr.type === RenderInstruction.DECORATION)
            .map(instr => Symbols.getDecorationMinBelowDrums(instr.decoration))
    );
    const maxContractHeight = Math.max(
        0,  // If there are no contracts then take 0
        ...instructions
            .filter(instr => instr.type === RenderInstruction.CONTRACT_START)  // Only contract starts store data about the ratio and hooks
            .map(instr => getHeight(getContractSize(instr.ratio, instr.hooks)))
    );
    const maxRestHeight = Math.max(
        0,  // If there are no rests then take 0
        ...instructions
            .filter(instr => instr.type === RenderInstruction.REST)
            .map(instr => getHeight(getRestSize(instr.ticks, instr.dots)))
    );


    // Compute contractCenterYs ---
    // For now just put them all touching (but not going over) the top edge
    const contractCenterYs = instructions
            .filter(instr => instr.type === RenderInstruction.CONTRACT_START)  // Only contract starts store data about the ratio and hooks
            .map(instr => getContractSize(instr.ratio, instr.hooks).sizeUp);
    

    // Compute stemTopYs ---
    // For now just put them all as high as possible
    const stemTop = maxContractHeight + maxDecorationMinAboveBars;
    const stemTopYs = instructions
            .filter(instr => instr.hasDrums)  // An instruction has drums <=> An instruction has a stem
            .map(instr => stemTop);
    
    
    // Compute drumYs ---
    
    // Find the actual height of the drums
    const highestDrumId = minKey(id => relativeDrumYs[id], ...Object.keys(relativeDrumYs));  // Returns null if relativeDrumYs is empty
    const highestDrumSizeUp = (highestDrumId !== null) ? getDrumSize(highestDrumId).sizeUp : 0;
    const lowestDrumId = minKey(id => -relativeDrumYs[id], ...Object.keys(relativeDrumYs));  // Negate the key so then we are actually finding the maxKey
    const lowestDrumSizeDown = (lowestDrumId !== null) ? getDrumSize(highestDrumId).sizeDown : 0;
    const lowestDrumAnchor = (lowestDrumId !== null) ? relativeDrumYs[lowestDrumId] : 0;
    const drumsHeight = lowestDrumSizeDown + lowestDrumAnchor + highestDrumSizeUp;  // relativeDrumYs[highestDrumId] === 0 so we don't need to add it
    
    // Figure out if (and by how much) the rests are taller than the drums
    const restAboveDrumsHeight = Math.max(0, maxRestHeight - drumsHeight) / 2;
    
    // Calculate the top of the highest drum
    const topDrumYTop = Math.max(
        stemTop + maxBeamFlagDotHeight + restAboveDrumsHeight,
        maxDecorationMinAboveDrums
    );
    const topDrumY = topDrumYTop + highestDrumSizeUp;  // Anchor of top drum
    
    // Create drumYs
    const drumYs = Object.fromEntries(
        Object.keys(relativeDrumYs).map(id => [id, topDrumY + relativeDrumYs[id]])
    );
    
    
    // Compute restCenterYs ---
    //     We'll just centre with drumYs for now
    const restCenterYs = instructions
            .filter(instr => instr.type === RenderInstruction.REST)
            .map(instr => topDrumYTop + drumsHeight / 2); 
    const toppestRestTop = topDrumYTop + drumsHeight / 2 - maxRestHeight / 2;
    const bottomestRestBottom = topDrumYTop + drumsHeight / 2 + maxRestHeight / 2;
    
    
    // Compute decorationCenterYs
    const decorationCenterYs = instructions
            .filter(instr => instr.type === RenderInstruction.DECORATION)
            .map(instr => getDecorationY(instr.id));
    

    // Get decoration heights ---
    // TODO: Ensure this is consistant with the README doc
    const maxStemTop = Math.max(...stemTopYs, 0);  // TODO: Should we only take into account the adjacent stem tops, or stem tops in that group?
    const bottomDrumYBottom = topDrumYTop + drumsHeight;  // Bottom edge of the lowest drum
    const topInDrumSpace = Math.min(topDrumYTop, toppestRestTop);  // minAboveDrums takes rests into account
    const bottomInDrumSpace = Math.max(bottomDrumYBottom, bottomestRestBottom);  // minBelowDrums takes rests into account
    const decorationHeights = Object.fromEntries(
        // Get set of used decoration ids
        // Then convert to an array so we can map it
        new Array(...new Set(instructions
                    .filter(instr => instr.type === RenderInstruction.DECORATION)
                    .map(instr => instr.decoration)))
        // Get heights of said decoration ids
        .map(id => {
            return [id, computeDecorationHeight(id, bottomInDrumSpace, topInDrumSpace, maxStemTop)];
        })
    );
    
    // Calculate drum center y
    const drumCenterY = (topDrumYTop + bottomDrumYBottom) / 2;
    
    return {drumYs, restCenterYs, contractCenterYs, stemTopYs, decorationCenterYs, decorationHeights, drumCenterY};
}

function computeDecorationY(decoId, drumBottom, drumTop, beamTop) {
    // decoId: str - The id of the decoration that we're finding the y-level of.
    // drumBottom: float - The y-level of the bottom of the bottom drum.
    // drumTop: float - The top of the top drum.
    // beamTop: float - The y-level of the top of the top beam.
    // returns: float - The y-coordinate of the anchor of this decoration, relative to the given coordinate space.
    // 
    // Computes the y-coordinate of the anchor of the given decoration.
    // See the doc for the "new,decoration,..." instruction in src/README.md.
    
    const centerDrumY = (drumTop + drumBottom) / 2;

    const minHeight = Symbols.getDecorationMinHeight(decoId);  // Use the value from symbols as that does not account for stroke width.
    const minAboveDrums = Symbols.getDecorationMinAboveDrums(decoId);
    const minAboveBeams = Symbols.getDecorationMinAboveBars(decoId);
    const minBelowDrums = Symbols.getDecorationMinBelowDrums(decoId);
    
    if (minBelowDrums === null && minAboveDrums === null && minAboveBeams === null) {  
        return centerDrumY;
    } else if (minBelowDrums === null && minAboveDrums === null) {
        return drumTop - minAboveDrums + minHeight / 2;
    } else if (minBelowDrums === null && minAboveBeams === null) {
        return beamTop - minAboveBeams + minHeight / 2;
    } else if (minBelowDrums === null) {  // Both minAbove(beams|drums) were given, so take the minimum (highest up)
        return Math.min(drumTop - minAboveDrums, beamTop - minAboveBeams) + minHeight / 2;
    } else if (minAboveDrums === null && minAboveBeams === null) {  // Only minBelowDrums given
        return drumsBottom + minBelowDrums - minHeight / 2;
    } else if (minAboveBeams === null) {  // minBelowDrums and minAboveDrums given
        return (drumBottom + minBelowDrums + drumTop - minAboveDrums) / 2;
    } else if (minAboveDrums === null) {  // minBelowDrums and minAboveBeams given
        return (drumBottom + minBelowDrums + beamTop - minAboveBeams) / 2;
    } else {  // All are given, so find the heighest of top params
        return (Math.min(drumTop - minAboveDrums, beamTop - minAboveBeams) + drumBottom + minBelowDrums) / 2;
    }
}

function computeDecorationHeight(decoId, drumBottom, drumTop, beamTop) {
    // decoId: str - Id of the decoration to compute the height of.
    // drumBottom: float - The y-level of the bottom of the bottom drum.
    // drumTop: float - The top of the top drum.
    // beamTop: float - The y-level of the top of the top beam.
    // returns: float - The height of this decoration.
    //
    // Computes the height of the given decoration.
        
    const computedY = computeDecorationY(decoId, drumBottom, drumTop, beamTop);

    const minHeight = Symbols.getDecorationMinHeight(decoId);  // Use the value from symbols as that does not account for stroke width.
    const minAboveDrums = Symbols.getDecorationMinAboveDrums(decoId);
    const minAboveBars = Symbols.getDecorationMinAboveBars(decoId);
    const minBelowDrums = Symbols.getDecorationMinBelowDrums(decoId);
    return (-Math.min(  // Get minimum decoration top coordinate
        
            computedY - minHeight / 2,  
            ...((minAboveDrums !== null) ? [drumTop - minAboveDrums] : []),  // This is optional, so I've written it as a list expansion
            ...((minAboveBars !== null) ? [beamTop - minAboveBars] : [])  
        
        ) + Math.max(  // Get maximum decoration bottom coordinate
            
            computedY + minHeight / 2,  
            ...((minBelowDrums !== null) ? [drumBottom + minBelowDrums] : [])  // This is optional, so I've written it as a list expansion
            
        ));
    
}


function minKey(key, ...items) {
    // Returns the item in items with the lowest key(item).
    // If key is not injective then one of the lowest is returned.
    // If items is empty then null is returned.

    let lowestKey = Infinity;
    let lowestItem = null;

    items.forEach(item => {
        const itemKey = key(item);
        if (lowestKey > itemKey) {
            lowestKey = itemKey;
            lowestItem = item;
        }
    });

    return lowestItem;
}

export function calculateScoreComponentSpacing(instructions, vertGroupLinkedComponentInstructions, rhtyhmLengthHint) {
    // instructions: Array<RenderInstruction>
    // vertGroupLinkedComponentInstructions: Set<Array<RenderInstruction>>
    // rhtyhmLengthHint: float
    // 
    // Calculates the spacing specification to which the given RenderInstructions should be drawn with.
    // The calculations are applicable only for instructions. vertGroupLinkedComponentInstructions are used to ensure that drums (etc) shared between vert-linked-bars are drawn at the correct height.
    // The rhtyhmLengthHint is used as a minimum width for the bar. That's to say, should it be possible, horizontal space will be added between groups. This should follow the RenderInstruction.length.
    // 
    // It returns {
    //     instructionXs: [float],  // The x-coordinate of a stem, or the right edge of a rest or decoration, or the location of a contract hook (when required).
    //     drumYs: {str: float},  // A map from drum-id to anchor (the location where the symbol attaches to the stem) y-level.
    //     restCenterYs: [float],  // The y line that rests should be centred on. The index corresponds to the number of previous REST instructions.
    //     contractCenterYs: [float],  // The y line that contracts should be centred on. The index corresponds to the number of previous CONTRACT_START instructions.
    //     stemTopYs: [float],  // The y-level that should be the top of each stem. The index corresponds to the number of previous stems drawn.
    //     decorationCenterYs: [float],  // The y-level that decorations should be centres on. The index corresponds to the number of previous DECORATION instructions.
    //     drumCenterY: float,  // The y-level that the drums are centered on (this includes size of the drums, not just the anchors).
    //     decorationHeights: {str: float}  // A map from decoration-id to decoration height. This height does not include the stroke-width on the boundary.
    // }
    
    // TODO: Take rhtyhmLengthHint into account
    // TODO: stemTopYs inside of groups is unintuative. What if we want to have a beam at an angle
    //          Either: Store for first BEAM in beam-group and for BEAM_END
    //          Or: Calculate the whole slant here (does that really make sense though?)

    const instructionXs = getInstructionXs(instructions);
    const {drumYs, restCenterYs, contractCenterYs, stemTopYs, decorationCenterYs, decorationHeights, drumCenterY} = calculateRestContractStemDeorationDrumYs(instructions, vertGroupLinkedComponentInstructions);

    return {instructionXs, drumYs, restCenterYs, contractCenterYs, stemTopYs, decorationCenterYs, decorationHeights, drumCenterY};
}


// These functions shouldn't be exported normally, but we need data from them for testing
export const _exportedForTesting = {
    computeDecorationHeight, computeDecorationY
}
