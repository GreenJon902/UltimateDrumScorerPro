    console.log("2");
function splitDrawAndSize(func) {
    // Splits a function "drawAndGetSize..." into "draw..." and "getSize...".
    // func should return {svg, width, height}, then the two function return svg and {width, height} respectively.
    // These functions are automatically exported.
    // 
    // This is useful because we may not want to maintain two coppies of each function. But we don't need the svg in the spacer.
    
    // Get new function names
    console.log("1");
    if (!func.name.startsWith("drawAndGetSize")) throw "Function name invalid " + func.name;
    const specificName = func.name.replace("drawAndGetSize", "");  // Only replaces first
    const drawName = "draw" + specificName;
    const sizeName = "getSize" + specificName;
    
    // Define functions
    const splitDrawAndSize_drawFunc = (...args) => func(...args).svg;
    const splitDrawAndSize_sizeFunc = (...args) => {
        const ret = func(...args);
        return {width: ret.width, height: ret.height};
    };
    
    // Export function
    if (module.exports.hasOwnProperty(drawName) || module.hasOwnProperty(sizeName)) throw "Functions already defined " + drawnName + " " + sizeName;
    module.exports[drawName] = splitDrawAndSize_drawFunc;
    console.log(sizeName);
    module.exports[sizeName] = splitDrawAndSize_sizeFunc;
}

export function drawAndGetSizeRest(ticks, dots) {
    // Draws a rest with the given number of ticks and dots.
    // If ticks is zero then a crotchet rest is drawn.
    // Returns {svg, width: float, height: float}
}
splitDrawAndSize(drawAndGetSizeRest);
