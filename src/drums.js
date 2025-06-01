const drums = {
    "kick": {
        "symbol": "slanted-line",
        "y": 50
    },
    "snare": {
        "symbol": "slanted-line",
        "y": 30
    }
}

export function getDrumSymbolID(drumID) {
    // Returns the symbolID for the given drum
    return drums[drumID]["symbol"];
}

export function getDrumY(drumID) {
    // Returns the y position to draw and connect the stem of a given drum
    return drums[drumID]["y"];
}
