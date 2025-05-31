import {setEditComponent} from "./editor.js";
import {getScoreComponentBaseSubdivisions, getScoreComponentFurtherSubdivisionCount, getScoreComponentFurtherSubdivisionDrums, getScoreComponentTimeSignatureDenominator, getScoreComponentTimeSignatureNumerator, getScoreComponentX, getScoreComponentY, setScoreComponentX, setScoreComponentY} from "./files.js";

function calculateValuesBeamsAndDots(duration, subdivisions, subdivisionValues, subdivisionBeams, subdivisionDots) {
    // Calculates the value, number of beams and number of dots that a note with duration/subdivision for a beat would have.
    // This function will add duration occurances of these to each array.
    const v = duration;
    const l = Math.ceil(Math.log2(subdivisions/v));
    const d = Math.log2(subdivisions/(subdivisions-v*2**(l-1))) - 1;
    subdivisionValues.push(...Array(duration).fill(v)); // We want to add for all the gaps after too.
    subdivisionBeams.push(...Array(duration).fill(l)); // We want to add for all the gaps after too.
    subdivisionDots.push(...Array(duration).fill(d)); // We want to add for all the gaps after too.

}


function calculateActualSubdivisionIndex(subdivisions, componentID, base, further) {
    // Convert a base and further subdivision index to an index in a subdivision length of subdivisions.
    // This returns the subdivision relative to the start of the beat, but base should be relative to the start of the component.
    const furtherCount = getScoreComponentFurtherSubdivisionCount(componentID, base);
    const baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
    return (subdivisions / baseSubdivisions * (base % baseSubdivisions)) + (subdivisions / baseSubdivisions / furtherCount * further);
}


function drawDots(svg, x, y, dotNumber) {
    // Draws dotNumber dots starting at x, y in svg.
    
    for (let n=0; n<dotNumber; n++) {
        const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        dot.setAttribute("r", "2");
        dot.setAttribute("cx", x + 5 * n);
        dot.setAttribute("cy", y);
        svg.appendChild(dot);
    }
}

export function renderComponent(componentType, componentID) {
    // Render the given component. If it already exists then it will be removed.
    
    // First delete it if it already exists
    let old = document.getElementById(componentType + "_" + componentID);
    if (old !== null) {
        old.remove();
    }

    if (componentType !== "score-component") throw "Not Implemented";
    
    // Now let's render it
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.classList.add("score-component");
    svg.setAttribute("id", componentType + "_" + componentID);  // So we can refer to it if we need to

    const baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
    const timeSignatureNumerator = getScoreComponentTimeSignatureNumerator(componentID);  // Number of beats
    let x = 0;  // Current x-coord (of last beat)
    for (let beatIndex = 0; beatIndex < timeSignatureNumerator; beatIndex++) {
        // Beam calculations ---
        
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
        const subdivisionBeams = [];  // Same rules as subdivisionValues, but this stores the number of beams attached to a given subdivision.
        const subdivisionDots = [];  // Same rules as subdivisionValues, but this stores the number of dots following a given subdivision. 
        const nonEmptySubdivisionBaseIndexes = [];  // Index of each non-empty subdivision (this will be repeated for each non-empty further subdivision
        const nonEmptySubdivisionFurtherIndexes = [];  // Same as above
        let isFirst = true;
        for (let beatBaseSubdivisionIndex = 0; beatBaseSubdivisionIndex < baseSubdivisions; beatBaseSubdivisionIndex++) {
            const baseSubdivisionIndex = beatIndex * baseSubdivisions + beatBaseSubdivisionIndex;
            const furtherSubdivisionCount = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex);
            for (let furtherSubdivisionIndex = 0; furtherSubdivisionIndex<furtherSubdivisionCount; furtherSubdivisionIndex++) {
                if (getScoreComponentFurtherSubdivisionDrums(componentID, baseSubdivisionIndex, furtherSubdivisionIndex).length !== 0) {
                    nonEmptySubdivisionBaseIndexes.push(baseSubdivisionIndex);
                    nonEmptySubdivisionFurtherIndexes.push(furtherSubdivisionIndex);

                    // While we are supposed to be adding after we found the empty space after the one we're adding. We can add what's before as it's useful for rest data
                    calculateValuesBeamsAndDots(currentEmpty, subdivisions, subdivisionValues, subdivisionBeams, subdivisionDots);                        
                    currentEmpty = 0;
                }
                currentEmpty += subdivisions / baseSubdivisions / furtherSubdivisionCount;
            }
        }
         
        // We are always one behind so we need to add the last one.
        calculateValuesBeamsAndDots(currentEmpty, subdivisions, subdivisionValues, subdivisionBeams, subdivisionDots)                        

        // Path object we can reuse:
        let path = "";

        // Check if we need to draw a rest (we handle crotchet rests later so ignore those)
        if (nonEmptySubdivisionBaseIndexes.length > 0 && (nonEmptySubdivisionBaseIndexes[0] !== 0 || nonEmptySubdivisionFurtherIndexes[0] !== 0)) {
            const restTicks = subdivisionBeams[0];
            const restDots = subdivisionDots[0];

            path += "M" + x + " 30 L" + (x + restTicks * 5 + 2.5) + " " + (27.5 - restTicks * 5) + " ";
            for (let n=0; n<restTicks; n++) {
                path += "M" + (x + n * 5 + 5) + " " + (25 - n * 5) + " L" + (x + n * 5) + " " + (20 - n * 5) + " ";
            }
            x += 10;
            drawDots(svg, x, "27.5", restDots);
            x += 5 * restTicks;


        }

        // Now we can draw the beams and dots ---
        

        // If there's only one non-empty then draw a stem with a flag, otherwise draw beams. Draw crotchet rest if no non-empty
        if (nonEmptySubdivisionBaseIndexes.length == 0) {
            path += "M" + x + " 0 L" + (x + 5) + " 10 L" + x + " 15 L" + (x + 5) + " 20 ";
        } else if (nonEmptySubdivisionBaseIndexes.length == 1) {
            const subdivisionIndex = calculateActualSubdivisionIndex(subdivisions, componentID, nonEmptySubdivisionBaseIndexes[0], nonEmptySubdivisionFurtherIndexes[0]);
            
            // Draw stem
            path += "M" + x + " 0 L" + x + " 50 "

            // Draw flags
            let y = 0;
            for (let n=0; n < subdivisionBeams[subdivisionIndex]; n++) {
                path += "M" + x + " " + y + " L" + (x + 10) + " " + (y + 10) + " ";
                y += 5;
            }
            y += 10;
            
            // Draw dots
            const dots = subdivisionDots[subdivisionIndex];
            drawDots(svg, x + 5, y, dots); // Drawn under flags, assume less than 50px worth of dots, so we don't change x


        } else {
        
            // For beams we need two non-empty subdivisions, so we will store the last one, and draw from it to the current.
            // For dots we will just draw it after whatever the current subdivision is.
            for (let nonEmptyIndex=0; nonEmptyIndex<nonEmptySubdivisionBaseIndexes.length; nonEmptyIndex++) {
                const currentSubdivisionIndex = calculateActualSubdivisionIndex(subdivisions, componentID, nonEmptySubdivisionBaseIndexes[nonEmptyIndex], nonEmptySubdivisionFurtherIndexes[nonEmptyIndex]);

                // We need to draw beams between pairs of adjacent non-empty subdivisions. So if this is the first then we can ignore it.
                if (nonEmptyIndex != 0) {  
                    // Collect the information
                    const lastSubdivisionIndex = calculateActualSubdivisionIndex(subdivisions, componentID, nonEmptySubdivisionBaseIndexes[nonEmptyIndex-1], nonEmptySubdivisionFurtherIndexes[nonEmptyIndex-1]);
                    const lastBeams = subdivisionBeams[lastSubdivisionIndex];
                    const currentBeams = subdivisionBeams[currentSubdivisionIndex];
                    const minBeams = Math.min(lastBeams, currentBeams);

                    // Now draw the beams
                    // Full-beams:
                    for (let n=0; n<minBeams; n++) {
                        path += "M" + x + " " + (n * 10) + " L" + (x + 50) + " " + (n * 10) + " ";
                    }
                    // Half-beams:
                    // We need half-beams iff a stem needs more beams than are connected to it (on either side).
                    if (lastBeams > minBeams) {  // We might need half-beams on the left
                        // Check if it already has enough beams on the other side
                        let needsHalfBeams = true;
                        if (nonEmptyIndex > 1) {  // If last is the first then it cannot have any on the other side
                            const secondLastSubdivisionIndex = calculateActualSubdivisionIndex(subdivisions, componentID, nonEmptySubdivisionBaseIndexes[nonEmptyIndex-2], nonEmptySubdivisionFurtherIndexes[nonEmptyIndex-2]);
                            if (subdivisionBeams[secondLastSubdivisionIndex] >= lastBeams) {
                                needsHalfBeams = false;
                            }
                        }
                        if (needsHalfBeams) {
                            for (let n=minBeams; n<lastBeams; n++) {
                                path += "M" + x + " " + (n * 10) + " L" + (x + 20) + " " + (n * 10) + " ";
                            }
                        }
                    } else if (currentBeams > minBeams) {  // We might need half-beams on the right
                        // Check if it already has enough beams on the other side
                        let needsHalfBeams = true;
                        if (nonEmptyIndex < nonEmptySubdivisionBaseIndexes.length - 2) {  // If current is the last then it cannot have beams on the other side
                            const nextSubdivisionIndex = calculateActualSubdivisionIndex(subdivisions, componentID, nonEmptySubdivisionBaseIndexes[nonEmptyIndex+1], nonEmptySubdivisionFurtherIndexes[nonEmptyIndex+1]);
                            if (subdivisionBeams[nextSubdivisionIndex] >= currentBeams) {
                                needsHalfBeams = false;
                            }
                        }
                        if (needsHalfBeams) {
                            for (let n=minBeams; n<currentBeams; n++) {
                                path += "M" + (x + 30) + " " + (n * 10) + " L" + (x + 50) + " " + (n * 10) + " ";
                            }
                        }
                    }
                }

                x += 50;  // Beams are 50 wide so move x by 50 (or if no beams then move anyway)
                
                // Draw stem
                path += "M" + x + " 0 L" + x + " 50 "

                // Now we can draw dots
                const dots = subdivisionDots[currentSubdivisionIndex];
                const y = 10 * subdivisionBeams[currentSubdivisionIndex];  // Put under lowest beam
                drawDots(svg, x + 5, y, dots);  // Drawn under beams, assume less than 50px worth of dots, so we don't change x
            }
        }
        x += 50;  // Spacing between beats
        const beams = document.createElementNS("http://www.w3.org/2000/svg", "path");
        beams.setAttribute("d", path);
        beams.setAttribute("stroke", "black");
        beams.setAttribute("stroke-width", "3");
        svg.appendChild(beams);
        svg.setAttribute("height", "50");
        svg.setAttribute("width", x);
    }

    
    // Initial coordinates 
    svg.style.left = (getScoreComponentX(componentID) * 100) + "%";
    svg.style.top = (getScoreComponentY(componentID) * 100) + "%";
    // Add dragging logic
    const container = document.getElementById("component-container");
    svg.onmousedown = (downEvent) => {
        console.log("1", downEvent);
        const svgRect = svg.getBoundingClientRect();
        const parentRect = container.getBoundingClientRect();
        document.onmousemove = (moveEvent) => {
            console.log("2", downEvent);
            const newX = (svgRect.left - parentRect.left + moveEvent.clientX - downEvent.clientX) / parentRect.width;
            const newY = (svgRect.top - parentRect.top + moveEvent.clientY - downEvent.clientY) / parentRect.height;
            setScoreComponentX(componentID, newX);
            setScoreComponentY(componentID, newY);
            svg.style.left = (newX * 100) + "%";
            svg.style.top = (newY * 100) + "%";
        }
        document.onmouseup = (upEvent) => {
            console.log("3", downEvent);
            document.onmousemove = null;
            document.onmouseup = null;
        }
    }
    // Editing of component
    svg.onmouseup = (e) => {
        setEditComponent("score-component", componentID);
    }

    // Now add the svg to the document
    document.getElementById("component-container").appendChild(svg);
}
