import {getScoreComponentBaseSubdivisions, getScoreComponentFurtherSubdivisionCount, getScoreComponentFurtherSubdivisionDrums, getScoreComponentTimeSignatureDenominator, getScoreComponentTimeSignatureNumerator} from "./files.js";

function calculateValuesBarsAndDots(duration, subdivisions, subdivisionValues, subdivisionBars, subdivisionDots) {
    // Calculates the value, number of bars and number of dots that a note with duration/subdivision for a beat would have.
    // This function will add duration occurances of these to each array.
    const v = duration;
    const l = Math.ceil(Math.log2(subdivisions/v));
    const d = Math.log2(subdivisions/(subdivisions-v*2**(l-1))) - 1;
    subdivisionValues.push(...Array(duration).fill(v)); // We want to add for all the gaps after too.
    subdivisionBars.push(...Array(duration).fill(l)); // We want to add for all the gaps after too.
    subdivisionDots.push(...Array(duration).fill(d)); // We want to add for all the gaps after too.

}


export function renderComponent(componentType, componentID) {
    // Render the given component. If it already exists then it will be removed.
    
    // First delete it if it already exists
    let old = document.getElementById(componentType + "_" + componentID);
    if (old !== null) {
        document.remove();
    }

    if (componentType !== "score-component") throw "Not Implemented";
    
    // Now let's render it
    const svg = document.createElement("svg");
    svg.classList.add("score-component");

    const baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
    const timeSignatureNumerator = getScoreComponentTimeSignatureNumerator(componentID);  // Number of beats
    for (let beatIndex = 0; beatIndex < timeSignatureNumerator; beatIndex++) {
        // Bar calculations ---
        
        // We store it as a mix of subdivisions, but we need to have only one per beat that can account for all.
        // The easiest way to do this is to find the product of all the subdivisions 
        let subdivisions = baseSubdivisions;
        for (let beatBaseSubdivisionIndex = 0; beatBaseSubdivisionIndex < baseSubdivisions; beatBaseSubdivisionIndex++) {
            const baseSubdivisionIndex = beatIndex * baseSubdivisions + beatBaseSubdivisionIndex; 
            subdivisions *= getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex);
       }

        
        // Now we calculate some numbers to do with each subdivision
        
        let currentEmpty = 0;
        const subdivisionValues = [];  // The number of subdivisions that follow a non-empty subdivision before we reach another non-empty subdivision. If the index is an empty-subdivision, it gives the value for the last non-empty subdivision before the current index  
        const subdivisionBars = [];  // Same rules as subdivisionValues, but this stores the number of bars attached to a given subdivision.
        const subdivisionDots = [];  // Same rules as subdivisionValues, but this stores the number of dots following a given subdivision. 
        let isFirst = true;
        for (let beatBaseSubdivisionIndex = 0; beatBaseSubdivisionIndex < baseSubdivisions; beatBaseSubdivisionIndex++) {
            const baseSubdivisionIndex = beatIndex * baseSubdivisions + beatBaseSubdivisionIndex;
            const furtherSubdivisionCount = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex);
            for (let furtherSubdivisionIndex = 0; furtherSubdivisionIndex<furtherSubdivisionCount; furtherSubdivisionIndex++) {
                if (getScoreComponentFurtherSubdivisionDrums(componentID, baseSubdivisionIndex, furtherSubdivisionIndex).length !== 0) {
                    if (isFirst) {
                        isFirst = false;  // Don't add the first one yet, we'll add this later once we know how much empty space follows it.
                    } else {
                        calculateValuesBarsAndDots(currentEmpty, subdivisions, subdivisionValues, subdivisionBars, subdivisionDots)                        
                    }
                    currentEmpty = 0;
                }
                currentEmpty += subdivisions / baseSubdivisions / furtherSubdivisionCount;
            }
        }
         
        // We are always one behind so we need to add the last one.
        calculateValuesBarsAndDots(currentEmpty, subdivisions, subdivisionValues, subdivisionBars, subdivisionDots)                        


        console.log(subdivisionValues, subdivisionBars, subdivisionDots);
        
       /* const subdivisionValues = [];

        let baseSubdivisionIndex = beatIndex * baseSubdivisions;
        let furtherSubdivisionCount = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex);
        let furtherSubdivisionIndex = 0;

        do {
            // Get empty space till next subdivision with drums in it
            let emptySubdivisionCount = subdivisions / baseSubdivisions / furtherSubdivisionCount; // Take account of the first subdivision.
            while (getScoreComponentFurtherSubdivisionDrums(componentID, baseSubdivisionIndex, furtherSubdivisionIndex).length === 0) {
                furtherSubdivisionIndex++;
                if (furtherSubdivisionIndex >= furtherSubdivisionCount) {
                    furtherSubdivisionIndex = 0;
                    baseSubdivisionIndex += 1;
                    furtherSubdivisionCount = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisions);
                }
                emptySubdivisionCount += subdivisions / baseSubdivisions / furtherSubdivisionCount;
            }
            subdivisionValues.push(...Array(emptySubdivisionCount).fill(emptySubdivisionCount));  // Add multiple
            furtherSubdivisionIndex++;
            if (furtherSubdivisionIndex >= furtherSubdivisionCount) {
                furtherSubdivisionIndex = 0;
                baseSubdivisionIndex += 1;
                furtherSubdivisionCount = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisions);
            }
        } while (baseSubdivisionIndex < (beatIndex+1)*subdivisions);

        return;
        let emptySubdivisionCount = 0;
        let rest = 0;  // The number of subdivisions taken up by rests at the start of the bar

        while (beatBaseSubdivisionIndex < baseSubdivisions) {
            const baseSubdivisionIndex = beatIndex * baseSubdivisions + beatBaseSubdivisionIndex;
            const furtherSubdivisionCount = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex);
            const isNotEmpty = getScoreComponentFurtherSubdivisionDrums(componentID, baseSubdivisionIndex, furtherSubdivisionIndex).length !== 0;

            const isRest = subdivisionValues.length == 0 && beatBaseSubdivisionIndex != 0 && furtherSubdivisionIndex != 0;  // Is this / is there a rest
            if (isNotEmpty && isRest) {  // Is a rest
                rest = emptySubdivisionCount;
                subdivisionValues.push(...Array(emptySubdivisionCount).fill(0));  // No bars over rests
                emptySubdivisionCount = 0;
            } else if (isNotEmpty) {  // Not a rest 
                emptySubdivisionCount += subdivisions / baseSubdivisions / furtherSubdivisionCount;  // This is how much space this note takes up.
subdivisionValues.push(...Array(emptySubdivisionCount).fill(emptySubdivisionCount));  // Add length of last.
                emptySubdivisionCount = 0;
            } else {  // Empty so just carry on
                emptySubdivisionCount += subdivisions / baseSubdivisions / furtherSubdivisionCount;  // This is how much space this note takes up.
            }

            furtherSubdivisionIndex++;
            if (furtherSubdivisionIndex >= furtherSubdivisionCount) {
                furtherSubdivisionIndex = 0;
                beatBaseSubdivisionIndex += 1;
            }
        }
        console.log(subdivisionValues);*/
    }

    // Now add the svg to the document
    document.getElementById("component-container").appendChild(svg);
}
