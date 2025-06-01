import {getDrumSymbolID, getDrumY} from "./drums.js";
import {setEditComponent} from "./editor.js";
import {getScoreComponentBaseSubdivisions, getScoreComponentFurtherSubdivisionCount, getScoreComponentFurtherSubdivisionDrums, getScoreComponentTimeSignatureDenominator, getScoreComponentTimeSignatureNumerator, getScoreComponentX, getScoreComponentY, setScoreComponentX, setScoreComponentY} from "./files.js";
import {getSymbolIDs, getSymbolPath, getSymbolLeft, getSymbolRight, getSymbolTop, getSymbolBottom} from "./symbols.js";

class RhythmInformation {
	constructor (subdivisions, subdivisionValues, subdivisionBeams, subdivisionDots, nonEmptySubdivisionBaseIndexes, nonEmptySubdivisionFurtherIndexes) {
		this.subdivisions = subdivisions;
		this.subdivisionValues = Object.freeze([...subdivisionValues]);  // Freeze so immutable
		this.subdivisionBeams = Object.freeze([...subdivisionBeams]);
		this.subdivisionDots = Object.freeze([...subdivisionDots]);
		this.nonEmptySubdivisionBaseIndexes = Object.freeze([...nonEmptySubdivisionBaseIndexes]);
		this.nonEmptySubdivisionFurtherIndexes = Object.freeze([...nonEmptySubdivisionFurtherIndexes]);
		
		Object.freeze(this);

	}
}

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

function calculateRhythmInformation(componentID, beatIndex) {
	// Get's the rythm information for the given component on the given beat. 
	// This consists of how many bars, flags and dots to draw over each subdivision. It also returns non-empty subdivisions.
	// The bar, flag and dot arrays contain a value for each subdivision, the indexes can be found with calculateActualSubdivisionIndex.
	// The return value is a RhythmInformation object.

	// We store it as a mix of subdivisions, but we need to have only one per beat that can account for all.
    // The easiest way to do this is to find the product of all the subdivisions 
    const baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
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
	
	return new RhythmInformation(subdivisions, subdivisionValues, subdivisionBeams, subdivisionDots, nonEmptySubdivisionBaseIndexes, nonEmptySubdivisionFurtherIndexes);
}

function drawPath(svg, pathString) {
	// Draws the given path to the svg.
	// Returns the created path node.
	const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", pathString);
    path.setAttribute("stroke", "black");
    path.setAttribute("stroke-width", "3");
    svg.appendChild(path);

	return path;
}

function drawRest(svg, x, componentID, rhythmInformation) {
	// Draw a rest (if required) and add it to the svg using the given information.
	// This returns the new x-coordinate, as well as the path.
	

	
	let path;
	if (rhythmInformation.nonEmptySubdivisionBaseIndexes.length == 0) {  // Draw crotchet rest
		x += 10  // Left padding
		
		path = "M" + x + " 0 L" + (x + 5) + " 10 L" + x + " 15 L" + (x + 5) + " 20 ";
		
		x += 10;
		
	} else if ((rhythmInformation.nonEmptySubdivisionBaseIndexes[0] % getScoreComponentBaseSubdivisions(componentID)) !== 0 || rhythmInformation.nonEmptySubdivisionFurtherIndexes[0] !== 0) {  // Draw the other kind of rest
		x += 15  // Left padding
	
		const restTicks = rhythmInformation.subdivisionBeams[0];
        const restDots = rhythmInformation.subdivisionDots[0];

        path = "M" + x + " 30 L" + (x + restTicks * 5 + 2.5) + " " + (27.5 - restTicks * 5) + " ";
        for (let n=0; n<restTicks; n++) {
            path += "M" + (x + n * 5 + 5) + " " + (25 - n * 5) + " L" + (x + n * 5) + " " + (20 - n * 5) + " ";
        }
        x += 10;
        drawDots(svg, x, "27.5", restDots);
        x += 5 * restTicks;
	} else {  // No rest
		return x;
	}
	
	drawPath(svg, path);
	
	return x;
}

function drawNoteHeads(svg, x, nonEmptyIndex, componentID, rhythmInformation) {
	// Draws note head(s) to the svg.
	// The new x-coordinate is returned. It also returns lowestSubdivisionY - the lowest note-head's stem connection point, and lowestSubdivisionYDrumBottom - the distance the lowest note-head's goes below lowestSubdivisionYDrumBottom
	
    x += 50;  // Note heads draw backwards to increment x beforehand
	
    let lowestSubdivisionY = 0;
    let lowestSubdivisionYDrumBottom = 0;
    const drumIDs = getScoreComponentFurtherSubdivisionDrums(componentID, rhythmInformation.nonEmptySubdivisionBaseIndexes[nonEmptyIndex], rhythmInformation.nonEmptySubdivisionFurtherIndexes[nonEmptyIndex]);
    for (let drumIndex = 0; drumIndex < drumIDs.length; drumIndex++) {
        const drumID = drumIDs[drumIndex];
        const symbolID = getDrumSymbolID(drumID);
        const drumY = getDrumY(drumID);
        const path = getSymbolPath(symbolID);
        const left = getSymbolLeft(symbolID);
        const right = getSymbolRight(symbolID);
        const top = getSymbolTop(symbolID);
        const bottom = getSymbolBottom(symbolID);
        
        if (drumY > lowestSubdivisionY) {
            lowestSubdivisionY = drumY;
            lowestSubdivisionYDrumBottom = bottom;
        }
		
        const pathNode = drawPath(svg, path);
        pathNode.setAttribute("transform", "translate(" + x + " " + drumY + ")")
    }
    
    return {x, lowestSubdivisionY, lowestSubdivisionYDrumBottom};
}

function drawStem(svg, x, lowestPoint) {
	// Draws a stem at the given x-coordinate from y=0 to y=lowestPoint
	drawPath(svg, "M" + x + " 0 L" + x + " " + lowestPoint + " ");
}

function drawFlagsAndDots(svg, x, subdivisionIndex, rhythmInformation) {
	// Draws the flags and dots for a subdivision that has no beams.
	// Assume less than 50px worth of dots, so doesn't change x

	// Draw flags
    let y = 0;
    let path = "";
    for (let n=0; n < rhythmInformation.subdivisionBeams[subdivisionIndex]; n++) {
        path += "M" + x + " " + y + " L" + (x + 10) + " " + (y + 10) + " ";
        y += 5;
    }
    y += 10;
    drawPath(svg, path);
    
    // Draw dots
    const dots = rhythmInformation.subdivisionDots[subdivisionIndex];
    drawDots(svg, x + 5, y, dots); // Drawn under flags
}

export function renderComponent(componentType, componentID) {
	// Render the given component. If it already exists then it will be removed.
    
    // First delete it if it already exists
    let old = document.getElementById(componentType + "_" + componentID);
    if (old !== null) {
        old.remove();
    }

    if (componentType !== "score-component") throw "Not Implemented";
    
    // Now let's render it ----------------------------------
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.classList.add("score-component");
    svg.setAttribute("id", componentType + "_" + componentID);  // So we can delete it later
    
    const timeSignatureNumerator = getScoreComponentTimeSignatureNumerator(componentID);  // Number of beats
    let x = 0;  // Current x-coord (of last beat)
    let height = 50;  // Min height
    for (let beatIndex = 0; beatIndex < timeSignatureNumerator; beatIndex++) {
    	const rhythmInformation = calculateRhythmInformation(componentID, beatIndex);  // Get the rhythm information
    	
    	x = drawRest(svg, x, componentID, rhythmInformation);  // Draw rests if we need them
    	
    	if (rhythmInformation.nonEmptySubdivisionBaseIndexes.length == 0) {  // We don't do anything if there's nothing to draw (rests done above)
    	
    	
    	} else if (rhythmInformation.nonEmptySubdivisionBaseIndexes.length == 1) {  // Single note needs no beams
    		const subdivisionIndex = calculateActualSubdivisionIndex(rhythmInformation.subdivisions, componentID, rhythmInformation.nonEmptySubdivisionBaseIndexes[0], rhythmInformation.nonEmptySubdivisionFurtherIndexes[0]);
    		
    		const {x: newX, lowestSubdivisionY, lowestSubdivisionYDrumBottom} = drawNoteHeads(svg, x, 0, componentID, rhythmInformation);
    		const newHeight = lowestSubdivisionY + lowestSubdivisionYDrumBottom;
    		x = newX;  // We need to do it like this so we don't re-declare x.
    		drawStem(svg, x, lowestSubdivisionY);
    		drawFlagsAndDots(svg, x, subdivisionIndex, rhythmInformation);
    		
    		x += 10;  // Flag padding
    		
    		height = Math.max(height, newHeight);
    		
    		
    	} else {  // Draw notes and beams
    		// Draw note head(s)
    		let path = "";  // Beam path
    		for (let nonEmptyIndex=0; nonEmptyIndex<rhythmInformation.nonEmptySubdivisionBaseIndexes.length; nonEmptyIndex++) {
                const currentSubdivisionIndex = calculateActualSubdivisionIndex(rhythmInformation.subdivisions, componentID, rhythmInformation.nonEmptySubdivisionBaseIndexes[nonEmptyIndex], rhythmInformation.nonEmptySubdivisionFurtherIndexes[nonEmptyIndex]);
                
                // Draw head(s) and stem
                const {x: newX, lowestSubdivisionY, lowestSubdivisionYDrumBottom} = drawNoteHeads(svg, x, nonEmptyIndex, componentID, rhythmInformation);  // We need the old x for the beams.
                const newHeight = lowestSubdivisionY + lowestSubdivisionYDrumBottom;
                drawStem(svg, newX, lowestSubdivisionY);  // Stem goes after note heads
                height = Math.max(height, newHeight);
                
                
                // Draw beams and dots
                // We need to draw beams between pairs of adjacent non-empty subdivisions. So if this is the first then we can ignore it.
                if (nonEmptyIndex != 0) {  
                    // Collect the information
                    const lastSubdivisionIndex = calculateActualSubdivisionIndex(rhythmInformation.subdivisions, componentID, rhythmInformation.nonEmptySubdivisionBaseIndexes[nonEmptyIndex-1], rhythmInformation.nonEmptySubdivisionFurtherIndexes[nonEmptyIndex-1]);
                    const lastBeams = rhythmInformation.subdivisionBeams[lastSubdivisionIndex];
                    const currentBeams = rhythmInformation.subdivisionBeams[currentSubdivisionIndex];
                    const minBeams = Math.min(lastBeams, currentBeams);

                    // Now draw the beams
                    // Full-beams:
                    for (let n=0; n<minBeams; n++) {
                        path += "M" + x + " " + (n * 10) + " L" + newX + " " + (n * 10) + " ";
                    }
                    // Half-beams:
                    // We need half-beams iff a stem needs more beams than are connected to it (on either side).
                    if (lastBeams > minBeams) {  // We might need half-beams on the left
                        // Check if it already has enough beams on the other side
                        let needsHalfBeams = true;
                        if (nonEmptyIndex > 1) {  // If last is the first then it cannot have any on the other side
                            const secondLastSubdivisionIndex = calculateActualSubdivisionIndex(rhythmInformation.subdivisions, componentID, rhythmInformation.nonEmptySubdivisionBaseIndexes[nonEmptyIndex-2], rhythmInformation.nonEmptySubdivisionFurtherIndexes[nonEmptyIndex-2]);
                            if (rhythmInformation.subdivisionBeams[secondLastSubdivisionIndex] >= lastBeams) {
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
                        if (nonEmptyIndex < rhythmInformation.nonEmptySubdivisionBaseIndexes.length - 2) {  // If current is the last then it cannot have beams on the other side
                            const nextSubdivisionIndex = calculateActualSubdivisionIndex(rhythmInformation.subdivisions, componentID, rhythmInformation.nonEmptySubdivisionBaseIndexes[nonEmptyIndex+1], rhythmInformation.nonEmptySubdivisionFurtherIndexes[nonEmptyIndex+1]);
                            if (rhythmInformation.subdivisionBeams[nextSubdivisionIndex] >= currentBeams) {
                                needsHalfBeams = false;
                            }
                        }
                        if (needsHalfBeams) {
                            for (let n=minBeams; n<currentBeams; n++) {
                                path += "M" + (newX - 20) + " " + (n * 10) + " L" + newX + " " + (n * 10) + " ";
                            }
                        }
                    }
                }

                x = newX;  // Draw dots after stem
                const dots = rhythmInformation.subdivisionDots[currentSubdivisionIndex];
                const y = 10 * rhythmInformation.subdivisionBeams[currentSubdivisionIndex];  // Put under lowest beam
                drawDots(svg, x + 5, y, dots);  // Drawn under beams, assume less than 50px worth of dots, so we don't change x
            }
            drawPath(svg, path);  // Draw beams
    	}
	}
	
	// Set size with some padding
	svg.setAttribute("height", height + 20);
    svg.setAttribute("width", x + 20);
    svg.setAttribute("viewBox", "-10 -10 " + (x + 20) + " " + (height + 20));
    
    
    // Positioning and interactions ----------------------------------
    // Initial coordinates 
    svg.style.left = (getScoreComponentX(componentID) * 100) + "%";
    svg.style.top = (getScoreComponentY(componentID) * 100) + "%";
    // Add dragging logic
    const container = document.getElementById("component-container");
    svg.onmousedown = (downEvent) => {
        const svgRect = svg.getBoundingClientRect();
        const parentRect = container.getBoundingClientRect();
        document.onmousemove = (moveEvent) => {
            const newX = (svgRect.left - parentRect.left + moveEvent.clientX - downEvent.clientX) / parentRect.width;
            const newY = (svgRect.top - parentRect.top + moveEvent.clientY - downEvent.clientY) / parentRect.height;
            setScoreComponentX(componentID, newX);
            setScoreComponentY(componentID, newY);
            svg.style.left = (newX * 100) + "%";
            svg.style.top = (newY * 100) + "%";
        }
        document.onmouseup = (upEvent) => {
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
    	

























