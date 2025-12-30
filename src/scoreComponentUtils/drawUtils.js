function drawAndGetSizeRest(ticks, dots) {
    // Draws a rest with the given number of ticks and dots.
    // If ticks is zero then a crotchet rest is drawn.
    // Returns {svg, size: {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float}}
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
