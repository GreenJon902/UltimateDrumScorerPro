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

function ensureSymbolIdPart(string) {
    // Ensures the given string is formatted as a valid base-symbol-id/part-symbol-id/modifier-id: "some-id".
    // If it is correct then it is returned, otherwise an error is thrown.
    return ensureStringIsLowerAndGiven(string, "-");
}
const ensureBaseSymbolId = ensureSymbolIdPart;
const ensurePartSymbolId = ensureSymbolIdPart;
const ensureModifierId = ensureSymbolIdPart;

function ensureSymbolOrGroupId(string) {
    // Ensures the given string is formatted as a valid symbol-id/group-id: "some-id_some-modifier"/"some-id".
    // If it is correct then it is returned, otherwise an error is thrown.
    return ensureStringIsLowerAndGiven(string, "-", "_");
}

function ensureExists(id, parseData) {
    // Ensures the given id (symbol-id or group-id) exists.
    // If it does then the id is returned, otherwise an error is thrown.
    if (!(parseData.groups.has(id) || id in parseData.symbols)) throw "Given id not in parse data";
    return id;
}

function ensureDoesNotExist(id, parseData) {
    // Ensures the given id (symbol-id or group-id) does not exist.
    // If it does then an error is thrown, otherwise it is returned.
    if (parseData.groups.has(id) || id in parseData.symbols) throw "Given id already in parse data";
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
    // 
    // This returns a parseData object (see creation for doc).
    
    const parseData = {
        parts: {},  // {part-symbol-id: {instructions: Array<SvgInstruction>}}
        symbols: {},  // {symbol-id: {sizeLeft: float, sizeUp: float, sizeRight: float, sizeDown: float, instructions: Array<SvgInstruction>, groups: Array<group-id>}}
        constraints: new Set(),  // {topId: (symbol|group)-id, bottomId: (symbol|group)-id, distance: float}
        groups: new Set()  // group-id
    }

    const tokens = symbolsSource.split(",");
    while (tokens.length != 0) {
        // Figure out which specific parse function to call, and then call it
        const action = dequeue(tokens);
        const actionFunction = {  // Select which function we want to call
            "new_base": parseNewBase,
            "new_part": parseNewPart,
            "modifier_explicit": parseModifierExplicit,
            "modifier_auto": parseModifierAuto,
            "head_constraint": parseHeadConstraint
        }[action];
        if (actionFunction === undefined) throw "Unknown action " + action;
        actionFunction(tokens, parseData);  // Functions update tokens array for us
    }
    
    return parseData;
}

function parseNewBase(tokens, parseData) {
    // Parse a new_base action from the array of tokens. 
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this base-symbol-id,size-left,size-up,size-right,size-down,<instructions>,<groups>.
    const baseSymbolId = ensureBaseSymbolId(dequeue(tokens), parseData);
    const sizeLeft = parseFloat(dequeue(tokens));
    const sizeUp = parseFloat(dequeue(tokens));
    const sizeRight = parseFloat(dequeue(tokens));
    const sizeDown = parseFloat(dequeue(tokens));
    const instructions = parseInstructions(tokens, parseData);
    const groups = parseGroups(tokens);
    
    parseData.symbols[baseSymbolId] = {sizeLeft: sizeLeft, sizeUp: sizeUp, sizeRight: sizeRight, sizeDown: sizeDown, instructions: instructions, groups: groups};
    groups.forEach(group => parseData.groups.add(group));
}

function parseNewPart(tokens, parseData) {
    // Parse a new_part action from the array of tokens. 
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this base-symbol-id,<instructions>.
    const partSymbolId = ensureDoesNotExist(ensurePartSymbolId(dequeue(tokens)), parseData);
    const instructions = parseInstructions(tokens, parseData);
    
    parseData.parts[partSymbolId] = {instructions: instructions}
}

function parseModifierExplicit(tokens, parseData) {
    // Parse a modifier_explicit action from the array of tokens.
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this base_symbol-id(_modifier-id)+,size-left,size-up,size-right,size-down,<instructions>,<groups>.
    const symbolId = ensureDoesNotExist(dequeue(tokens), parseData);
    const {base: baseSymbolId, modifiers: modifierIds} = splitSymbolId(symbolId);
    ensureExists(baseSymbolId, parseData);
    if (modifierIds.length === 0) throw "Expected at least one modifierId";
    const sizeLeft = parseFloat(dequeue(tokens));
    const sizeUp = parseFloat(dequeue(tokens));
    const sizeRight = parseFloat(dequeue(tokens));
    const sizeDown = parseFloat(dequeue(tokens));
    const instructions = parseInstructions(tokens, parseData);
    const groups = parseGroups(tokens);
    
    parseData.symbols[symbolId] = {sizeLeft: sizeLeft, sizeUp: sizeUp, sizeRight: sizeRight, sizeDown: sizeDown, instructions: instructions, groups: groups};
    groups.forEach(group => parseData.groups.add(group));
}

function parseModifierAuto(tokens, parseData) {
    // Parse a modifier_auto action from the array of tokens.
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this modifier-id,<pattern>,(+detla,>min)size-left,(+detla,>min)size-right,(+detla,>min)size-up,(+detla,>min)size-down,min-width,min-height,<instructions>,<groups>.
    // 
    // Created groups have the id <old-symbol-id>_<modifier-id> and inherit groups+instructions from the old symbol (as well as the new groups+instructions).
    const modifierId = ensureModifierId(dequeue(tokens), parseData);  // We don't mind if the modifierId already exists, if we want to apply it to a symbolId then we can check then
    const symbolIds = parsePatternAndGetMatchingSymbols(tokens, parseData);
    if (symbolIds.length === 0) throw "Matched no symbolIds which this algorithm is not built for";
    const {delta: sizeLeftDelta, min: minSizeLeft} = parseModifierSizeChanger(dequeue(tokens));
    const {delta: sizeUpDelta, min: minSizeUp} = parseModifierSizeChanger(dequeue(tokens));
    const {delta: sizeRightDelta, min: minSizeRight} = parseModifierSizeChanger(dequeue(tokens));
    const {delta: sizeDownDelta, min: minSizeDown} = parseModifierSizeChanger(dequeue(tokens));
    const minWidth = parseFloat(dequeue(tokens));
    const minHeight = parseFloat(dequeue(tokens));
    const tokensCopy = Array.from(tokens);  // Clone array at this point, we will use it later
    parseInstructions(tokens, parseData, Array.from(symbolIds)[0]);  // Just skip instructions, we will reparse later
    const extraGroups = parseGroups(tokens);
    
    // Each of the symbolIds needs to be modified
    symbolIds.forEach(parentSymbolId => {
        const parentSymbol = parseData.symbols[parentSymbolId];
        const modifiedSymbolId = parentSymbolId + "_" + modifierId;

        // For this specific symbol, get the instructions
        // We need to do it like this as transform anchors may be different for each symbolId
        const instructions = parseInstructions(Array.from(tokensCopy), parseData, parentSymbolId);  // We don't want it to modify our copy of tokens, as we may still need to loop through it more
            // This will add the instructions from parentSymbolId too
        
        // Figure out correct size for new symbol
        const parentCenterX = -parentSymbol.sizeLeft / 2 + parentSymbol.sizeRight / 2;
        const parentCenterY = -parentSymbol.sizeUp / 2 + parentSymbol.sizeDown / 2;
        const sizeLeft = Math.max(parentSymbol.sizeLeft + sizeLeftDelta, minSizeLeft, minWidth / 2 - parentCenterX);
        const sizeRight = Math.max(parentSymbol.sizeRight + sizeRightDelta, minSizeUp, minWidth / 2 + parentCenterX);
        const sizeUp = Math.max(parentSymbol.sizeUp + sizeUpDelta, minSizeRight, minHeight / 2 - parentCenterY);
        const sizeDown = Math.max(parentSymbol.sizeDown + sizeDownDelta, minSizeDown, minHeight / 2 + parentCenterY);
        
        // New groups set
        const groups = parentSymbol.groups.union(extraGroups);

        // Add it if it doesn't already exist
        ensureDoesNotExist(modifiedSymbolId, parseData);
        parseData.symbols[modifiedSymbolId] = {sizeLeft: sizeLeft, sizeUp: sizeUp, sizeRight: sizeRight, sizeDown: sizeDown, instructions: instructions, groups: groups};
        groups.forEach(group => parseData.groups.add(group));
    });
}

function parseHeadConstraint(tokens, parseData) {
    // Parse a head_constraint action from the array of tokens.
    // This removes the tokens from the given array.
    // This expects the action ID to already have been removed.
    // 
    // The following tokens should be like this top-(symbol|group)-id,bottom-(symbol|group)-id,distance.
    const topId = ensureExists(ensureSymbolOrGroupId(dequeue(tokens)), parseData);
    const bottomId = ensureExists(ensureSymbolOrGroupId(dequeue(tokens)), parseData);
    const distance = parseInt(dequeue(tokens));
    
    parseData.constraints.add({topId: topId, bottomId: bottomId, distance: distance});
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
    }
}

function parseInstructions(tokens, parseData, parentSymbolId=null) {
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
    //      `push-anchored-transform`,`horizAnchor`,`vertAnchor` - This is only valid when parentSymbolId is not null. horizAnchor can be left,middle,right, vertAnchor can be top,middle,bottom. The anchors are relative to the size of the parent.
    // 
    // When parentSymbolId is given, then the instructions from that symbol will be put before the instructions from tokens.
    
    const instructions = new Array();  // Array of generated instructions
    // Handle instructions from parent
    if (parentSymbolId !== null) {
        instructions.push(...parseData.symbols[parentSymbolId].instructions);
    }
    // Handle instructions from tokens   
    const numberOfInstruction = parseInt(dequeue(tokens));
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
                if (parentSymbolId === null) throw "Push-anchored-transform cannot be used when parentSymbolId is null";
                // Convert anchored transform to normal transform:
                
                const parent = parseData.symbols[parentSymbolId];
                // Find amounts we need to translate by
                const transX = {
                    left: -parent.sizeLeft,
                    middle: -parent.sizeLeft / 2 + parent.sizeRight / 2,
                    right: parent.sizeRight
                }[dequeue(tokens)];
                const transY = {
                    top: -parent.sizeUp,
                    middle: -parent.sizeUp / 2 + parent.sizeDown / 2,
                    bottom: parent.sizeDown
                }[dequeue(tokens)];
                // Now add it to the instructions
                instructions.push(new SvgInstruction(SvgInstruction.PUSH_TRANSFORM, `transform(${transX} ${transY})`));
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

function matchSymbolIds(toMatch, parseData) {
    // Returns symbol names based on toMatch. "*" is all, otherwise pass a symbol or group id.
    let referingIds;
    if (toMatch === "*") {
        referingIds = new Set(Object.keys(parseData.symbols));
    } else if (parseData.groups.has(toMatch)) {
        referingIds = new Set(Object.keys(parseData.symbols)
            .filter(id => parseData.symbols[id].groups.has(toMatch)));
    } else if (toMatch in parseData.symbols) {
        referingIds = new Set([toMatch]);
    } else {
        throw "Could not find what toMatch is refering to";
    }
    return referingIds;
}

function parsePatternAndGetMatchingSymbols(tokens, parseData) {
    // Parses the given pattern and then finds and returns the ids of any symbols that match that in a frozen array.
    // 
    // The first token should be the number of include/exclude statements, and the following tokens should be the actual statements. These are processed in order.
    // These are the possible statements:
    //      `*` - take all `symbol-id`s.  
    //      `-` before a statement - to reject all the ones that match.  
    //      `symbol-id` - match a specific symbol. 
    //      `group-id` - match a specific group.
    const numberOfParts = parseInt(dequeue(tokens));
    let ids = new Set();
    for (let i=0; i<numberOfParts; i++) {
        const statement = dequeue(tokens);
        const isRemoving = statement[0] === "-";
        const toMatch = statement.slice((isRemoving) ? 1 : 0);  // Remove "-" from start of statement
        
        // First collect all ids we are refering too
        const referingIds = matchSymbolIds(toMatch, parseData);
        
        // Handle our ids
        if (isRemoving) {
            ids = ids.difference(referingIds);   
        } else {
            ids = ids.union(referingIds);
        }
    }
    return Object.freeze(ids);
}

function calculateFullDrumOrder(parseData) {
    // Using the constraint data, figure out which drum symbols need to be drawn over which symbols.
    
    // Extract the constraint data to get direct relations beetween symbols
    const symbolOverSymbols = {};  // {symbol-id: Array<symbol-ids-which-are-below>}
    Object.keys(parseData.symbols).forEach(id => { symbolOverSymbols[id] = new Set(); });  // Create set for each symbol
    parseData.constraints.forEach(constraint => {  // Add direct constraints
        const topIds = matchSymbolIds(constraint.topId, parseData);
        const bottomIds = matchSymbolIds(constraint.bottomId, parseData);
        topIds.forEach(topId => {
            symbolOverSymbols[topId].add(...bottomIds);  // Add bottomIds to all topIds
        });
    });
    
    // Check that we have no "loops" - a is over b but b is over a
    Object.keys(parseData.symbols).forEach(id1 => Object.keys(parseData.symbols).forEach(id2 => {
        if (symbolOverSymbols[id1].has(id2) && symbolOverSymbols[id2].has(id1)) throw "Circular constraint";
    }));
    
    // Actually order our symbolIds
    // We do this by iteratively looking at the data set, if all the symbolIds that need to be below a given symbol are there, then we can add that symbol
    const symbolIds = Array.from(Object.keys(parseData.symbols));
    const symbolIdCount = symbolIds.length;  // Take this now as the array reduces in size
    const fullOrder = new Array();
    while (fullOrder.length < symbolIdCount) {
        for (let i=0; i<symbolIds.length; i++) {
            const symbolId = symbolIds[i];
            if (symbolOverSymbols[symbolId].difference(new Set(fullOrder)).size === 0) {  // Are all requisites for symbolId in fullOrder?
                // Yes to we can move symbolId
                fullOrder.push(symbolId);
                symbolIds.splice(i,1);  // Remove from old array so faster
                i--;
            }
        }
    }
    
    // Reverse array so bottom is at end of array
    fullOrder.reverse();

    return Object.freeze(fullOrder);
}

// PUT_DEBUG_FOREVERLOOP_HERE

// First parse tokens into the arrays
const parseData = parseSymbolSourceString(SYMBOLS_SOURCE);
// Process constraints
const fullDrumOrder = calculateFullDrumOrder(parseData);

// Create functions to export -------------------------------------
export class DrumSymbols {
    static getFullOrder() {
        // Returns an array containing the order in which symbols should be drawn where index 0 is the top.
        return fullDrumOrder;  // This is already frozen
    }

    static isAbove(symbolId1, symbolId2) {
        // True if symbolId2 should be drawn above symbolId1.
        return fullOrder.indexOf(symbolId1) < fullOrder.indexOf(symbolId2);
    }

    static getMinDistance(symbolId1, symbolId2) {
        // Get's the minimum distance between the anchors of the given symbols.
        // If symbolId2 should be drawn above symbolId1 then an error is thrown.
        // This will not return indirect constraints (e.g. if a is 10 from b and b is 5 from c, it will not say a is 15 from c (unless you add that externally)).
        if (isSymbolAbove(symbolId2, symbolId1)) throw "SymbolId2 should be below symbolId1"
        
        // Find the maximum distance from all the (relevant) constraints
        const minDistance = Math.max(...Array.from(parseData.constraints).map(constraint => {
            if (!(matchSymbolIds(constraint.topId, parseData).has(symbolId1) && matchSymbolIds(constraint.bottomId, parseData).has(symbolId2))) {  // If this constraint doesn't refer to both of the given symbols
                return 0;  // 0 as no constraint
            } else {
                return constraint.distance; 
            }
        }));
        
        return minDistance;
    }

    static getInstructions(symbolId) {
        // Returns an array of SvgInstruction for the given symbol.
        return parseData.symbols[symbolId].instructions;
    }

    static getSizeLeft(symbolId) {
        // Returns the sizeLeft for the given symbol. This is the horizontal distance to the left of the anchor that this symbol takes up.
        return parseData.symbols[symbolId].sizeLeft;
    }

    static getSizeRight(symbolId) {
        // Returns the sizeRight for the given symbol. This is the horizontal distance to the right of the anchor that this symbol takes up.
        return parseData.symbols[symbolId].sizeRight;
    }

    static getSizeUp(symbolId) {
        // Returns the sizeUp for the given symbol. This is the vertical distance above the anchor that this symbol takes up.
        return parseData.symbols[symbolId].sizeUp;
    }

    static getSizeDown(symbolId) {
        // Returns the sizeDown for the given symbol. This is the vertical distance below the anchor that this symbol takes up.
        return parseData.symbols[symbolId].sizeDown;
    }
}
