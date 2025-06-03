const drums = {
    "kick": {
        "symbol": "slanted-line",
        "y": 100
    },
    "low-floor-tom": {
        "symbol": "slanted-circled-line",
        "y": 90
    },
    "high-floor-tom": {
        "symbol": "slanted-circled-line",
        "y": 80
    },
    "snare": {
        "symbol": "slanted-line",
        "y": 70
    },
    "low-rack-tom": {
        "symbol": "slanted-circled-line",
        "y": 60
    },
    "high-rack-tom": {
        "symbol": "slanted-circled-line",
        "y": 50
    },
    "hi-hat": {
        "symbol": "cross",
        "y": 40
    },
    "ride": {
        "symbol": "shallow-cross",
        "y": 40
    },
    "crash": {
        "symbol": "star",
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
