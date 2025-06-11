import {getScoreComponentBaseSubdivisions, getScoreComponentFurtherSubdivisionCount, getScoreComponentFurtherSubdivisionDrums, getScoreComponentTimeSignatureNumerator} from "./files.js";

class RenderInstruction {
    // Render instructions are produced by preRenderScoreComponent and are used to tell renderScoreComponent what to draw.
    //
    // There are a couple types of render-instructions (and what they store):
    //     GROUP: 
    //         - drums
    //         - decorations
    //         - full-beams
    //         - broken-beams
    //         - dots
    //     GROUP-END:
    //         - drums
    //         - decorations
    //         - dots
    //     FLAG:
    //         - drums
    //         - decorations
    //         - flags
    //         - dots
    //     REST:
    //         - ticks
    //         - dots
    // 
    // drums: A string array of the drumIDs to draw.
    // decorations: A string array of the symbolIDs to draw.
    // full-beams: The number (non-zero and positive) of full beams to draw between this instruction and the next instruction (with a stem, full beams go over rests).
    // broken-beams: The same full-beams except for broken-beams. This can be signed, where negative means to draw on the left, and positive to the right. It can also be zero - no broken-beams. If dots != 0 then this cannot be negative.
    // dots: The number (zero or positive) of dots that should be drawn after the stem. If broken-beams is negative (broken-beams on the left) then this must be 0 (no dots).
    // flags: The number (zero or positive) of flags to draw after the stem.
    // ticks: The number (zero or positive) of ticks to draw on a rest. Zero means it's a crotchet rest.
    // 
    // GROUPs connect to the next GROUP or GROUP-END, so must be followed by at least one of these. However RESTs can be put in-between.
    // Rests can also come between GROUPs, FLAGs and RESTs.
    // A GROUP-END must follow a GROUP (there can be RESTs in-between).
    // FLAGs stand alone so should not follow an un-ended GROUP.
    // This means crotchets should be represented using a FLAG with flags=0.
    
    // Instruction Types
    static get GROUP() {return "GROUP";}  // Declare like this so are immutable.
    static get GROUP_END() {return "GROUP_END";}
    static get FLAG() {return "FLAG";}
    static get REST() {return "REST";}

    constructor(type, ...args) {
        // Type should be the value in GROUP, GROUP_END...
        // Args should be passed in the order they are documented in.
        
        this.type = type;
        if (type === RenderInstruction.GROUP) {
            this.drums = args[0];
            this.decorations = args[1];
            this.full_beams = args[2];
            this.broken_beams = args[3];
            this.dots = args[4];
        } else if (type === RenderInstruction.GROUP_END) {
            this.drums = args[0];
this.decorations = args[1];
            this.dots = args[2];
        } else if (type === RenderInstruction.FLAG) {
            this.drums = args[0];
         this.decorations = args[1];
            this.flags = args[2];
            this.dots = args[3];
        } else if (type === RenderInstruction.REST) {
            this.ticks = args[0];
            this.dots = args[1];
        }
        
        // Object.freeze(this);  // So is immutable  // TODO: Freeze this again
    }
}

function calculateFinalSubdivisionIndex(finalSubdivisions, componentID, base, further) {
    // Convert a base and further subdivision index to an index in a subdivision length of finalSubdivisions.
    // This is relative to the start of the bar.
    const furtherCount = getScoreComponentFurtherSubdivisionCount(componentID, base);
    const baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
    return (finalSubdivisions / baseSubdivisions * base) + (finalSubdivisions / baseSubdivisions / furtherCount * further);
}

function numberOfFactors(n, f) {
    // Returns the number of times n fits fully into f.
    let count = -1;  // As the loop adds a count for the first non-integer value
    while (n == Math.floor(n)) {
        n /= f;
        count += 1;
    }
    return count;
}

// TODO: Move this to another file called compiler or something idk
function preRenderScoreComponent(componentID) {
    // Figures out how to actaully draw the score-component.
    // This is like the overall idea, it tells us what we need to draw, not how. Specifically which drums, decorations on each subdivision, and what bars / dots / rests / flags to draw.

    let baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
    let numerator = getScoreComponentTimeSignatureNumerator(componentID);
    

    // First, calculate the non-empty subdivision indexes:
    function SubdivisionIndex(base, further) {
        // The name says it all.
        this.base = base;
        this.further = further;
        Object.freeze(this);
    }
    let nonEmptySubdivisionIndexes = [];  // Holds {base: int, further: int}
    let baseSubdivisionIndex = 0;
    let furtherSubdivisionIndex = 0;
    while (baseSubdivisionIndex < baseSubdivisions * numerator) {
        if (getScoreComponentFurtherSubdivisionDrums(componentID, baseSubdivisionIndex, furtherSubdivisionIndex).length != 0) {  // If it's non-empty
            nonEmptySubdivisionIndexes.push(new SubdivisionIndex(baseSubdivisionIndex, furtherSubdivisionIndex));
        }

        // Increment indexes
        furtherSubdivisionIndex += 1;
        if (furtherSubdivisionIndex >= getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex)) {
            furtherSubdivisionIndex = 0;
            baseSubdivisionIndex += 1;
        }
    }
    console.log(nonEmptySubdivisionIndexes);

    // Second, figure out what the final subdivision is.
    // We calculate this for the whole bar, and it is (the number of subdivisions we would need to store the whole bar without any further subdivisions) * baseSubdivisions = baseSubdivisions * (LCM(all the furtherSubdivisions)).
    let finalSubdivisions = 1;
    // For now just multiply finalSubdivisions by furtherSubdivisions if furtherSubdivisions does not fit into finalSubdivisions.
    for (let baseSubdivisionIndex = 0; baseSubdivisionIndex < baseSubdivisions * numerator; baseSubdivisionIndex++) {
        const furtherSubdivisionCount = getScoreComponentFurtherSubdivisionCount(componentID, baseSubdivisionIndex);
        if (finalSubdivisions % furtherSubdivisionCount != 0) {
            finalSubdivisions *= furtherSubdivisionCount;
        }
    }
    finalSubdivisions *= baseSubdivisions;


    // Third, group subdivisions so we only have what needs to be drawn:
    // At this point we will ignore how long these groups can actually be (there a limitations as to what lengths can be represented with dots and beams) and just make groups as big as possible. We will also ignore rests for now.
    function SubdivisionGroup(subdivisionIndex, length) {
        // A group of `length` adjacent subdivisions starting at `index`.
        // The subdivision at `index` may be empty, the rest must be empty.
        // If subdivisionIndex is null then it means a rest of the given length.
        // The length is the number of finalSubdivisions.
        this.index = subdivisionIndex;
        this.length = length;
        Object.freeze(this);
    }
    let sGroups = [];  // List of SubdivisionGroups
    for (let i = 0; i < nonEmptySubdivisionIndexes.length; i++) {
        const currentIndex = nonEmptySubdivisionIndexes[i];
        const currentFinalIndex = calculateFinalSubdivisionIndex(finalSubdivisions, componentID, currentIndex.base, currentIndex.further);
        
        // Get the next index (if it exists) or the first beat in the next bar
        let nextIndex;
        let nextFinalIndex;
        if (i + 1 == nonEmptySubdivisionIndexes.length) {  // Current is the last non-empty so length is till the end of the bar
            nextIndex = new SubdivisionIndex(numerator * baseSubdivisions, 0);  // Would be first beat in next bar
            nextFinalIndex = finalSubdivisions * numerator;  // We can't use the calculate function because that subdivision doesn't exist
        } else {  // There's another non-empty so get that
            nextIndex = nonEmptySubdivisionIndexes[i + 1];
            nextFinalIndex = calculateFinalSubdivisionIndex(finalSubdivisions, componentID, nextIndex.base, nextIndex.further)
        }
        
        // Add this group the the array
        sGroups.push(new SubdivisionGroup(currentIndex, nextFinalIndex - currentFinalIndex));


    }
    console.log(sGroups);

    // Fourth, clean the sGroups:
    // Many of the sGroups are actually impossible due to limitations with beams and dots, and many will also cross beat boundaries (which they should not). So add rests where they are required.
    SubdivisionGroup.prototype.rhythmInfo = function() {
        // Returns {bars, beams, length} where length is the actual length (with respect to finalSubdivisions) of this note (as this.length may not be possible).
        
        // Beams
        let val = this.length / finalSubdivisions;
        if (val < 0) throw "val < 0"
        let beams = 0; 
        while (val < 1) {
            val *= 2;
            beams += 1;
        }
        
        // Dots
        const initialValue = finalSubdivisions / Math.pow(2, beams);  // The value of the note before the dots
         val = this.length - initialValue;
        let dots = 0;
        while (val > 0 && numberOfFactors(finalSubdivisions, 2) >= dots) {  // If we can add more dots, and our final subdivision allows for more dots
            dots += 1;
            val -= initialValue / Math.pow(2, dots);
        }
        if (val < 0) {
            val += initialValue / Math.pow(2, dots);
            dots -= 1;  // We want to be just under this.length.
        }

        // Get actual length
        const length = this.length - val;


        return {beams, dots, length};
    }

    // Does the bar start with a rest
    if (sGroups.length > 0 && (sGroups[0].index.base != 0 || sGroups[0].index.further != 0)) {
        sGroups.splice(0, 0, new SubdivisionGroup(new SubdivisionIndex(0, 0), calculateFinalSubdivisionIndex(finalSubdivisions, componentID, sGroups[0].index.base, sGroups[0].index.further)));  // Index cannot be null, as it's length may be bigger than a beat, and the next algorithm needs the index to split it up
    } else if (sGroups.length == 0) {  // Insert a rest that is as long as the bar
        sGroups.push(new SubdivisionGroup(new SubdivisionIndex(0, 0), finalSubdivisions * numerator));
    }

    // We will work on the array in-place because then any rests we add that are illegal will be fixed in further iterations
    for (let i=0; i < sGroups.length; i++) {
        let group = sGroups[i];

        // Does group cross a beat boundary?
        if (group.index != null) {  // If index is null then we created it so it shouldn't be over a boundary
            let groupStartFinal = calculateFinalSubdivisionIndex(finalSubdivisions, componentID, group.index.base, group.index.further);
            let groupEndFinal = groupStartFinal + group.length - 1;  // We want the last final subdivision of this group, not the first of the next
            if (Math.floor(groupStartFinal / finalSubdivisions) != Math.floor(groupEndFinal / finalSubdivisions)) {
                // It does so we need to split it on the beat boundary.
                let amountOver = groupEndFinal % finalSubdivisions + 1;  // Because the first in the next beat is 1 over, not 0 over.
                const newLength = group.length - amountOver;

                // Check if we need to add crotchet rests
                let crotchetRestCount = 0;
                while (amountOver >= finalSubdivisions) {
                    crotchetRestCount += 1;
                    amountOver -= finalSubdivisions;
                }
                // Incase my logic is wrong
                if (amountOver < 0) throw "newLength < 0"

                // Split the group
                sGroups.splice(i, 1, new SubdivisionGroup(group.index, newLength));  // Replace the old group
                for (let n=0; n<crotchetRestCount; n++) { // Add crotchet rests
                    sGroups.splice(i + n + 1, 0, new SubdivisionGroup(null, finalSubdivisions));  // We can put null in because it is a rest.
                }
                if (amountOver != 0) {
                    sGroups.splice(i + crotchetRestCount + 1, 0, new SubdivisionGroup(null, amountOver));  // Add the smaller rest. We can put null because it is a rest.
                }
            }
            group = sGroups[i];
        }

        // Is the group an illegal length?
        const rhythmInfo = group.rhythmInfo();
        if (rhythmInfo.length != group.length) {
            const amountOver = group.length - rhythmInfo.length;
            if (amountOver < 0) throw "amountOver < 0";

            // We can assume amountOver is less than a crotchet because we handled that above
            
            // Split the group
            sGroups.splice(i, 1, new SubdivisionGroup(group.index, rhythmInfo.length));  // Replace the old group
            sGroups.splice(i + 1, 0, new SubdivisionGroup(null, amountOver));  // Put in the rest. We can put null because it is a rest
        }
        group = sGroups[i];
    }
    console.log(sGroups);



    // Fifth, convert groups to RenderInstructions
    SubdivisionGroup.prototype.drums = function() {
        // Gets the list of drums in this subdivision group.

        // If currentIndex is null then it's rest (so is empty)
        if (this.index == null) {
            return [];
        }

        // Otherwise load the score-component info
        return getScoreComponentFurtherSubdivisionDrums(componentID, this.index.base, this.index.further);
    }
    const renderInstructions = [];
    let i = 0;
    let finalIndex = 0;  // Some SubdivisionGroups won't store an index, so we will use the lengths to track which beat we are in
    while (i<sGroups.length) {
        // We do this one beat at a time, first we need to know whether this beat has beams or flags (or is only a rest). For this we need to know how many sGroups are in this beat and which sGroups are non-empty (so are not rests).
            const currentBeat = Math.floor(finalIndex / finalSubdivisions);
            let j = i;  // We know sGroup[i] must fit within this beat, but we don't know if it's non-empty, and that is checked inside the loop
            const nonEmptySGroups = [];
            while (j < sGroups.length && currentBeat == Math.floor((
                finalIndex + sGroups[j].length - 1  // - 1 as + length is the finalSubdivision immediately after this sGroup, not that last one in this sGroup
            ) / finalSubdivisions)) {  // Is still sGroups left and are we still in the same beat?
                finalIndex += sGroups[j].length;
                if (sGroups[j].drums().length != 0) {
                    nonEmptySGroups.push(sGroups[j]);
                }
                j += 1;
            }
            
            // Now create the render instructions
            if (nonEmptySGroups.length == 0 || nonEmptySGroups.length == 1) {  // It's only RESTs or it's RESTs and a FLAG
                // There may still be rests so loop properly
                while (i < j) {
                    const current = sGroups[i];
                    if (current.drums().length == 0) {  // It's a rest
                        renderInstructions.push(new RenderInstruction(RenderInstruction.REST, current.rhythmInfo().beams, current.rhythmInfo().dots));
                    } else {  // It's a flag
                        renderInstructions.push(new RenderInstruction(RenderInstruction.FLAG, current.drums(), [], current.rhythmInfo().beams, current.rhythmInfo().dots));
                    }
                    i += 1;
                    finalIndex += current.length;
                }
            } else {  // We need to add some GROUPs, a GROUP_END and possibly some RESTs
            

                let nonEmptyI = 0;  // The index in the nonEmptySGroups array. The value in here should refer to the same sGroup as i does
                let lastGroup = null;  // The last GROUP that we created
                while (i < j) {
                    if (sGroups[i].drums().length == 0) {  
                        // This is a rest, so it doesn't affect the beams (they go over it (unless this is at the start or end of the beat but it still doesn't matter)).
                        renderInstructions.push(new RenderInstruction(RenderInstruction.REST, sGroups[i].rhythmInfo().beams, sGroups[i].rhythmInfo().dots));
                        finalIndex += sGroups[i].length;
                        i++;
                    } else {
                        // This is not a rest, so calculate
                                               
                        if (nonEmptyI < nonEmptySGroups.length - 1) { // Are there more non-empty groups to beam to?
                            // We need to figure out what combination of (full) beams and broken-beams we need to draw for this current GROUP
                            const c = nonEmptySGroups[nonEmptyI].rhythmInfo().beams;  // How many beams it wants connected to it
                            const n = nonEmptySGroups[nonEmptyI + 1].rhythmInfo().beams;
                            const nn = ((nonEmptyI < nonEmptySGroups.length - 2) ? nonEmptySGroups[nonEmptyI + 2].rhythmInfo().beams : 0);  // If a sGroup doesn't exist then it will supply no beams, so just say 0
                            const l = ((nonEmptyI > 0) ? nonEmptySGroups[nonEmptyI - 1].rhythmInfo().beams : 0);  
                            
                            // Remember, beams go from c to n!
                            if (c == n) {  // Both want the same number of beams. So draw that.
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[i].drums(), [], c, 0, sGroups[i].rhythmInfo().dots));
                            } else if (c < n && nn >= n) {  // Next wants more beams than current will give it, but nextnext is able to supply what it needs. So we only need to draw current (full) beams
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[i].drums(), [], c, 0, sGroups[i].rhythmInfo().dots));
                            } else if (c < n && nn < n) {  // Next wants more beams than current will give it, and nextnext also won't supply enough. So draw c full (beams) and n-c half-beams on the right
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[i].drums(), [], c, n - c, sGroups[i].rhythmInfo().dots)); 
                            } else if (c > n && l >= c) {  // If current wants more beams than next will supply, but last can supply enough. So draw n (full) beams
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[i].drums(), [], n, 0, sGroups[i].rhythmInfo().dots));
                            } else if (c > n && l < c) {  // If current wants more beams than next will supply, and last can't supply enough beams
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[i].drums(), [], n, -(c - n), sGroups[i].rhythmInfo().dots));  // Negative broken-beams means draw on left
                            } else {
                                throw "None of the beam logic cases worked, this shouldn't be possible, here are the values " + l + " " + c + " " + n + " " + nn;
                            }
                            
                            // In the case that we have drawn broken beams on both sides of a stem
                            const currentGroup = renderInstructions[renderInstructions.length - 1];
                            if (lastGroup != null && lastGroup.broken_beams > 0 && currentGroup.broken_beams < 0) {
                                // We only want to keep the side with the most full-beams
                                if (lastGroup.full_beams >= currentGroup.full_beams) {  // If both equal then point left
                                    currentGroup.broken_beams = 0;
                                } else {
                                    lastGroup.broken_beams = 0;
                                    
                                }
                            }
                            lastGroup = currentGroup;
                            
                            

                        } else { // This is the last non-empty sGroup so this is a GROUP-END
                            renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP_END, sGroups[i].drums, [], sGroups[i].rhythmInfo().dots));
                        }

                        finalIndex += sGroups[i].length;
                        i++;
                        nonEmptyI++;
                    }
                }
            }
    }

    return renderInstructions;
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


function renderScoreComponent(componentID) {
    // Renders a score component. This returns a svg node.
    // This does not attach the event handling stuff.
    let instructions = preRenderScoreComponent(componentID);
    console.log(instructions);
    // TODO: Process sizing first?
    // Then draw.
    
    
    // PoC renderer
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.classList.add("score-component");
    

    function drawRest(svg, path, instructions, i, y) {
        if (instructions[i].ticks == 0) {
            path += "M" + x + " " + y + " L" + (x + 5) + " " + (y + 10) + " L" + x + " " + (y + 15) + " L" + (x + 5) + " " + (y + 20) + " ";
            x += 5;
            if (instructions[i].dots != 0) throw "We can't draw dots on a crotchet rest";
        } else {
            const count = instructions[i].ticks;
            path += "M" + x + " " + (y + count * 10) + " L" + (x + count * 10) + " " + y + " ";
            for (let n=0; n < count; n++) {
                path += "M" + (x + 5 + n * 10) + " " + (y + (count - n) * 10 - 5) + " L" + (x + n * 10) + " " + (y + (count - n) * 10 - 10) + " ";
            }
            drawDots(svg, x + 10, y + count * 10 - 5, instructions[i].dots);
            x += Math.max(count * 10, instructions[i].dots * 10 + 10);
        }

        return path;
    }


    let i = 0;
    let x = 0;
    let lastBeamPath = "";
    let path = "";
    while (i < instructions.length) {
        if (instructions[i].type === RenderInstruction.REST) {
           path = drawRest(svg, path, instructions, i, 0); 
        } else if (instructions[i].type === RenderInstruction.FLAG) {
            path += "M" + x + " 0 " + "L" + x + " 100 ";
            for (let n=0; n < instructions[i].flags; n++) {
                path += "M" + x + " " + (n * 10) + " L" + (x + 10) + " " + (n * 10 + 10) + " ";
            }
            drawDots(svg, x + 5, instructions[i].flags * 10 + 20, instructions[i].dots)
            x += Math.max(5, instructions[i].dots * 5 + 5);
        } else if (instructions[i].type === RenderInstruction.GROUP) {
            while (instructions[i].type !== RenderInstruction.GROUP_END) {
                if (instructions[i].type === RenderInstruction.FLAG) {
                    throw "Found flag in the middle of a GROUP";
                } else if (instructions[i].type == RenderInstruction.REST) {
                    path = drawRest(svg, path, instructions, i, 50);
                    x += 10;  // Spacing
                } else {
                    path += lastBeamPath.replaceAll("subX", (x-10).toString()).replaceAll("x", x.toString());
                    lastBeamPath = "";

                    path += "M" + x + " 0 " + "L" + x + " 100 ";
                    let y = 0;
                    for (let n = 0; n< instructions[i].full_beams; n++) {
                        lastBeamPath += "M" + x + " " + y + " Lx " + y + " ";
                        y += 5;
                    }
                    for (let n = 0; n> instructions[i].broken_beams; n--) {
                        path += "M" + x + " " + y + " L" + (x + 10) + " " + y + " ";
                        y += 5;
                    }
                     for (let n = 0; n< instructions[i].broken_beams; n++) {
                        lastBeamPath += "MsubX " + y + " Lx " + y + " ";
                        y += 5;
                    }
                    drawDots(svg, x + 5, y, instructions[i].dots);

                    x += Math.max((instructions[i].broken_beams == 0) ? 10 : 20, instructions[i].dots * 5 + 5);
                }
                i += 1;
            }
            path += lastBeamPath.replaceAll("subX", (x-10).toString()).replaceAll("x", x.toString());
            lastBeamPath = "";
            path += "M" + x + " 0 " + "L" + x + " 100 ";
            drawDots(svg, x + 5, 0, instructions[i].dots);
        } else {
            throw "Unexpected instruction type " + instructions[i].type;
        }
        x += 10;  // Spacing
        i++;
    }
    x -= 10;  // Don't need the last spacing
    path = path.trim();  // It has a space as the last character

    const pathNode = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathNode.setAttribute("d", path);
    pathNode.setAttribute("stroke", "black");
    pathNode.setAttribute("stroke-width", "3");
    pathNode.setAttribute("fill", "none");
    svg.appendChild(pathNode);
    
    svg.style.left = "20px";
    svg.style.top = "20px";
    svg.setAttribute("viewBox", "-10 -10 " + (x + 20) + " 150");
    svg.setAttribute("width", x + 20);
    svg.setAttribute("height", 150 + 20);

    return svg;

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
    let svg = renderScoreComponent(componentID);
    svg.setAttribute("id", componentType + "_" + componentID);
    document.getElementById("component-container").appendChild(svg);
}
