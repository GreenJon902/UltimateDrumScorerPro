
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

function ensureSymbolId(string, mustBeModified=false) {
    // Ensures the given string is a valid symbol-id (e.g. "hello-world", "hello-world_i-am_jon").
    // If it is correct then it is returned, otherwise an error is thrown.
    // 
    // If a string is a symbolIdPart then it necessarily passes this function too.
    // 
    // If mustBeModified is true then the id must be modified (contain an _).
    
    ensureStringIsLowerAndGiven(string, "-", "_");
    
    if (mustBeModified && !string.includes("_")) throw "Id must be modified but is not";
    
    return string;
}

function ensureExists(id, parseData, group=true, drum=true, part=true, decoration=true) {
    // Ensures the given id exists.
    // If it does then the id is returned, otherwise an error is thrown.
    // If group, drum, part, or decoration is false then that specific one will not be checked.
    if (!((group && parseData.groups.has(id)) || (drum && id in parseData.drums) || (part && id in parseData.parts) || (decoration && id in parseData.decorations))) throw "Given id not in parse data";
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

function parseOptionalFloat(string) {
    // Parses an optional float -> float, or an empty string to null.

    if (string === "") return null;
    return parseFloat(string);
}

function parseList(tokens, parseItem, ...parseItemArgs) {
    // Parses a list from the given token array.
    // This expects the first token to be the length of the array. It consumes this value.
    // It will then call the parseItem(tokens, ...parseItemArgs)->result function that many times, and expects it to consume any tokens it uses.
    // This then returns an array with the results.
    
    const n = parseInt(dequeue(tokens));
    const listValues = new Array();
    for (let i=0; i<n; i++) {
        listValues.push(parseItem(tokens, ...parseItemArgs));
    }
}

function parseInstruction(tokens, parseData) {
    // Parses an instruction from the given tokens.
    // Expects this instruction to be first, and will consume it.
    // This will not update parseData, it will only query it.
    // 
    // See src/README.md for instruction types.

    const instructionName = dequeue(tokens);
    if (instructionName === "path") {
        const pathString = dequeue(tokens);
        return SvgInstruction(SvgInstruction.PATH, pathString);
    } else if (instructionName === "circle") {
        const cx = parseFloat(dequeue(tokens));
        const cy = parseFloat(dequeue(tokens));
        const r = parseFloat(dequeue(tokens));
        return SvgInstruction(SvgInstruction.CIRCLE, cx, cy, r);
    } else if (instructionName === "use") {
        const id = ensureExists(ensureSymbolId(dequeue(tokens)), parseData, group=false);  // We can't draw a group so don't check those.
        return SvgInstruction(SvgInstruction.USE, id);
    } else if (instructionName === "push-transform") {
        const transformString = dequeue(tokens);
        return SvgInstruction(SvgInstruction.PUSH_TRANSFORM, transformString);
    } else if (instructionName === "pop-transform") {
        return SvgInstruction(SvgInstruction.POP_TRANSFORM);
    } else {
        throw "Instruction " + instructionName + " is not recognised";
    }
}

function parseGroup(tokens) {
    // Parses a group-id from the given tokens.
    // This will consume that token, and expects it to be first.
    // This will not add the groups to parseData.
    return ensureSymbolIdPart(dequeue(tokens));
}

function parseSymbolSourceString(symbolsSource) {
    // Parse the given symbol source string. This string is made of actions with arguments which are all separated by commas.
    // This loads them into thise maps: parts, symbols, constraints.
    // See individual parsing functions for each action type.
    // 
    // This returns a parseData object (see creation for doc).
    
    const parseData = {
        parts: {},  // {part-id: {instructions: Object.freeze(Array<SvgInstruction>)}}
        drums: {},  // {symbol-id: Object.freeze({sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float, instructions: Object.freeze(Array<SvgInstruction>), groups: Object.freeze(Array<group-id>)})}
        decorations: {},  // {decoration-id: Object.frreze({width: float, minHeight: float, minBelowDrums: float|null, minAboveDrums: float|null, minAboveBars: float|null, instructions: Object.freeze(Array<SvgInstruction>)})}
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

function parseModifier(tokens, parseData) {
    // Parses a statement that begins with modifier from the tokens.
    // This expects that modifier to have already been consumed.
    // This will remove tokens from the array, and add the result to parseData.

    const what = dequeue(tokens);
    let whatFunction = {  // Select which function we want to call
        "drum": parseModifierDrum
    }[what];
    if (whatFunction === undefined) throw "Unknown what " + what;
    whatFunction(tokens, parseData);  // Functions update tokens array and parseData for us
}

function parseModifierDrum(tokens, parseData) {
    // Parses a statement that begins with modifier,drum from the tokens.
    // This expects that modifier,drum to have already been consumed.
    // This will remove tokens from the array, and add the result to parseData.

    const how = dequeue(tokens);
    let howFunction = {  // Select which function we want to call
        "explicit": parseModifierDrumExplicit,
        "auto": parseModifierDrumAuto
    }[how];
    if (howFunction === undefined) throw "Unknown how " + how;
    howFunction(tokens, parseData);  // Functions update tokens array and parseData for us
}

function parseConstraint(tokens, parseData) {
    // Parses a statement that begins with constraint from the tokens.
    // This expects that constraint to have already been consumed.
    // This will remove tokens from the array, and add the result to parseData.

    const what = dequeue(tokens);
    let whatFunction = {  // Select which function we want to call
        "drum": parseConstraintDrum
    }[what];
    if (whatFunction === undefined) throw "Unknown what " + what;
    whatFunction(tokens, parseData);  // Functions update tokens array and parseData for us
}

function parseNewDrum(tokens, parseData) {
    // Parses a statement that begins with new,drum from the tokens.
    // This expects that new,drum to have already been consumed.
    // This will remove tokens from the array, and add the result to parseData.
    // 
    // See src/README.md for token doc.

    // Parse all parts of data for drum
    const id = ensureDoesNotExist(ensureSymbolIdPart(dequeue(tokens)), parseData);
    const sizeLeft = parseFloat(dequeue(tokens));
    const sizeUp = parseFloat(dequeue(tokens));
    const sizeRight = parseFloat(dequeue(tokens));
    const sizeDown = parseFloat(dequeue(tokens));
    const instructions = parseList(tokens, parseInstruction, parseData);
    const groups = parseList(tokens, parseGroup);
    
    // Add groups to parseData
    groups.forEach(g => parseData.groups.add(g));
    
    // Add drum to parseData
    parseData.drums[id] = {sizeLeft: sizeLeft, sizeUp: sizeUp, sizeRight: sizeRight, sizeDown: sizeDown, instructions: Object.freeze(instructions), groups: Object.freeze(groups)};
}

function parseNewDecoration(tokens, parseData) {
    // Parses a statement that begins with new,decoration from the tokens.
    // This expects that new,decoration to have already been consumed.
    // This will remove tokens from the array, and add the result to parseData.
    // 
    // See src/README.md for token doc.

    // Parse all parts of data for decoration
    const id = ensureDoesNotExist(ensureSymbolIdPart(dequeue(tokens)), parseData);
    const width = parseFloat(dequeue(tokens));
    const minHeight = parseFloat(dequeue(tokens));
    const minBelowDrums = parseOptionalFloat(dequeue(tokens));
    const minAboveDrums = parseOptionalFloat(dequeue(tokens));
    const minAboveBars = parseOptionalFloat(dequeue(tokens));
    const instructions = parseList(tokens, parseInstruction, parseData);
    
    // Add decoration to parseData
    groups.decorations[id] = {width: width, minHeight: minHeight, minBelowDrums: minBelowDrums, minAboveDrums: minAboveDrums, minAboveBars: minAboveBars, instructions: Object.freeze(instructions)};
}

function parseModifierDrumExplicit(tokens, parseData) {
    // Parses a statement that begins with modifier,drum,explicit from the tokens.
    // This expects that modifier,drum,explicit to have already been consumed.
    // This will remove tokens from the array, and add the result to parseData.
    // 
    // See src/README.md for token doc.

    // Parse all parts of data for modifier
    const id = ensureDoesNotExist(ensureSymbolId(dequeue(tokens), mustBeModified=true));
    ensureExists(splitSymbolId(id).base);  // Ensure base exists
    const sizeLeft = parseFloat(dequeue(tokens));
    const sizeUp = parseFloat(dequeue(tokens));
    const sizeRight = parseFloat(dequeue(tokens));
    const sizeDown = parseFloat(dequeue(tokens));
    const instructions = parseList(tokens, parseInstruction, parseData);
    const groups = parseList(tokens, parseGroup);
    
    // Add groups to parseData
    groups.forEach(g => parseData.groups.add(g));
    
    // Add drum to parseData
    parseData.drums[id] = {sizeLeft: sizeLeft, sizeUp: sizeUp, sizeRight: sizeRight, sizeDown: sizeDown, instructions: Object.freeze(instructions), groups: Object.freeze(groups)};
}

function parseModifierDrumAuto(tokens, parseData) {
    // Parses a statement that begins with modifier,drum,auto from the tokens.
    // This expects that modifier,drum,auto to have already been consumed.
    // This will remove tokens from the array, and add the result to parseData.
    // 
    // See src/README.md for token doc.

    // TODO: This
}

function parseConstraintDrum(tokens, parseData) {
    // Parses a statement that begins with constraint,drum from the tokens.
    // This expects that constraint,drum to have already been consumed.
    // This will remove tokens from the array, and add the result to parseData.
    // 
    // See src/README.md for token doc.

    // TODO: This
}

class SvgInstruction {
    // An instruction for how to create the svg nodes for a given symbol. Multiple of these create a symbol.
    //
    // There are a couple types of svg-instructions (and what they store):
    //      PATH:
    //          - path - The value of the `d` attribute of the node.
    //      CIRCLE:
    //          - cx - The centre x of the circle.
    //          - cy - The centre y of the circle.
    //          - r - The radius of the circle.
    //      USE:
    //          - id - The id of the part or symbol to use.
    //      PUSH-TRANSFORM:
    //          - transform - The value to put in the svg transform value.
    //      POP-TRANSFORM:

    // Instruction types
    static get PATH() {return "PATH";}  // Declare like this so are immutable
    static get CIRCLE() {return "CIRCLE";} 
    static get USE() {return "USE";}  
    static get PUSH_TRANSFORM() {return "PUSH-TRANSFORM";}  
    static get POP_TRANSFORM() {return "POP-TRANSFORM";}  
    
    constructor(type, ...args) {
        // Type should be the value in PATH, CIRCLE...
        // Args should be passed in the order they are documented in.
        
        this.type = type;
        if (type === SvgInstruction.PATH) {
            this.path = args[0];
        } else if (type === SvgInstruction.CIRCLE) {
            this.cx = args[0];
            this.cy = args[1];
            this.r = args[2];
        } else if (type === SvgInstruction.USE) {
            this.id = args[0];
        } else if (type === SvgInstruction.PUSH_TRANSFORM) {
            this.transform = args[0];
        } else if (type === SvgInstruction.POP_TRANSFORM) {
            // There are no args for this
        } else {
            throw "Unknown type " + type;
        }
        
        Object.freeze(this);  // Make final
    }
}
