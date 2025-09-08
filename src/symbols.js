import { SYMBOLS_SOURCE } from "./_symbols_source.js";

function dequeue(tokens) {
    // Removes the first element from the array, and throws an error if it doesn't exist.
    if (tokens.length === 0) throw "Failed to dequeue element as tokens' length is 0";
    return tokens.shift();  // Shift removes first item from the array then returns it
}

function ensureStringIsLowerAndGiven(string, ...allowedNonAlphanumeric) {
    // Ensures the given string is lower case and only contains alphanumerics and the given non-alphanumerics.
    // If it is correct then it is returned, otherwise an error is thrown.
    if (string.toLowerCase() !== string) throw "Given string has upper case";
    if (new Set(string.split("")).intersection(new Set(string.toUpperCase().split(""))).difference(new Set(allowedNonAlphanumeric)).size !== 0) throw "String contains not allowed characters";
    return string;
}

function ensureBaseSymbolId(string) {
    // Ensures the given string is formatted as a valid base-symbol-id/part-symbol-id/modifier-id: "some-id".
    // If it is correct then it is returned, otherwise an error is thrown.
    return ensureStringIsLowerAndGiven(string, "-");
}
const ensurePartSymbolId = ensureBaseSymbolId;
const ensureModifierId = ensureBaseSymbolId;

function ensureSymbolOrGroupId(string) {
    // Ensures the given string is formatted as a valid symbol-id/group-id: "some-id_some-modifier"/"some-id".
    // If it is correct then it is returned, otherwise an error is thrown.
    return ensureStringIsLowerAndGiven(string, "-", "_");
}
const ensureSymbolOrPartSymbolId = ensureSymbolOrGroupId;

function ensureExists(id) {
    // Ensures the given id (symbol-id or group-id) exists.
    // If it does then the id is returned, otherwise an error is thrown.
    return id;
}

function ensureDoesNotExist(id) {
    // Ensures the given id (symbol-id or group-id) does not exist.
    // If it does then an error is thrown, otherwise it is returned.
    return id;
}

function splitSymbolId(string) {
    // Ensures the given symbol id is valid, if it ins't then an error is thrown.
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

    const tokens = symbolsSource.split(",");
    while (tokens.length != 0) {
        // Figure out which specific parse function to call, and then call it
        const action = dequeue(tokens);
        const actionFunction = {
            "new_base": parseNewBase,
            "new_part": parseNewPart,
            "modifier_explicit": parseModifierExplicit,
            "modifier_auto": parseModifierAuto,
            "head_constraint": parseHeadConstraint
        }[action];
        if (actionFunction === undefined) throw "Unknown action " + action;
        actionFunction(tokens);  // Functions update tokens array for us
    }
}

function parseNewBase(tokens) {
    // Parse a new_base action from the array of tokens. 
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this base-symbol-id,size-left,size-up,size-down,<instructions>,<groups>.
    const baseSymbolId = ensureBaseSymbolId(dequeue(tokens));
    const sizeLeft = parseFloat(dequeue(tokens));
    const sizeUp = parseFloat(dequeue(tokens));
    const sizeRight = parseFloat(dequeue(tokens));
    const sizeDown = parseFloat(dequeue(tokens));
    const instructions = parseInstructions(tokens);
    const groups = parseGroups(tokens);
}

function parseNewPart(tokens) {
    // Parse a new_part action from the array of tokens. 
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this base-symbol-id,<instructions>.
    const partSymbolId = ensureDoesNotExist(ensurePartSymbolId(dequeue(tokens)));
    const instructions = parseInstructions(tokens);
}

function parseModifierExplicit(tokens) {
    // Parse a modifier_explicit action from the array of tokens.
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this base_symbol-id(_modifier-id)+,size-left,size-up,size-down,<instructions>,<groups>.
    const {base: baseSymbolId, modifiers: modifierIds} = splitSymbolId(ensureDoesNotExist(dequeue(tokens)));
    ensureExists(baseSymbolId);
    if (modifierIds.length === 0) throw "Expected at least one modifierId";
    const sizeLeft = parseFloat(dequeue(tokens));
    const sizeUp = parseFloat(dequeue(tokens));
    const sizeRight = parseFloat(dequeue(tokens));
    const sizeDown = parseFloat(dequeue(tokens));
    const instructions = parseInstructions(tokens);
    const groups = parseGroups(tokens);
}

function parseModifierAuto(tokens) {
    // Parse a modifier_auto action from the array of tokens.
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this modifier-id,<pattern>,(+detla,>min)size-left,(+detla,>min)size-right,(+detla,>min)size-up,(+detla,>min)size-down,min-width,min-height,<instructions>,<groups>.
    const modifierId = ensureModifierId(dequeue(tokens));  // We don't mind if the modifierId already exists, if we want to apply it to a symbolId then we can check then
    const symbolIds = parsePatternAndGetMatchingSymbols(tokens);
    const {delta: sizeLeftDelta, min: minSizeLeft} = parseModifierSizeChanger(dequeue(tokens));
    const {delta: sizeUpDelta, min: minSizeUp} = parseModifierSizeChanger(dequeue(tokens));
    const {delta: sizeRightDelta, min: minSizeRight} = parseModifierSizeChanger(dequeue(tokens));
    const {delta: sizeDownDelta, min: minSizeDown} = parseModifierSizeChanger(dequeue(tokens));
    const minWidth = parseFloat(dequeue(tokens));
    const minHeight = parseFloat(dequeue(tokens));
    const extraInstructions = parseInstructions(tokens, true);
    const extraGroups = parseGroups(tokens);
}

function parseHeadConstraint(tokens) {
    // Parse a modifier_auto action from the array of tokens.
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this top-(symbol|group)-id,bottom-(symbol|group)-id,distance.
    const topId = ensureExists(ensureSymbolOrGroupId(dequeue(tokens)));
    const bottomId = ensureExists(ensureSymbolOrGroupId(dequeue(tokens)));
    const distance = parseInt(dequeue(tokens));
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
    //      PUSH-ANCHORED-TRANSFORM:
    //          - horizAnchor - LEFT,MIDDLE,RIGHT - of the parent symbol
    //          - vertAnchor - TOP,MIDDLE,BOTTOM - of the parent symbol

    // Instruction types
    static get PATH() {return "PATH";}  // Declare like this so are immutable
    static get CIRCLE() {return "CIRCLE";} 
    static get USE() {return "USE";}  
    static get PUSH_TRANSFORM() {return "PUSH-TRANSFORM";}  
    static get POP_TRANSFORM() {return "POP-TRANSFORM";}  
    static get PUSH_ANCHORED_TRANSFORM() {return "PUSH-ANCHORED-TRANSFORM";}  
    
    // Anchor types
    static get LEFT() {return "LEFT";}
    static get MIDDLE() {return "LEFT";}
    static get RIGHT() {return "LEFT";}
    static get TOP() {return "LEFT";}
    static get BOTTOM() {return "LEFT";}
    
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
        } else if (type === SvgInstruction.PUSH_ANCHORED_TRANSFORM) {
            this.horizAnchor = args[0];
            this.vertAnchor = args[1];
        } else {
            throw "Unknown type " + type;
        }
    }
}

function parseInstructions(tokens, allow_push_anchord_transform=false) {
    // Parse and return the instructions (as an svg element (e.g. <group> or <path>, not <svg>)) that are at the start of tokens.
    // This removes the tokens from the given array.
    // 
    // This expects the following tokens to be the number of instructions followed by the instructions.
    // The instructions can be these:
    //      `path`,`path-string`  
    //      `circle`,`cx`,`cy`,`r`  
    //      `use`,`symbol-id`  
    //      `use`,`part-symbol-id`  
    //      `push-transform`,`transform-string`  
    //      `pop-transform`  
    const numberOfInstruction = parseInt(dequeue(tokens));
    const instructions = new Array();  // Array of generated instructions
    for (let i=0; i<numberOfInstruction; i++) {
        const instructionName = dequeue(tokens);
        switch (instructionName) {
            case "path":
                instructions.push(new SvgInstruction(SvgInstruction.PATH, dequeue(tokens)));
                break;
            case "circle":
                instructions.push(new SvgInstruction(SvgInstruction.CIRCLE, dequeue(tokens), dequeue(tokens), dequeue(tokens)));
                break;
            case "use":
                instructions.push(new SvgInstruction(SvgInstruction.USE, dequeue(tokens)));
                break;
            case "push-transform":
                instructions.push(new SvgInstruction(SvgInstruction.PUSH_TRANSFORM, dequeue(tokens)));
                break;
            case "pop-transform":
                instructions.push(new SvgInstruction(SvgInstruction.POP_TRANSFORM));
                break;
            case "push-anchored-transform":
                if (!allow_push_anchord_transform) throw "Push-anchored-transform is currently disabled";
                instructions.push(new SvgInstruction(SvgInstruction.PUSH_ANCHORED_TRANSFORM, dequeue(tokens), dequeue(tokens)));
                break;
            default:
                throw "Invalid instruction name " + instructionName;
        }
    }
    return Object.freeze(instructions);
}

function parseGroups(tokens) {
    // Parse and return a list of groups from the list of tokens.
    // This removes the tokens from the given list.
    // This returns a frozen set of strings.
    // This does not require the groups to exist.
    // 
    // This expects the first token to be the number of groups, then the groups follow that.
    const numberOfGroups = parseInt(dequeue(tokens));
    const groups = new Set();
    for (let i=0; i<numberOfGroups; i++) {
        groups.add(dequeue(tokens));
    }
    return Object.freeze(groups);
}

function parsePatternAndGetMatchingSymbols(tokens) {
    // Parses the given pattern and then finds and returns the ids of any symbols that match that in a frozen array.
    // 
    // The first token should be the number of include/exclude statements, and the following tokens should be the actual statements. These are processed in order.
    // These are the possible statements:
    //      `*` - take all `symbol-id`s.  
    //      `*(_modifier-id)+` - take all `symbol-id`s with the given `modifier-id`s.  
    //      `-` before a statement - to reject all the ones that match.  
    //      `symbol-id` - match a specific symbol. 
    //      `group-id` - match a specific group.
    //      `group-id(_modifier-id)+` - take all `symbol-id`s in the given `group-id` with the given `modifier-id`s. 
    const numberOfParts = parseInt(dequeue(tokens));
    const ids = new Array();
    for (let i=0; i<numberOfParts; i++) {
        dequeue(tokens);
    }
    return Object.freeze(ids);
}

// PUT_DEBUG_FOREVERLOOP_HERE

// First parse tokens into the arrays
parseSymbolSourceString(SYMBOLS_SOURCE);
// Process constraints
processConstraints();
