import {getScoreComponentBeatSubdivisionCount, getScoreComponentBeatSubdivisionDrums, getScoreComponentTimeSignatureNumerator} from "./files.js";

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
    //     CONTRACT-START:
    //     CONTRACT-END:
    //         - ratio
    //         - hooks
    // 
    // drums: A string array of the drumIDs to draw.
    // decorations: A string array of the symbolIDs to draw.
    // full-beams: The number (non-zero and positive) of full beams to draw between this instruction and the next instruction (with a stem, full beams go over rests).
    // broken-beams: The same full-beams except for broken-beams. This can be signed, where negative means to draw on the left, and positive to the right. It can also be zero - no broken-beams. If dots != 0 then this cannot be negative.
    // dots: The number (zero or positive) of dots that should be drawn after the stem. If broken-beams is negative (broken-beams on the left) then this must be 0 (no dots).
    // flags: The number (zero or positive) of flags to draw after the stem.
    // ticks: The number (zero or positive) of ticks to draw on a rest. Zero means it's a crotchet rest.
    // ratio: The length (positive integer) of notes to contracted into one beat. This is the number to be drawn between the start and end.
    // hooks: Should hooks (the lines that show where a contraction has effect) be drawn. This is true or false.
    // 
    // GROUPs connect to the next GROUP or GROUP-END, so must be followed by at least one of these.
    // A GROUP-END must follow a GROUP.
    // FLAGs stand alone so should not follow an un-ended GROUP. This means crotchets should be represented using a FLAG with flags=0.
    // Each CONTRACT-START must be closed by a CONTRACT-END, and must be closed before another CONTRACT can start.
    // RESTS and CONTRACTING-START/END can come anywhere between GROUPs and FLAGs.
    // 
    // CONTRACT groups are for contracting-ratios, they say notes inside this group (of the length given inside ratio) should be contracted so that they last the length of a single beat.
    
    // Instruction Types
    static get GROUP() {return "GROUP";}  // Declare like this so are immutable.
    static get GROUP_END() {return "GROUP_END";}
    static get FLAG() {return "FLAG";}
    static get REST() {return "REST";}
    static get CONTRACT_START() {return "CONTRACT_START";}
    static get CONTRACT_END() {return "CONTRACT_END";}

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
        } else if (type === RenderInstruction.CONTRACT_START) {
        } else if (type === RenderInstruction.CONTRACT_END) {
            this.ratio = args[0];
            this.hooks = args[1];
        } else {
            throw "Unkown type " + type;
        }

        
        // Object.freeze(this);  // So is immutable  // TODO: Freeze this again
    }
}

function calculateRhythmInformation(length, subdivisions) {
    // Calculates the rhythm info that is used to draw a duration of length / subdivisions of a beat.
    // Returns {beams: int, dots: int, length: int} where beams is the total number of beams (full and broken) that the stem at the start of this needs, and length is the actual of the returned beams and dots (as it may not be possbile to represent this length with just beams and dots).
    
    // So, to calculate the information, we pretend subdivisions is actually the highest power of two below what it actually is. This means (ignoring the number above) it would last longer than a beat, however the number we draw above the beams tells us to squish the notes closer together.
    // So for example, If we have a triplet with only the first note, we would draw a dotted crotchet, which is 1.5 beats, but then the 3 we write above it tells us to compress that into 1 beat.
    const pretendSubdivisions = 2**Math.floor(Math.log2(subdivisions));

    // Beams
    let beams = Math.ceil(Math.log(length / pretendSubdivisions) / Math.log(1/2));
    if (beams == 0 && subdivisions != 1) {  
        // If subdivisions == 1 then it is a crotechet, otherwise it's duration is less than a crotchet so it should have at least one beam. Except when using a subdivision like 3, we could have a this combo of lengths {2, 1}. The 2 has no beams, but the 1 does. Our beaming algorithm is not set up to handle that, so just force at least one beam and then have it add a rest or something.
        // I also feel it is easier to read.
        beams = 1;
    }
    
    // Dots
    let lengthLeft = length - pretendSubdivisions / 2**(beams);
    let dots = 0;
    while (lengthLeft != 0) {
        const sub = pretendSubdivisions / 2**(beams + dots + 1);
        if (Math.floor(sub) != sub) {
            break;
        }
        if (lengthLeft - sub < 0) {
            break;
        }
        lengthLeft -= sub;
        dots += 1;
    }

    return {beams, dots: dots, length: length - lengthLeft};
}

function gcd(a, b) {
    // Calculate the greatest common denominator of two numbers
    if (!b) {
    return a;
  }

  return gcd(b, a % b);
}

function gcdOfArray(array) {
    // Calculates the GCD of all the numbers in an array
    let current = array[0];
    for (let i=1; i<array.length; i++) {
        current = gcd(current, array[i]);
    }
    return current;
}

function preRenderScoreComponent(componentID) {
    // Figures out how to actaully draw the score-component.
    // This is like the overall idea, it tells us what we need to draw, not how. Specifically which drums, decorations on each subdivision, and what bars / dots / rests / flags to draw.

    let numerator = getScoreComponentTimeSignatureNumerator(componentID);
    
    
    const renderInstructions = [];
    // We do each beat separately
    for (let bi=0; bi < numerator; bi++) {  // BI: Beat Index
        const beatSubdivisions = getScoreComponentBeatSubdivisionCount(componentID, bi);

        // First, calculate the non-empty subdivision indexes:
        let nonEmptySubdivisionIndexes = [];  // Holds the indexes of non-empty subdivisions in this beat, relative to the start of the beat
        for (let si=0; si < beatSubdivisions; si ++) {  // SI: subdivisionIndex
            if (getScoreComponentBeatSubdivisionDrums(componentID, bi, si).length != 0) {
                nonEmptySubdivisionIndexes.push(si);
            }
        }
        console.log("1. BI:", bi, "BS:", beatSubdivisions, "NESI:", nonEmptySubdivisionIndexes);
        
        
        // Second, group all empty subdivisions after a non-empty subdivision with that non-empty subdivision.
        // We only need to store the lengths, as the lengths of all the groups before imply the index
        const sGroups = [];  // The lengths of each of these groups.
        if (nonEmptySubdivisionIndexes.length == 0) {  // Are there no non-empty subdivisions (so is the beat empty)?
            sGroups.push(beatSubdivisions);
        } else if (nonEmptySubdivisionIndexes[0] != 0) { // Is there a rest before any non-empty subdivisions?
            sGroups.push(nonEmptySubdivisionIndexes[0]);
        }
        // Now group the non-empty ones (not the last one)
        for (let i=0; i<nonEmptySubdivisionIndexes.length - 1; i++) {  // `- 1` as last handled below
            sGroups.push(nonEmptySubdivisionIndexes[i + 1] - nonEmptySubdivisionIndexes[i]);
        }
        // Group the last non-empty until the end of the beat
        if (nonEmptySubdivisionIndexes.length > 0) {  // Is there at least one?
            sGroups.push(beatSubdivisions - nonEmptySubdivisionIndexes[nonEmptySubdivisionIndexes.length - 1]);
        }
        console.log("2. BI:", bi, "BS:", beatSubdivisions, "SG:", sGroups);
        


        
        // Third, clean the sGroups:
        // Can we actually reduce the number of subdivisions (if we have 2, 2, 2 that can be 1, 1, 1)
        const subdivisionMultiplier = gcdOfArray(sGroups);  // The amount to multiply a subdivisons after this point to get indexes that can be used to lookup in the component info.
        for (let i=0; i<sGroups.length; i++) {
            sGroups[i] /= subdivisionMultiplier;
        }
        const relativeSubdivisions = beatSubdivisions / subdivisionMultiplier;
        console.log("3a. BI:", bi, "RS:", relativeSubdivisions, "SG:", sGroups);
        
        // Many of the sGroups are actually impossible due to limitations with beams and dots, and many will also cross beat boundaries (which they should not). So add rests where they are required.
        // We will work on the array in-place because then any rests we add that are illegal will be fixed in further iterations
        for (let i=0; i < sGroups.length; i++) {
            let rhythmInfo = calculateRhythmInformation(sGroups[i], beatSubdivisions);
            if (rhythmInfo.length != sGroups[i]) {  // Is the group an illegal length?
                const amountOver = sGroups[i] - rhythmInfo.length;
                if (amountOver <= 0) throw "amountOver <= 0";  

                // Split the group into two (the first must be a legal length, if the second isn't then it will be fixed in the next iteration).
                sGroups.splice(i, 1, rhythmInfo.length);  // Replace the old group
                sGroups.splice(i + 1, 0, amountOver);  // Put in the rest
            }
        }
        console.log("3b. BI:", bi, "RS:", relativeSubdivisions, "SG:", sGroups);

        
        // Fourth, get all the non-empty sGroups
        let si = 0;  // SI: subdivisionIndex. This should correspond to the start of the ith (see below) sGroup
        let nonEmptySGroups = [];  // The indexes of sGroups that aren't empty
        for (let i=0; i<sGroups.length; i++) {  // i: Index of curreng sGroup
            if (getScoreComponentBeatSubdivisionDrums(componentID, bi, si * subdivisionMultiplier).length != 0) { // Is non-empty?
                nonEmptySGroups.push(i);
            }
            si += sGroups[i];
        }
        

        // Fifth, convert groups to RenderInstructions
        // Add the CONTRACT-START (if we need it)
        const isStandardSubdivision = relativeSubdivisions == 2**Math.floor(Math.log2(relativeSubdivisions));  // Is subdivisions a power of two?
        if (!isStandardSubdivision) {  // We only need to tell the reader what the subdivision is for non-standard ones
            renderInstructions.push(new RenderInstruction(RenderInstruction.CONTRACT_START));
        }

        // Draw the actual content
        si = 0;  // Reset SI
        for (let i=0; i<sGroups.length; i++) {  // i: Index of current sGroup
            const rhythmInfo = calculateRhythmInformation(sGroups[i], relativeSubdivisions);
            if (nonEmptySGroups.includes(i)) {
                const drums = getScoreComponentBeatSubdivisionDrums(componentID, bi, si * subdivisionMultiplier);
                const decorations = [];  // TODO: Me
                if (nonEmptySGroups.length == 1) {
                    // i is the only non-empty sGroup, so draw a FLAG
                    renderInstructions.push(new RenderInstruction(RenderInstruction.FLAG, drums, decorations, rhythmInfo.beams, rhythmInfo.dots));
                } else if (i != nonEmptySGroups[nonEmptySGroups.length - 1]) {
                    // There are multiple non-empty sGroups, and this is not the last, so draw a GROUP
                    
                    // We need to figure out what combination of full-beams and broken-beams we need to draw for this current GROUP
                    const currentNonEmptyIndex = nonEmptySGroups.indexOf(i);
                    const c = rhythmInfo.beams;  // How many beams it wants connected to it
                    const n = calculateRhythmInformation(sGroups[nonEmptySGroups[currentNonEmptyIndex + 1]], relativeSubdivisions).beams;
                    const nn = ((currentNonEmptyIndex < nonEmptySGroups.length - 2) ? calculateRhythmInformation(sGroups[nonEmptySGroups[currentNonEmptyIndex + 2]], relativeSubdivisions).beams : 0);  // If a sGroup doesn't exist then it will supply no beams, so just say 0
                    const l = ((currentNonEmptyIndex > 0) ? calculateRhythmInformation(sGroups[nonEmptySGroups[currentNonEmptyIndex - 1]], relativeSubdivisions).beams : 0);  
                    
                    // Remember, beams go from c to n!
                    if (c == n) {  // Both want the same number of beams. So draw that.
                        renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, drums, decorations, c, 0, rhythmInfo.dots));
                    } else if (c < n && nn >= n) {  // Next wants more beams than current will give it, but nextnext is able to supply what it needs. So we only need to draw current (full) beams
                        renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, drums, decorations, c, 0, rhythmInfo.dots));
                    } else if (c < n && nn < n) {  // Next wants more beams than current will give it, and nextnext also won't supply enough. So draw c full (beams) and n-c half-beams on the right
                        renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, drums, decorations, c, n - c, rhythmInfo.dots)); 
                    } else if (c > n && l >= c) {  // If current wants more beams than next will supply, but last can supply enough. So draw n (full) beams
                        renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, drums, decorations, n, 0, rhythmInfo.dots));
                    } else if (c > n && l < c) {  // If current wants more beams than next will supply, and last can't supply enough beams
                        renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, drums, decorations, n, -(c - n), rhythmInfo.dots));  // Negative broken-beams means draw on left
                    } else {
                        throw "None of the beam logic cases worked, this shouldn't be possible, here are the values " + l + " " + c + " " + n + " " + nn;
                    }
                    
                    // In the case that we have drawn broken beams on both sides of a stem
                    const lastGroup = renderInstructions[renderInstructions.length - i - 1 + nonEmptySGroups[currentNonEmptyIndex - 1]];  // Will be null if it doesn't exist
                    const currentGroup = renderInstructions[renderInstructions.length - 1];
                    if (lastGroup != null && lastGroup.broken_beams > 0 && currentGroup.broken_beams < 0) {
                        // We only want to keep the side with the most full-beams
                        if (lastGroup.full_beams >= currentGroup.full_beams) {  // If both equal then point left
                            currentGroup.broken_beams = 0;
                        } else {
                            lastGroup.broken_beams = 0;
                            
                        }
                    }


                } else {
                    // There are multiple non-empty sGroups, and this is the last, so draw a GROUP_END
                    renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP_END, drums, decorations, rhythmInfo.dots));
                }


            } else {  
                // This is a rest, so it doesn't affect the beams (they go over it (unless this is at the start or end of the beat but it still doesn't matter)).
                renderInstructions.push(new RenderInstruction(RenderInstruction.REST, rhythmInfo.beams, rhythmInfo.dots));
            }

            si += sGroups[i];
        }
        
        // Add the CONTRACT-END (if we need it)
        if (!isStandardSubdivision) {  // We only need to tell the reader what the subdivision is for non-standard ones
            const needsHooks = nonEmptySGroups[0] != 0 || nonEmptySGroups[nonEmptySGroups.length - 1] != sGroups.length - 1;  // If we start or end with a rest then we will need hooks (as this algorithm will produce only one group of GROUPs per beat.
            renderInstructions.push(new RenderInstruction(RenderInstruction.CONTRACT_END, relativeSubdivisions, needsHooks));
        }

    }
    
    console.log("5. RI:", renderInstructions)

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
    let currentContractStartX = null;  // The starting x-coordinate of the current CONTRACT, or null if we are not in a contract
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
                } else if (instructions[i].type === RenderInstruction.REST) {
                    path = drawRest(svg, path, instructions, i, 50);
                    x += 10;  // Spacing
                } else if (instructions[i].type === RenderInstruction.GROUP) {
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
                } else {
                    throw "Unexpected instruction type " + instructions[i].type;
                }

                i += 1;
            }
            path += lastBeamPath.replaceAll("subX", (x-10).toString()).replaceAll("x", x.toString());
            lastBeamPath = "";
            path += "M" + x + " 0 " + "L" + x + " 100 ";
            drawDots(svg, x + 5, 0, instructions[i].dots);
        } else if (instructions[i].type === RenderInstruction.CONTRACT_START) {
            if (currentContractStartX != null) {
                throw "Cannot start contract when it's already open";
            }
            currentContractStartX = x;
        } else if (instructions[i].type === RenderInstruction.CONTRACT_END) {
            if (currentContractStartX == null) {
                throw "Cannot end un-opened contract";
            }
            // Create text to say what the subdivision is
            const centerX = (currentContractStartX + x) / 2;
            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.style.fontStyle = "italic";
            text.style.fontWeight = "bold";
            text.style.textAnchor = "middle";
            text.style.dominantBaseline = "hanging";
            text.innerHTML = instructions[i].ratio.toString();
            text.setAttribute("x", centerX);
            svg.appendChild(text);  // Needs to be before text.getBBox()
            let bbox = {width: 5 * text.innerHTML.length, height: 17};  //TODO: fix this -  text.getBBox();
            text.setAttribute("y", "-" + bbox.height + "px");
            // Draw hooks if we want them
            if (instructions[i].hooks) {
                path += "M" + currentContractStartX + " -2 L" + currentContractStartX + " " + (-bbox.height / 2) + " L" + (centerX - bbox.width / 2 - 5) + " " + (-bbox.height / 2) + " ";
                path += "M" + (centerX + bbox.width / 2 + 5) + " " + (-bbox.height / 2) + " L" + x + " " + (-bbox.height / 2) + " L" + x + " -2 ";
            }
            currentContractStartX = null;
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
