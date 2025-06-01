const symbols = {
    "slanted-line": {
        "path": "M0 0 L-20 10",
        "left": -20,
        "right": 0,
        "top": 0,
        "bottom": 10,
    }, 
    "slanted-circled-line": {
        "path": "M0 0 L-20 10 C-25 0 -5 -10 0 0 C5 10 -15 20 -20 10",
        "left": -20.8,  // Approximate values
        "right": 0.8,
        "top": -4.1,
        "bottom": 14.1,
    },
    "cross": {
        "path": "M0 0 L-20 20 M-20 0 L0 20",
        "left": -20,
        "right": 0,
        "top": 0,
        "bottom": 20
    }
,
    "shallow-cross": {
        "path": "M0 0 L-20 10 M-20 0 L0 10",
        "left": -20,
        "right": 0,
        "top": 0,
        "bottom": 10
    },
    "star": {
        "path": "M-2.5 2.5 L-17.5 17.5 M-17.5 2.5 L-2.5 17.5 M-10 0 L-10 20 M0 10 L-20 10",
        "left": -20,
        "right": 0,
        "top": 0,
        "bottom": -20

    }
};

export function getSymbolPath(symbolId) {
    // Gets the svg path string for the given symbol.
    // Since symbolIDs are shared between drums and decorations:
    //     For drums the 0,0 position is where the note anchors to the stem.
    //     For decorations the 0,0 is the bottom-middle.
    // Returned paths will move to 
    return symbols[symbolId]["path"];
}

export function getSymbolLeft(symbolId) {
    // Gets the displacement of the left edge of the symbol from the center (negative is to the left).
    return symbols[symbolId]["left"];
}

export function getSymbolRight(symbolId) {
    // Gets the displacement of the right edge of the symbol from the center (negative is to the left).
    return symbols[symbolId]["right"];
}

export function getSymbolTop(symbolId) {
    // Gets the displacement of the top edge of the symbol from the center (negative is up).
    return symbols[symbolId]["top"];
}

export function getSymbolBottom(symbolId) {
    // Gets the displacement of the bottom edge of the symbol from the center (negative is up).
    return symbols[symbolId]["bottom"];
}

export function getSymbolIDs() {
    // Lists all symbol IDs
    return Object.keys(symbols);
}
