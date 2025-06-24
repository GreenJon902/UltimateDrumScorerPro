var CURRENT_PROJECT;


export function loadJSON(data) {
    // Validates and loads the given data as the current project.
    // TODO: Validation
    CURRENT_PROJECT = data;
}

export function listScoreComponents() {
    // Return a list of all the score component IDs.
    return Object.keys(CURRENT_PROJECT["score-components"]);
}

function findUniqueID(prefix, object) {
    // Finds the first n (starting at 0) such that object[prefix + "-" + n] is undefined. It returns prefix + "-" + n.
    let idNo = 0;
    while (object[prefix + idNo] !== undefined) {
        idNo += 1;
    }
    const id = prefix + idNo;
    return id;

}

export function createNewScoreComponent() {
    // Create a new empty score-component and return it's component ID.
    
    // Find a new unique ID.
    const id = findUniqueID("score-component", CURRENT_PROJECT["score-components"]);

    // Create the new score component
    CURRENT_PROJECT["score-components"][id] = {
        "x": 0, "y": 0,
        "time-signature-denomenator": 4,
        "enabled-drums": ["snare", "kick"],
        "enabled-decorations": ["accent"],
        "rhythm-length-hint": 0,
        "score-content": [
            [{"drums": [], "decorations": []}],
            [{"drums": [], "decorations": []}],
            [{"drums": [], "decorations": []}],
            [{"drums": [], "decorations": []}]
        ]
    };

    return id;
}

export function getScoreComponentTimeSignatureNumerator(componentID) {
    // Returns the top of the time-signature of this component.
    return CURRENT_PROJECT["score-components"][componentID]["score-content"].length;
}

export function setScoreComponentTimeSignatureNumerator(componentID, value) {
    // Sets the top of the time-signature of this component.
    // This will chop the end off, or add to the end depending how it grows.
    const array = CURRENT_PROJECT["score-components"][componentID]["score-content"];
    while (array.length < value) {  // Grow it
        array.push([{"drums": [], "decorations": []}]);  // Add empty beat
    }
    while (array.length > value) {  // Shrink it
        array.pop();
    }
    CURRENT_PROJECT["score-components"][componentID]["score-content"] = array;  // I don't trust JS.
}

export function getScoreComponentTimeSignatureDenominator(componentID) {
    // Returns the bottom of the time-signature of this component.
    return CURRENT_PROJECT["score-components"][componentID]["time-signature-denomenator"];
}

export function setScoreComponentTimeSignatureDenominator(componentID, value) {
    // Sets the bottom of the time-signature of this component.
    CURRENT_PROJECT["score-components"][componentID]["time-signature-denomenator"] = value;
}

export function getScoreComponentEnabledDrums(componentID) {
    // Returns the IDs of the drums (including cymbals) that are being used by this component.
    // Not all of the returned IDs are necessarily used, but any that are used will definitely be here.
    return Array.from(CURRENT_PROJECT["score-components"][componentID]["enabled-drums"]);  // Clone array
}

export function getScoreComponentEnabledDecorations(componentID) {
    // Returns the IDs of the decorations that are being used by this component.
    // Not all of the returned IDs are necessarily used, but any that are used will definitely be here.
    return Array.from(CURRENT_PROJECT["score-components"][componentID]["enabled-decorations"]);  // Clone array
}

export function getComponentX(componentType, componentID) {
    // Returns the X coordinate of this component.
    // This is in mm from the left edge of the page.
    return CURRENT_PROJECT[componentType + "s"][componentID]["x"];
}

export function setComponentX(componentType, componentID, value) {
    // Sets the X coordinate of this component.
    // This is in mm from the left edge of the page.
    CURRENT_PROJECT[componentType + "s"][componentID]["x"] = value;
}

export function getComponentY(componentType, componentID) {
    // Returns the Y coordinate of this component.
    // This is in mm from the top edge of the page.
    return CURRENT_PROJECT[componentType + "s"][componentID]["y"];
}

export function setComponentY(componentType, componentID, value) {
    // Sets the Y coordinate of this component.
    // This is in mm from the top edge of the page.
    CURRENT_PROJECT[componentType + "s"][componentID]["y"] = value;
}

export function getScoreComponentRhythmLengthHint(componentID) {
	// Gets the hinted width of a full beat
    return CURRENT_PROJECT["score-components"][componentID]["rhythm-length-hint"];
}

export function setScoreComponentRhythmLengthHint(componentID, value) {
	// Sets the hinted width of a full beat
    CURRENT_PROJECT["score-components"][componentID]["rhythm-length-hint"] = value;
}

/*export function getScoreComponentLeftDecoration(componentID) {
	// Returns the ID of the left decoration (e.g. a repeat marker) of this component or null.
    return CURRENT_PROJECT["score-components"][componentID]["left-decoration"];
}

export function getScoreComponentRightDecoration(componentID) {
	// Returns the ID of the right decoration (e.g. a bar end sign) of this component or null.
    return CURRENT_PROJECT["score-components"][componentID]["right-decoration"];
}*/

export function getScoreComponentBeatSubdivisionCount(componentID, beatIndex) {
	// Returns the number of times a given beat is subdivided.
    return CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex].length;
}

export function setScoreComponentBeatSubdivisionCount(componentID, beatIndex, value) {
	// Sets the number of times a given beat is subdivided.
    // TODO: Grow and shrink this logically (don't just change the end) (e.g. If 4 to 2 then remove 1, 3.
    const array = CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex];
    while (array.length < value) {  // Grow it
        array.push({"drums": [], "decorations": []});  // Add empty subdivision
    }
    while (array.length > value) {  // Shrink it
        array.pop();
    }
    CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex] = array;  // I don't trust JS.
}

export function getScoreComponentBeatSubdivisionDrum(componentID, beatIndex, subdivisionIndex, drumID) {
	// Returns whether given drum (or cymbal) is being hit on a specific subdivision of a beat of a component.
    return CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex][subdivisionIndex]["drums"].includes(drumID);
}

export function getScoreComponentBeatSubdivisionDrums(componentID, beatIndex, subdivisionIndex) {
	// Returns an array of the IDs of the drums (and cymbals) being hit on a specific subdivision of beat of a component.
    return Array.from(CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex][subdivisionIndex]["drums"]);  // Duplicate array
}

export function setScoreComponentBeatSubdivisionDrum(componentID, beatIndex, subdivisionIndex, drumID, checked) {
	// Sets the IDs of the drums (and cymbals) that are being hit on a specific subdivision of a component.
	// If the ID is not in the array returned by getScoreComponentEnabledDrums then it will throw an error.
	if (!getScoreComponentEnabledDrums(componentID).includes(drumID)) {
		throw "Tried to remove a drum but id isn't enabled";
	}
    addRemoveFromArray(CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex][subdivisionIndex]["drums"], drumID, checked);
}



export function getScoreComponentBeatSubdivisionDecoration(componentID, beatIndex, subdivisionIndex, decorationID) {
	// Returns whether given drum (or cymbal) is being hit on a specific subdivision of a beat of a component.
    return CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex][subdivisionIndex]["decorations"].includes(decorationID);
}

export function getScoreComponentBeatSubdivisionDecorations(componentID, beatIndex, subdivisionIndex) {
	// Returns an array of the IDs of the decorations being hit on a specific subdivision of beat of a component.
    return Array.from(CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex][subdivisionIndex]["decorations"]);  // Duplicate array
}

export function setScoreComponentBeatSubdivisionDecoration(componentID, beatIndex, subdivisionIndex, decorationID, checked) {
	// Sets the IDs of the decoration that are being hit on a specific subdivision of a component.
	// If the ID is not in the array returned by getScoreComponentEnabledDecoration then it will throw an error.
	if (!getScoreComponentEnabledDecorations(componentID).includes(decorationID)) {
		throw "Tried to remove a drum but id isn't enabled";
	}
    addRemoveFromArray(CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex][subdivisionIndex]["decorations"], decorationID, checked);
}



function addRemoveFromArray(array, item, shouldContain) {
    // If shouldContain is true then this function makes sure item is in the given array, otherwise all instances of it are removed from the array
    if (shouldContain && !array.includes(item)) {
        array.push(item);
    } else if (!shouldContain) {
        while (array.includes(item)) {  // Loop incase there are multiple occurances
            const index = array.indexOf(item);
            array.splice(index, 1);  // Remove from the array
        }
    }

}

export function listTextComponents() {
    // Returns an array of all the text component IDs
    return Object.keys(CURRENT_PROJECT["text-components"]);
}

export function createNewTextComponent() {
    // Create a new empty text-component and return s component ID.
    const id = findUniqueID("text-component", CURRENT_PROJECT["text-components"]);
    CURRENT_PROJECT["text-components"][id] = {
        "x": 0, "y": 0,
        "font-size": 3,
        "text-content": ""
    };
    return id;
}

export function getTextComponentFontSize(componentID) {
    return CURRENT_PROJECT["text-components"][componentID]["font-size"];
}
export function setTextComponentFontSize(componentID, newFontSize) {
    CURRENT_PROJECT["text-components"][componentID]["font-size"] = newFontSize;
}
export function getTextComponentTextContent(componentID) {
    return CURRENT_PROJECT["text-components"][componentID]["text-content"];
}
export function setTextComponentTextContent(componentID, newTextContent) {
    CURRENT_PROJECT["text-components"][componentID]["text-content"] = newTextContent;
}



