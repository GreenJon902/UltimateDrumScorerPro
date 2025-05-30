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
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.classList.add("score-component");

    const baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
    const timeSignatureNumerator = getScoreComponentTimeSignatureNumerator(componentID);  // Number of beats
    let x = 0;  // Current x-coord (of last beat)
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


        // Now we can draw the bars and dots ---
        
        // For bars we need two non-empty subdivisions, so we will store the last one, and draw from it to the current.
        // For dots we will just draw it after whatever the current subdivision is.
        let lastSubdivisionIndex = null;
        let path = "";
        for (let beatBaseSubdivisionIndex = 0; beatBaseSubdivisionIndex < baseSubdivisions; beatBaseSubdivisionIndex++) {
            const baseSubdivisionIndex = beatIndex * baseSubdivisions + beatBaseSubdivisionIndex;
            const furtherSubdivisionCount = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex);
            for (let furtherSubdivisionIndex = 0; furtherSubdivisionIndex<furtherSubdivisionCount; furtherSubdivisionIndex++) {
                if (getScoreComponentFurtherSubdivisionDrums(componentID, baseSubdivisionIndex, furtherSubdivisionIndex).length !== 0) {
                    const subdivisionIndex = (subdivisions / baseSubdivisions * beatBaseSubdivisionIndex) + (subdivisions / baseSubdivisions / furtherSubdivisionCount * furtherSubdivisionIndex);
                    
                    // We need to draw bars between pairs of adjacent non-empty subdivisions. If this is the first then we can ignore it.
                    if (lastSubdivisionIndex != null) {  // This is at least the second non-empty subdivision
                        // Collect the information
                        const lastBars = subdivisionBars[lastSubdivisionIndex];
                        const currentBars = subdivisionBars[subdivisionIndex];
                        const minBars = Math.min(lastBars, currentBars);

                        // Now draw the bars
                        // Full-bars:
                        for (let n=0; n<minBars; n++) {
                            path += "M" + x + " " + (n * 10) + " L" + (x + 50) + " " + (n * 10) + " ";
                        }
                        // Half-bars:
                        if (lastBars > minBars) {  // We need half-bars on the left
                            for (let n=minBars; n<lastBars; n++) {
                                path += "M" + x + " " + (n * 10) + " L" + (x + 20) + " " + (n * 10) + " ";
                            }
                        } else if (currentBars > minBars) {  // We need half-bars on the right
                            for (let n=minBars; n<currentBars; n++) {
                                path += "M" + (x + 30) + " " + (n * 10) + " L" + (x + 50) + " " + (n * 10) + " ";
                            }
                        }
                    }

                    x += 50;  // Bars are 50 wide so move x by 50 (or if no bars then move anyway)
                    
                    // Draw stem
                    path += "M" + x + " 0 L" + x + " 50 "

                    // Now we can draw dots
                    const dots = subdivisionDots[subdivisionIndex];
                    const y = 10 * subdivisionBars[subdivisionIndex];  // Put under lowest bar
                    for (let n=0; n<dots; n++) {
                        const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                        dot.setAttribute("r", "2");
                        dot.setAttribute("cx", x + 5 + 5 * n);  // Drawn under bars, assume less than 50px worth of dots, so we don't change x
                        dot.setAttribute("cy", y);
                        svg.appendChild(dot);
                    }
                    // Save this index for next time we find a non-empty subdivision
                    lastSubdivisionIndex = subdivisionIndex;
                }
            }
        }
        x += 50;  // Spacing between beats
        const bars = document.createElementNS("http://www.w3.org/2000/svg", "path");
        bars.setAttribute("d", path);
        bars.setAttribute("stroke", "black");
        bars.setAttribute("stroke-width", "3");
        svg.appendChild(bars);
        svg.setAttribute("height", "210");
        svg.setAttribute("width", x);
    }

    // Now add the svg to the document
    document.getElementById("component-container").appendChild(svg);
}
