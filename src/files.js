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
    return Array.from(CURRENT_PROJECT["score-components"][componentID]["enabled-drums"]);  // Clone array
}

export function getScoreComponentEnabledDecorations(componentID) {
    // Returns the IDs of the decorations (e.g. accents) that are being used by this component.
    return Array.from(CURRENT_PROJECT["score-components"][componentID]["enabled-decorations"]);  // Clone array
}

export function getScoreComponentX(componentID) {
    // Returns the X coordinate of this score component.
    // The returned value multiplied by the parent's width is the x-coordinate.
    return CURRENT_PROJECT["score-components"][componentID]["x"];
}

export function setScoreComponentX(componentID, value) {
    // Sets the X coordinate of this score component.
    // The value multiplied by the parent's width is the x-coordinate.
    CURRENT_PROJECT["score-components"][componentID]["x"] = value;
}

export function getScoreComponentY(componentID) {
    // Returns the Y coordinate of this score component.
    // The returned value multiplied by the parent's height is the y-coordinate.
    return CURRENT_PROJECT["score-components"][componentID]["y"];
}


export function setScoreComponentY(componentID, value) {
    // Sets the Y coordinate of this score component.
    // The returned value multiplied by the parent's height is the y-coordinate.
    CURRENT_PROJECT["score-components"][componentID]["y"] = value;
}

export function getScoreComponentLeftDecoration(componentID) {
	// Returns the ID of the left decoration (e.g. a repeat marker) of this component or null.
    return CURRENT_PROJECT["score-components"][componentID]["left-decoration"];
}

export function getScoreComponentRightDecoration(componentID) {
	// Returns the ID of the right decoration (e.g. a bar end sign) of this component or null.
    return CURRENT_PROJECT["score-components"][componentID]["right-decoration"];
}

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
	// Sets the IDs of the drums (and cymbals) that are being hit on a specific further-subdivision of subdivision of a component.
    addRemoveFromArray(CURRENT_PROJECT["score-components"][componentID]["score-content"][beatIndex][subdivisionIndex]["drums"], drumID, checked);
}

/*
export function getScoreComponentFurtherSubdivisionDecoration(componentID, baseSubdivisionIndex, furtherSubdivisionIndex, decorationID) {
	// Returns whether a given decoration is being used on a specific further-subdivision of subdivision of a component.
    return CURRENT_PROJECT["score-components"][componentID]["score-content"][baseSubdivisionIndex][furtherSubdivisionIndex]["decorations"].includes(decorationID);
}

export function setScoreComponentFurtherSubdivisionDecoration(componentID, baseSubdivisionIndex, furtherSubdivisionIndex, decorationID, checked) {
	// Sets the IDs of the decorations that are being used on a specific further-subdivision of subdivision of a component.
    addRemoveFromArray(CURRENT_PROJECT["score-components"][componentID]["score-content"][baseSubdivisionIndex][furtherSubdivisionIndex]["decorations"], decorationID, checked);
}*/

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

