import {drawSymbolAt, drawStem} from "./drawUtils.js";


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
    
    let prevStemCount = 0;  // The number of stems we've already drawn
    for (let instrI = 0; instrI < instructions.length; instrI++) {
        const instr = instructions[instrI];

        if (instr.hasDrums) {
            // Draw the symbols
            instr.drums.forEach(drumId => {
                const x = spacing.instructionXs[instrI];
                const y = spacing.drumYs[drumId];
                
                drawSymbolAt(svg, svg, drumId, x, y);
            });
            
            // An instruction has a stem iff it has symbols, so draw the stem
            const stemX = spacing.instructionXs[instrI];
            const stemTopY = spacing.stemTopYs[prevStemCount];
            const stemBottomY = Math.max(...Array.from(instr.drums).map(id => spacing.drumYs[id]));  // Get the anchor of the lowest drum
            drawStem(svg, svg, stemX, stemTopY, stemBottomY);
        }
        
    }

}
