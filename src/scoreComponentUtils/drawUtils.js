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

