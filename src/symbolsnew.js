
function dequeue(tokens) {
    // Removes the first element from the array, and throws an error if it doesn't exist.
    if (tokens.length === 0) throw "Failed to dequeue element as tokens' length is 0";
    return tokens.shift();  // Shift removes first item from the array then returns it
}

function peek(tokensm i=0) {
    // Peeks at the ith element from the start of the given array, and throws an error if it doesn't exist.
    if (tokens.length >= i) throw "Failed to peek element as tokens' length is 0";
    return tokens[i];  
}

function ensureStringIsLowerAndGiven(string, ...allowedNonAlpha) {
    // Ensures the given string is lower case and only contains alpha and the given non-alphas.
    // If it is correct then it is returned, otherwise an error is thrown.
    if (string.toLowerCase() !== string) throw "Given string has upper case";
    if (new Set(string.split("")).intersection(new Set(string.toUpperCase().split(""))).difference(new Set(allowedNonAlphanumeric)).size !== 0) throw "String contains not allowed characters";
    return string;
}

function ensureSymbolIdPart(string) {
    // Ensures the given string is formatted as a valid symbol id part (e.g. "hello-world").
    // If it is correct then it is returned, otherwise an error is thrown.
    return ensureStringIsLowerAndGiven(string, "-");
}

function ensureSymbolId(string) {
    // Ensures the given string is a valid symbol-id (e.g. "hello-world", "hello-world_i-am_jon").
    // If it is correct then it is returned, otherwise an error is thrown.
    // 
    // If a string is a symbolIdPart then it necessarily passes this function too.
    ensureStringIsLowerAndGiven(string, "-", "_");
}

function ensureExists(id, parseData) {
    // Ensures the given id exists.
    // If it does then the id is returned, otherwise an error is thrown.
    if (!(parseData.groups.has(id) || id in parseData.drums || id in parseData.parts || id in parseData.decorations)) throw "Given id not in parse data";
    return id;
}

function ensureDoesNotExist(id, parseData) {
    // Ensures the given id does not exist.
    // If it does then an error is thrown, otherwise it is returned.
    if (parseData.groups.has(id) || id in parseData.drums || id in parseData.parts || id in parseData.decorations) throw "Given id already in parse data";
    return id;
}

function splitSymbolId(string) {
    // Ensures the given symbol id is valid, if it isn't then an error is thrown.
    // Returns {base: baseSymbolId, modifiers: Array<modifierId>}.
    ensureStringIsLowerAndGiven(string, "-", "_");
    const [base, ...modifiers] = string.split("_");
    return {base: base, modifiers: modifiers};
}

function parseModifierSizeChanger(string) {
    // Parses the delta or min size left/up/right/down for the auto modifier.
    // Returns {delta: int, min: int}.
    if (string === "0") {
        return {delta: 0, min: 0};
    } else if (string[0] === "+") {
        return {delta: parseFloat(string.slice(1)), min: 0};
    } else if (string[0] === ">") {
        return {delta: 0, min: parseFloat(string.slice(1))};
    } else {
        throw "Unrecognised size modifier for given string";
    }
}

function parseSymbolSourceString(symbolsSource) {
    // Parse the given symbol source string. This string is made of actions with arguments which are all separated by commas.
    // This loads them into thise maps: parts, symbols, constraints.
    // See individual parsing functions for each action type.
    // 
    // This returns a parseData object (see creation for doc).
    
    const parseData = {
        parts: {},  // {part-id: {instructions: Array<SvgInstruction>}}
        drums: {},  // {symbol-id: {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float, instructions: Array<SvgInstruction>, groups: Array<group-id>}}
        decorations: {},  // {decoration-id: {width: float, minHeight: float, minBelowDrums: float|null, minAboveDrums: float|null, minAboveBars: float|null, instructions: Array<SvgInstruction>}}
        constraints: new Set(),  // {topId: (symbol|group)-id, bottomId: (symbol|group)-id, distance: float}
        groups: new Set()  // group-id
    }

    const tokens = symbolsSource.split(",");
    while (tokens.length != 0) {
        // Figure out which specific parse function to call, and then call it
        const action = dequeue(tokens);
        let actionFunction = {  // Select which function we want to call
            "new": parseNew,
            "modifier": parseModifier,
            "constraint": parseConstraint
        }[action];
        if (actionFunction === undefined) throw "Unknown action " + action;
        actionFunction(tokens, parseData);  // Functions update tokens array and parseData for us
    }
    
    return parseData;
}

function parseNew(tokens, parseData) {
    // Parses a statement that begins with new from the tokens.
    // This expects that new to have already been consumed.
    // This will remove tokens from the array, and add the result to parseData.

    const what = dequeue(tokens);
    let whatFunction = {  // Select which function we want to call
        "drum": parseNewDrum,
        "decoration": parseNewDecoration
    }[what];
    if (whatFunction === undefined) throw "Unknown what " + what;
    whatFunction(tokens, parseData);  // Functions update tokens array and parseData for us
}
