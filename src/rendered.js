import {getScoreComponentBeatSubdivisionCount, getScoreComponentBeatSubdivisionDrums, getScoreComponentTimeSignatureNumerator, getComponentX, getComponentY, getTextComponentFontSize, getTextComponentTextContent, setComponentX, setComponentY} from "./files.js";
import {setEditComponent} from "./editor.js";

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
    //         - ratio
    //         - hooks
    //     CONTRACT-END:
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
            this.ratio = args[0];
            this.hooks = args[1];
        } else if (type === RenderInstruction.CONTRACT_END) {
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
    let beams = Math.ceil(Math.log2(pretendSubdivisions / length));
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
            let rhythmInfo = calculateRhythmInformation(sGroups[i], relativeSubdivisions);
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
            const needsHooks = nonEmptySGroups[0] != 0 || nonEmptySGroups[nonEmptySGroups.length - 1] != sGroups.length - 1;  // If we start or end with a rest then we will need hooks (as this algorithm will produce only one group of GROUPs per beat.
            renderInstructions.push(new RenderInstruction(RenderInstruction.CONTRACT_START, relativeSubdivisions, needsHooks));
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
            renderInstructions.push(new RenderInstruction(RenderInstruction.CONTRACT_END));
        }

    }
    
    console.log("5. RI:", renderInstructions)

    return renderInstructions;
}

function loadDrumsSVG() {
    // Loads the SVG information for each of the drums, returns an array ordered in height to draw at, and a map from drumID to svg node.
    // Return is {array, map}.

    // Get SVG
    let drumsSVG = Array.from(document.getElementById("drums").getElementById("defs").children);
    // Make a map from drumID to node too
    const drumsSVGMap = {};
    for (let i=0; i<drumsSVG.length; i++) {
        drumsSVGMap[drumsSVG[i].id] = drumsSVG[i];
    }
    // Return
    return {array: drumsSVG, map: drumsSVGMap};
}

function getTextSize(string, fontSize) {
	const svg = document.getElementById("text-svg");
	const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.innerHTML = string;
    if (fontSize !== null) {
    	text.style.fontSize = fontSize + "px";  // The SVG scales 1px to 1mm so use px
    }
    svg.appendChild(text);
    const bbox = text.getBBox();
    const mmToPx = 1;//parseFloat(window.getComputedStyle(svg, null).height);  // SVG height is 1mm, so we can use it to scale pixels to mm
    const size = {left: bbox.x / mmToPx, up: bbox.y / mmToPx, width: bbox.width / mmToPx, height: bbox.height / mmToPx};
    //svg.removeChild(text);
    return size;
}

function calculateSpacing(instructions) {
    // Returns some information on how to draw the given instructions.
    // It returns {
    //     instructionXs: [int] - The x coordinate of a stem, or the right edge of a REST. It is the start and end of a CONTRACT_START/END pair.
    //     drumYs: {str: int} - A map from drumID to drum anchor (where the stem connects to the head) y level.
    //     restCenterYs: [int] - The y line where rests should be centered on. The index is the number of the rest as they come in instructions.
    //     contractCenterYs: [int] - The y line where contracts should be centered on. The index is the number of the contract (one for each pair) as they come in instructions.
    //     stemStartYs: [int] - The y level where stems (and hence beams and flags and dots) should be start being drawn on (so the top). The index is the number of the stem as they come in instructions.
    //     width: int, height: int  - The width and height of the SVG to be drawn
    //  }

    let {array: DRUMS, map: DRUMS_MAP} = loadDrumsSVG();
    
    // Get a list of the DRUMS that are. Order is preserved.
    const usedDrumsSet = new Set();
    instructions.filter(instruction => [RenderInstruction.GROUP, RenderInstruction.GROUP_END, RenderInstruction.FLAG].includes(instruction.type)).forEach(instruction => instruction.drums.forEach(drumID => usedDrumsSet.add(DRUMS_MAP[drumID])));
    const USED_DRUMS = Array.from(DRUMS).filter(drum => usedDrumsSet.has(drum));
    
    // First, calculate the spacing between each instruction
    const instructionXs = [];  // Where the stem should be drawn, or the right hand edge for rests. Indexes refer to instruction too
    let x = 0;
    for (let i=0; i<instructions.length; i++) {
        let instr = instructions[i];  // If i is changed then this should be changed to reflect that
        let type = instr.type;  // If i is changed then this should be changed to reflect that
        /*const lastType = (i > 0) ? instructions[i - 1].type : null;*/
        // We need x to be the stem or the right edge of a rest, so shift it along
        if (type === RenderInstruction.FLAG/* || (type === RenderInstruction.GROUP && lastType !== RenderInstruction.GROUP)*/) {
            // Account for width of note heads
            const headWidth = Math.max(...instr.drums.map(id => DRUMS_MAP[id].dataset.sizeLeft));
            x += headWidth
        } else if (type === RenderInstruction.REST) {
            // Account for width of rest
            if (instr.ticks == 0) {  // Is crotchet rest
                x += 5;
            } else {  // Is non-crotechet rest
                x += 5 * instr.ticks;  
            }
        } else if (type === RenderInstruction.GROUP) {
            // Account for width of note heads (before first stem in group)
            const headWidth = Math.max(...instr.drums.map(id => DRUMS_MAP[id].dataset.sizeLeft));
            x += headWidth
            instructionXs.push(x);

            // Save the current group for later
            let lastGroupI = i;
            i ++;
            while (true) {
                instr = instructions[i];
                type = instructions[i].type;
                if (type === RenderInstruction.REST) {
                    // Account for right of last note heads
                    const lastInstr = instructions[i - 1];
                    if (lastInstr.type === RenderInstruction.GROUP) {
                        const maxLastInstrRight = Math.max(...lastInstr.drums.map(id => DRUMS_MAP[id].dataset.sizeRight));
                        x += maxLastInstrRight;
                    }

                    // Account for width of rest
                    if (instr.ticks == 0) {  // Is crotchet rest
                        throw "Cannot have crotchet rest after un-ended GROUP";
                    } else {  // Is non-crotechet rest
                        x += 5 * instr.ticks;  
                    }
                } else if (type === RenderInstruction.GROUP || type === RenderInstruction.GROUP_END) {
                    // Calculate minimum rhythmWidth
                    const lastGroupInstr = instructions[lastGroupI];
                    const dotWidth = lastGroupInstr.dots * 2 + ((lastGroupInstr.dots === 0) ? 0 : 2);  // Add extra space if there are dots so they don't collide with next thing
                    let rhythmWidth;
                    if (lastGroupInstr.broken_beams < 0) {  // Are broken beams on left?
                        const brokenBeamWidth = 5 + 5;  // Plus five so broken beams don't connect to current stem  
                        rhythmWidth = Math.max(dotWidth, brokenBeamWidth);
                    } else if (lastGroupInstr.broken_beams > 0) {  // Are broken beams on right?
                        const brokenBeamWidth = 5 + ((lastGroupInstr.dots === 0) ? 5 : 0);  // Plus five so broken beams don't connect to last stem. If dots then won't connect anyway
                        rhythmWidth = dotWidth + brokenBeamWidth;
                    } else {  // No broken beams
                        rhythmWidth = dotWidth;
                    }

                    // Calculate minimum space used by note heads
                    const lastInstr = instructions[i - 1];
                    let maxLastInstrRight;
                    if (lastInstr.type === RenderInstruction.GROUP) {
                        maxLastInstrRight = Math.max(...lastInstr.drums.map(id => DRUMS_MAP[id].dataset.sizeRight));
                    } else {
                        maxLastInstrRight = 0;  // RESTs take up no space to the right
                    }
                    let maxInstrLeft = Math.max(...instr.drums.map(id => DRUMS_MAP[id].dataset.sizeLeft));
                    const headWidth = maxLastInstrRight + maxInstrLeft;

                    // Figure out the actual width
                    let width;
                    if (x - instructionXs[lastGroupI] + headWidth >= rhythmWidth) {  // Is the distance including rests bigger than rhythmWidth?
                        width = headWidth;
                    } else {
                        width = rhythmWidth;
                    }
                    x += width;

                    // If GROUP_END then exit
                    if (type === RenderInstruction.GROUP_END) {
                        break;
                    }
                    lastGroupI = i;
                } else {
                    throw "Unexpected instruction type";
                }
                instructionXs.push(x);
                if (type === RenderInstruction.REST) {
                    // Account for rest dots if we have them
                    const dotWidth = 2 + 2 * instr.dots - 5 * instr.ticks;
                    if (dotWidth > 0) {
                        x += dotWidth;
                    }
                }
                i++;
            }
        } else if (type === RenderInstruction.CONTRACT_START || type === RenderInstruction.CONTRACT_END) {
            // These don't take up any width
        } else {  // GROUP_ENDs intentionally come here, it should be a GROUP
            throw "Unexpected instruction type";
        }
        instructionXs.push(x);
        // Shift x along for any extra padding we want
        if (type === RenderInstruction.FLAG) {
            // Acount for flags and dots
            const flagWidth = (instr.flags == 0) ? 0 : 5;
            const dotWidth = instr.dots * 2 + ((instr.dots === 0) ? 0 : 2);  // +2 if dots so doesn't collide with thing after
            x += Math.max(flagWidth, dotWidth);
        } else if (type === RenderInstruction.REST) {
            // Account for width of dots if longer than rest
            const dotWidth = (instr.dots * 2) + ((instr.dots === 0) ? 0 : 2);  // +2 if dots so doesn't collide with thing after
            const restWidth = 5 * instr.ticks;
            x += Math.max(restWidth, dotWidth) - restWidth;  // Only add that which extends further than rest width
        } else if (type === RenderInstruction.GROUP_END) {
            // Account for dots
            const dotWidth = (instr.dots * 2) + ((instr.dots === 0) ? 0 : 2);  // +2 if dots so doesn't collide with thing after
            x += dotWidth;
        } else if (type === RenderInstruction.CONTRACT_START || type === RenderInstruction.CONTRACT_END) {
            // These don't take up any width
        } else {  // GROUPs intentionally come here, it should be a GROUP_END
            throw "Unexpected instruction type";
        }   
    }
    let width = x;
    console.log("1. IX:", instructionXs, "W:", width);

            
    // Second, calculate which drumIDs exist on the same beat
    const drumCollisions = {};  // Maps from drumID to set of drumIDs
    for (let i=0; i<instructions.length; i++) {
        if (![RenderInstruction.GROUP, RenderInstruction.GROUP_END, RenderInstruction.FLAG].includes(instructions[i].type)) continue;

        for (let j=0; j<instructions[i].drums.length; j++) {
            for (let k=0; k<instructions[i].drums.length; k++) {
                if (j != k) {
                    const jID = instructions[i].drums[j];
                    const kID = instructions[i].drums[k];
                    if (drumCollisions[jID] === undefined) {
                        drumCollisions[jID] = new Set();
                    }
                    drumCollisions[jID].add(kID);
                }
            }
        }
    }
    console.log("2. DC:", drumCollisions);

    // Third, calculate the relative (to the anchor of the head above it) Y of each drum
    const drumYs = [];  // Index matches to USED-DRUMS, value is anchor Y.
    let amountShifted = 0;  // The total amount that the (current) bottom drum has been shifted down.
    for (let i=0; i<USED_DRUMS.length; i++) {  
        const currentDrum = USED_DRUMS[i];
        let y = parseInt(currentDrum.dataset.beamSpacing) + amountShifted;  // Add amount shifted to retain minimum distance between notes like kicks and snares
        
        // Check if this drum will colide with a drum above it
        for (let j=0; j<drumYs.length; j++) {
            if (drumCollisions[currentDrum.id] !== undefined && drumCollisions[currentDrum.id].has(USED_DRUMS[j].id)) {  // Does i exist in the same beat as j (and hence have potentially actually colide)?
                if (y - parseInt(currentDrum.dataset.sizeUp) < drumYs[j] + parseInt(USED_DRUMS[j].dataset.sizeDown)) {  // Does i actually colide with j?
                    // Shift i down so it doesn't collide with j.
                    const newY = drumYs[j] + parseInt(USED_DRUMS[j].dataset.sizeDown) + parseInt(currentDrum.dataset.sizeUp);
                    amountShifted += newY - y;
                    y = newY;
                }
            }
            // Carry on looping as we may collide with another drum at the same height as j but is taller
        }

        drumYs.push(y);
    }
    console.log("3. DY:", drumYs);
    
    // Fourth, calculate the tallest beam + dots
    let tallestRhythm = 0;
    for (let i=0; i<instructions.length; i++) {
        const instr = instructions[i];
        if (instr.type === RenderInstruction.GROUP) {
            const fullBeamHeight = instr.full_beams * 2;
            const dotHeight = (instr.dots === 0) ? 0 : 2;
            const brokenBeamHeight = Math.abs(instr.broken_beams) * 2;
            let height;
            if (instr.broken_beams < 0) {  // Dots under broken beams
                height = fullBeamHeight + brokenBeamHeight + dotHeight;
            } else {  // Dots next to broken beams
                height = fullBeamHeight + Math.max(brokenBeamHeight, dotHeight);
            }
            tallestRhythm = Math.max(tallestRhythm, height);
        } else if (instr.type === RenderInstruction.FLAG) {
            const flagHeight = 5 * instr.flags;
            const dotHeight = (instr.dots === 0) ? 0 : 5;
            const height = flagHeight + dotHeight + 2;  // Dots can't be at very top or touch flags
            tallestRhythm = Math.max(tallestRhythm, height);
        } else if (instr.type === RenderInstruction.GROUP_END) {
            const dotHeight = (instr.dots === 0) ? 0 : 5;
            const height = dotHeight;
            tallestRhythm = Math.max(tallestRhythm, height);
        }
    }
    console.log("4. TRh:", tallestRhythm);

    // Fifth, calculate the tallest rest, also count the rests
    let tallestRest = 0;
    let restCount = 0;
    for (let i=0; i<instructions.length; i++) {
        const instr = instructions[i];
        if (instr.type === RenderInstruction.REST) {
            restCount += 1;
            if (instr.ticks === 0) {  // Is crotchet rest?
                tallestRest = Math.max(tallestRest, 15);
            } else {
                tallestRest = Math.max(tallestRest, 5 * instr.ticks);
            }
        }
    }
    console.log("5. TRe:", tallestRest);
    
    // Sixth, find out if we have any contracts we need to account for, and how many there are
    let contractCount = 0;
    for (let i=0; i<instructions.length; i++) {
        if (instructions[i].type === RenderInstruction.CONTRACT_START) {  // All contracts that open should close so only need to check open
            contractCount += 1;
        }
    }
    console.log("6. CC:", contractCount);

    // Seventh, find out how many stems there are
    let stemCount = 0;
    for (let i=0; i<instructions.length; i++) {
        if ([RenderInstruction.GROUP, RenderInstruction.GROUP_END, RenderInstruction.FLAG].includes(instructions[i].type)) {
            stemCount += 1;
        }
    }
    console.log("7. SC:", stemCount);
    
    // Eighth, combind height information and return
    const contractHeight = (contractCount === 0) ? 0 : 5;

    let headHeight;
    if (USED_DRUMS.length != 0) {
        headHeight = parseInt(USED_DRUMS[0].dataset.sizeUp) + drumYs[drumYs.length - 1] + parseInt(USED_DRUMS[USED_DRUMS.length - 1].dataset.sizeDown);  // Distance from top of top drum to bottom of last drum
    } else {
        headHeight = 0;
    }
    const underRhythmHeight = Math.max(tallestRest, headHeight);  // Height of stuff under beams
        
    const restCenterY = contractHeight + tallestRhythm + (underRhythmHeight / 2);
    const restCenterYs = new Array(restCount).fill(restCenterY);
    const height = contractHeight + tallestRhythm + underRhythmHeight;
    
    const contractCenterYs = new Array(contractCount).fill(contractHeight / 2);
    const stemStartYs = new Array(stemCount).fill(contractHeight);
    
     // Center heads in underRhythmHeight and move to be under beams and make it so drumID points to y-coord
    const drumYsMap = {};
    for (let i=0; i<drumYs.length; i++) {
        drumYsMap[USED_DRUMS[i].id] = drumYs[i] + (underRhythmHeight - headHeight) / 2 + parseInt(USED_DRUMS[0].dataset.sizeUp) + tallestRhythm + contractHeight;            
    }

    let ret = {
        instructionXs,
        drumYs: drumYsMap,
        restCenterYs,
        contractCenterYs,
        stemStartYs,
        width,
        height
    };
    console.log("8. RE:", ret);
    return ret;
}

function drawDots(svg, x, y, n) {
    // Draw n dots, starting at x, y, and add them to the svg
    for (let _=0; _<n; _++) {
        const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        dot.setAttribute("r", "0.6");  // Six seems to look about like 1 stroke-width
        dot.setAttribute("cx", x);
        dot.setAttribute("cy", y);
        svg.appendChild(dot);
        x += 2;
    }
}

function draw(instructions, spacing) {
    // Draws the given instructions (the result from preRenderScoreComponent) using the spacing information (from calculateSpacing).
    // Returns a svg node.
    // This does not add any event bindings.
    
    // Create SVG node
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", `${spacing.width}mm`);
    svg.setAttribute("height", `${spacing.height}mm`);
    svg.setAttribute("viewBox", `0 0 ${spacing.width} ${spacing.height}`)
    
    // Add content to SVG
    const path = [];  // Array holding parts of the paths
    
    let lastGroupI = null;  // Index of last group, null we aren't in a group of GROUPs (so if it's been ended).
    let currentContractI = null;  // Index of the current contract's CONTRACT_START, or null if we're not in a contract.
    let restI = 0;  // How many rests we have hit so far
    let stemI = 0;  // How many stems we have hit so far
    let contractI = 0;  // How many contracts we have hit so far
    for (let i=0; i<instructions.length; i++) {
        const instr = instructions[i];
        if (instr.type === RenderInstruction.REST) {
            let right = spacing.instructionXs[i];
            let centerY = spacing.restCenterYs[restI];
            
            path.push(`M${right} ${centerY}`);
            if (instr.ticks === 0) {  // Is it a crotchet rest?
                path.push("m-5 -7.5 l5 5 l-5 5 l5 5");
                if (instr.dots !== 0) throw "Crotchet rest cannot have dots";
            } else {
                path.push(`m-${5 * instr.ticks} ${5 * instr.ticks / 2}`)
                for (let _=0; _<instr.ticks; _++) {
                    path.push("l5 -5 m-2.5 2.5 l-2.5 -2.5 m5 0");
                }
                drawDots(svg, right - 5 * (instr.ticks) + 2, centerY + 5 * instr.ticks / 2, instr.dots);
            }


            restI++;
        } else if ([RenderInstruction.GROUP, RenderInstruction.GROUP_END, RenderInstruction.FLAG].includes(instr.type)) {
            // Draw heads
            const anchorX = spacing.instructionXs[i];
            let highestAnchorY = 0;  // Lowest down, but highest number
            for (let drumI=0; drumI<instr.drums.length; drumI++) {
                const anchorY = spacing.drumYs[instr.drums[drumI]];
                highestAnchorY = Math.max(highestAnchorY, anchorY);
                
                const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
                use.setAttribute("transform", `translate(${anchorX} ${anchorY})`);
                use.setAttribute("href", `#${instr.drums[drumI]}`);
                svg.appendChild(use);
            }

            // Draw stem
            path.push(`M${anchorX} ${spacing.stemStartYs[stemI]} L${anchorX} ${highestAnchorY}`);
            
            // Draw flags if we need to
            if (instr.type === RenderInstruction.FLAG) {
                const lastAnchorX = spacing.instructionXs[i];
                for (let n=0; n<instr.flags; n++) {
                    path.push(`M${lastAnchorX} ${spacing.stemStartYs[stemI] + n * 5} l5 5`);
                }
            }

            // Draw beams if we need to
            if (instr.type === RenderInstruction.GROUP || instr.type === RenderInstruction.GROUP_END) {
                if (lastGroupI != null) {  // Is there an unended group before that needs beams from it to here?
                    // We want to draw beams from the last group to the current group.
                    // The last group stores the beaming information we need
                    const full_beams = instructions[lastGroupI].full_beams;
                    const broken_beams = instructions[lastGroupI].broken_beams;
                    const lastAnchorX = spacing.instructionXs[lastGroupI];
                    let y = spacing.stemStartYs[stemI];
                    for (let _=0; _<full_beams; _++) {  // Full beams
                        path.push(`M${lastAnchorX} ${y} L${anchorX} ${y}`);
                        y += 2;
                    }
                    for (let _=0; _<broken_beams; _++) {  // Right half beams
                        path.push(`M${anchorX - 5} ${y} L${anchorX} ${y}`);
                        y += 2;
                    }
                    for (let _=0; _>broken_beams; _--) {  // Left half beams
                        path.push(`M${lastAnchorX} ${y} L${lastAnchorX + 5} ${y}`);
                        y += 2;
                    }
                }  
                // Update last group accordingly
                if (instr.type === RenderInstruction.GROUP_END) {
                    lastGroupI = null;  // Not in a group of GROUPs anymore so set to null
                } else {
                    lastGroupI = i;
                }
            }
            
            // Draw dots
            let y = spacing.stemStartYs[stemI];
            if (instr.type === RenderInstruction.GROUP) {
                y += 2 * (Math.max(0, -instr.broken_beams) + instr.full_beams);  // It draws next to right beams and under left beams
            } else if (instr.type === RenderInstruction.FLAG) {
                y += 5 * instr.flags + 2;
            }
            drawDots(svg, anchorX + 2, y, instr.dots);
            
            // Update trackers
            stemI += 1;
        } else if (instr.type === RenderInstruction.CONTRACT_START) {
            if (currentContractI !== null) throw "Tried to start CONTRACT inside of CONTRACT";
            currentContractI = i;
        } else if (instr.type === RenderInstruction.CONTRACT_END) {
            if (currentContractI === null) throw "Tried to end CONTRACT when not inside of CONTRACT";
            const centerY = spacing.contractCenterYs[contractI];
            const startX = spacing.instructionXs[currentContractI];
            const endX = spacing.instructionXs[i];
            const centerX = (startX + endX) / 2;
            
            // Create text node
            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.innerHTML = instructions[currentContractI].ratio.toString();
            text.setAttribute("x", centerX);
            text.setAttribute("y", centerY);
            svg.appendChild(text);
            
            // Create hooks if we need them
            if (instructions[currentContractI].hooks) {
                const htw = getTextSize(instructions[currentContractI].ratio.toString(), null).width / 2;  // Half of text width
                path.push(`M${startX} ${centerY + 2.5} l0 -2.5 L${centerX - htw} ${centerY} M${centerX + htw} ${centerY} L${endX} ${centerY} l0 2.5`);
            }
            
            // Update trackers
            currentContractI = null;
            contractI += 1;
        } else {
            throw "Unexpected instruction type"
        }
    }

    // Convert path to an actual node and add it
    const pathNode = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathNode.setAttribute("d", path.join(" "));
    svg.appendChild(pathNode);

    // Return it
    return svg;
}

function renderScoreComponent(componentID) {
    // Renders a score component. This returns a svg node.
    // This does not attach the event handling stuff.
    const instructions = preRenderScoreComponent(componentID);
    const spacing = calculateSpacing(instructions);
    const svg = draw(instructions, spacing);
    return svg;
}   

function attachEvents(componentType, componentID, svg) {
    // Attach the event handlers for the given component
    
    const container = document.getElementById("component-container");
    svg.onmousedown = (downEvent) => {
        const svgRect = svg.getBoundingClientRect();
        const parentRect = container.getBoundingClientRect();
        let moved = false;
        document.onmousemove = (moveEvent) => {
            const newX = (svgRect.left - parentRect.left + moveEvent.clientX - downEvent.clientX) / parentRect.width;
            const newY = (svgRect.top - parentRect.top + moveEvent.clientY - downEvent.clientY) / parentRect.height;
            setComponentX(componentType, componentID, newX);
            setComponentY(componentType, componentID, newY);
            svg.style.left = (newX * 100) + "%";
            svg.style.top = (newY * 100) + "%";

            moved = true;
        }
        document.onmouseup = (upEvent) => {
            document.onmousemove = null;
            document.onmouseup = null;
            
            if (!moved) {
                setEditComponent(componentType, componentID);
            }
        }
    }
}

function renderTextComponent(componentID) {
    // Renders a text component. This returns a svg node.
    // This does not attach the event handling stuff.
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.innerHTML = getTextComponentTextContent(componentID);
    text.style.fontSize = getTextComponentFontSize(componentID) + "px";  // The SVG scales 1px to 1mm so use px
    svg.appendChild(text);
    const size = getTextSize(getTextComponentTextContent(componentID), getTextComponentFontSize(componentID));
    svg.setAttribute("width", size.width + "mm");  
    svg.setAttribute("height", size.height + "mm");
    svg.setAttribute("viewBox", `${size.left} ${size.up} ${size.width} ${size.height}`);  // Center text in viewbox and scale 1px to 1mm
    return svg;

}

export function renderComponent(componentType, componentID) {
	// Render the given component. If it already exists then it will be removed.
    
    // First delete it if it already exists
    let old = document.getElementById(componentType + "_" + componentID);
    if (old !== null) {
        old.remove();
    }

    const renderFunc = {
        "score-component": renderScoreComponent,
        "text-component": renderTextComponent
    }[componentType];
    
    if (renderFunc === undefined) throw "Not Implemented";

    // Now let's render it ----------------------------------
    const svg = renderFunc(componentID);
    svg.setAttribute("id", componentType + "_" + componentID);
    document.getElementById("component-container").appendChild(svg);
    svg.style.left = (getComponentX(componentType, componentID) * 100) + "%";
    svg.style.top = (getComponentY(componentType, componentID) * 100) + "%";
    attachEvents(componentType, componentID, svg);
}
