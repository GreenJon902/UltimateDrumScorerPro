//
// This is a very basic implementation of spacing.
// Group instructions will not overlap in the x direction, even when it is possible to do so (kick on next subdiv could go under snare (in certain situations)).
// Beams, flags and dots are drawn over the highest drum. So if we need 10 half_beams over a kick, these will not descend into the drum y-space, but will instead push the rhythm notation parts up.
// Similarily, contracts will be drawn over the highest beam/flag/dot.
//
//
//

import {RenderInstruction} from "./compile.js";
import {getRestSize} from "./drawUtils.js";
import {Symbols} from "../symbols.js";

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

    const directRelativeDrumYs = [{id: orderedDrumIds[0], dist: 0}];  // [{id: drumId, dist: float}] where the distance is to the anchor above it. The order of items in this array should be in the order that symbols are drawn top to bottom  // The first item will always have distance 0
    for (let i=1; i<orderedDrumIds.length; i++) {  // i is the index of the drum we are adding.  // Start with i=0 as we've already added item 0.
        const iid = orderedDrumIds[i];
        
        let distRequirement = 0;  // The distance from iid to the drum immediately above iid

        for (let j=0; j<directRelativeDrumYs.length; j++) {  // j is the index of the drum we are comparing to
            const jid = directRelativeDrumYs[j].id;
            
            const currentDist = [
                                    ...directRelativeDrumYs.slice(jid + 1).map(drdy => drdy.dist),
                                    0  // Add zero at the end so reduce works if slice returns no values
                                ].reduce((a, b) => (a + b));
            
            // Check Symbol-constraints between iid and jid
            const constraintMinDist = Symbols.getMinVertDistBetweenDrums(jid, iid);  // We know already that jid is "above" iid, so this will not crash
            if (constraintMinDist > currentDist) {
                distRequirement = constraintMinDist;
            }
            
            // Check if iid collides with jid
            if (drumCollisions[iid].has(jid)) {
                if (Symbols.getDrumSizeDown(jid) > (currentDist - Symbols.getDrumSizeUp(iid))) {
                    distRequirement = Symbols.getDrumSizeDown(jid) + Symbols.getDrumSizeUp(iid);
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
    const lastDrumsSpaceRight = 0;  // A drum-symbol can have size-right, which could impact the next group's instructionX
    const lastRyhthmRight = 0;  // A BEAM, BEAM_END and FLAG instruction stores rhythm information for after the stem, which could impact the next group's instructionX. Also BEAMS go over rests so rests can ignore this
    const lastX = 0;  // Same as last item in instructionXs

    for (let i=0; i<instructions.length; i++) {
        const instr = instructions[i];
        
        let newX, newDrumSpaceRight, newRyhthmRight;
        if (instr.type === RenderInstruction.CONTRACT_START) {
            newX = lastX;
            newDrumSpaceRight = lastDrumsSpaceRight;
            newRyhthmRight = lastRyhthmRight;
            

        } else if (instr.type === RenderInstruction.CONTRACT_END) {
            newX = lastX;
            newDrumSpaceRight = lastDrumsSpaceRight;
            newRyhthmRight = lastRyhthmRight;
            // TODO: Process minimum width of a contract
            

        } else if (instr.type === RenderInstruction.BEAM) {

            
        } else if (instr.type === RenderInstruction.BEAM_END) {

            
        } else if (instr.type === RenderInstruction.FLAG) {

            
        } else if (instr.type === RenderInstruction.REST) {
            const restSize = getREstSize(instr.ticks, instr.dots);
            
            newX = lastDrumsSpaceRight + restSize.sizeLeft;
            newDrumSpaceRight = newX + restSize.sizeRight;  // Rests are drawn in drum-space
            newRyhthmRight = lastRyhthmRight;  // Rests are below bars so don't impact them

            
        } else {
            throw "Unknown instruction type " + instr.type;
        }
    }
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
    //     decorationCenterYs: [float]  // The y-level that decorations should be centres on. The index corresponds to the number of previous DECORATION instructions.
    // }
    
    console.log(getRelativeDrumYs(vertGroupLinkedComponentInstructions))
    console.log(getInstructionXs(instructions));

}
