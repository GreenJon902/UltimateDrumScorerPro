import {drawSymbolAt} from "./drawUtils.js";


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
                
                drawSymbolAt(svg, svg, drumId, x, y);
            });
        }
    }

}
