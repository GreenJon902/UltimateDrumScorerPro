import {drawDrumAt, drawDecorationAt, drawStem, drawBeams, drawFlags, drawDots, drawRest, drawContract, createMain} from "./drawUtils.js";
import {RenderInstruction} from "./compile.js";


export function renderScoreComponentFromInstructionsAndSpacing(svg, instructions, spacing) {
    // svg: SVG
    // instructions: Array<RenderInstruction>
    // spacing: {
    //     instructionXs: [float],  // The x-coordinate of a stem, or the right edge of a rest or decoration, or the location of a contract hook (when required).
    //     drumYs: {str: float},  // A map from drum-id to anchor (the location where the symbol attaches to the stem) y-level.
    //     restCenterYs: [float],  // The y line that rests should be centred on. The index corresponds to the number of previous REST instructions.
    //     contractCenterYs: [float],  // The y line that contracts should be centred on. The index corresponds to the number of previous CONTRACT_START instructions.
    //     stemTopYs: [float],  // The y-level that should be the top of each stem. The index corresponds to the number of previous stems drawn.
    //     decorationCenterYs: [float],  // The y-level that decorations should be centres on. The index corresponds to the number of previous DECORATION instructions.
    //     drumCenterYs: float,  // The y-level that the drums are centered on (this includes size of the drums, not just the anchors).
    //     decorationHeights: [float]  // The decoration heights. This height does not include the stroke-width on the boundary. The index corresponds to the number of previous DECORATION instructions.
    // }
    //
    // Renders the given instructions to the given svg using the given spacing data.
    
    const main = createMain(svg); // The container in which to draw everything
    
    let prevStemCount = 0;  // The number of stems we've already drawn
    let prevDecorationCount = 0;  // The number of decorations we've already drawn
    let prevRestCount = 0;  // The number of rests we've already drawn
    let prevContractCount = 0;  // The number of contracts we've already drawn
    for (let instrI = 0; instrI < instructions.length; instrI++) {
        const instr = instructions[instrI];

        // Draw flags, dots and beams ---
        // Do this before draw stem so prevStemCount is still accurate
        if (instr.type === RenderInstruction.BEAM) {
            const beamStartX = spacing.instructionXs[instrI];
            const beamStartY = spacing.stemTopYs[prevStemCount];
            const nextStemI = findSatisfying(instructions, instrI, 1, i => i.hasDrums);  // There must be a BEAM or BEAM_END after instr (before any FLAGs), this is what we want to join the beams to
            const beamEndX = spacing.instructionXs[nextStemI];  
            const beamEndY = spacing.stemTopYs[prevStemCount + 1];  // There must be a BEAM or BEAM_END after instr (before any FLAGs), this is what we want to join the beams to            
            drawBeams(svg, main, instr.fullBeams, instr.brokenBeams, instr.dots, beamStartX, beamStartY, beamEndX, beamEndY);
        } else if (instr.type === RenderInstruction.BEAM_END) {
            drawDots(svg, main, instr.dots, spacing.instructionXs[instrI], spacing.stemTopYs[prevStemCount]);
        } else if (instr.type === RenderInstruction.FLAG) {
            drawFlags(svg, main, instr.flags, instr.dots, spacing.instructionXs[instrI], spacing.stemTopYs[prevStemCount]);
        }
        
        // Draw symbols ---
        if (instr.hasDrums) {
            // Draw the symbols
            instr.drums.forEach(drumId => {
                const x = spacing.instructionXs[instrI];
                const y = spacing.drumYs[drumId];
                
                drawDrumAt(svg, main, drumId, x, y);
            });
            
            // An instruction has a stem iff it has symbols, so draw the stem
            const stemX = spacing.instructionXs[instrI];
            const stemTopY = spacing.stemTopYs[prevStemCount];
            const stemBottomY = Math.max(...Array.from(instr.drums).map(id => spacing.drumYs[id]));  // Get the anchor of the lowest drum
            drawStem(svg, main, stemX, stemTopY, stemBottomY);
            
            prevStemCount++;
        }
        

        // Draw decorations ---
        if (instr.type === RenderInstruction.DECORATION) {
            drawDecorationAt(svg, main, instr.decoration, spacing.instructionXs[instrI], spacing.decorationCenterYs[prevDecorationCount], spacing.decorationHeights[prevDecorationCount], spacing.drumCenterY);
            prevDecorationCount++;
        }
        
        // Draw rests ---
        if (instr.type === RenderInstruction.REST) {
            drawRest(svg, main, instr.ticks, instr.dots, spacing.instructionXs[instrI], spacing.restCenterYs[prevRestCount]);
            prevRestCount++;
        }
        
        // Draw contracts ---
        if (instr.type === RenderInstruction.CONTRACT_START) {
            const contractStartX = spacing.instructionXs[instrI];
            const contractEndX = spacing.instructionXs[findSatisfying(instructions, instrI, 1, i => i.type === RenderInstruction.CONTRACT_END)];
            const contractY = spacing.contractCenterYs[prevContractCount];
            drawContract(svg, main, instr.ratio, instr.hooks, contractStartX, contractEndX, contractY);
            prevContractCount++;
        }
    }
}

function findSatisfying(array, start, direction, func) {
    // Searches through the array from the given start position in the given direction (+1 for forwards or -1 for backwards) for the first item for which func returns true.
    // This returns the index of that item.
    
    for (let i=start+direction; 0<=i && i<array.length; i+=direction) {
        if (func(array[i])) return i;
    }

    throw "None satisfying function found";
}
