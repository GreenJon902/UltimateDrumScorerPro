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

function loadDrumsSVG(callback) {
    // Runs the given function with the argument of groups defined in drums.svg.

    // Get SVG
    fetch("drums.svg").then(response =>  response.text()).then (text => {
        // Parse SVG and give to callback
        const parser = new DOMParser();
        const svg = parser.parseFromString(text, "text/xml");
        const children = svg.getElementById("defs").children;
        callback(children);
    });
    
    }

function calculateSpacing(instructions) {
    // Returns some information on how to draw the given instructions.
    // It returns {
    //     instructionXs: [int] - The x coordinate of a stem, or the right edge of a REST. It is the start and end of a CONTRACT_START/END pair.
    //     drumYs: {str: int} - A map from drumID to drum anchor (where the stem connects to the head) y level.
    //     restCenterY: int - The y line where all rests should be centered on
    //     width: int, height: int  - The width and height of the SVG to be drawn
    //  }


    loadDrumsSVG(DRUMS => {
        // Get DRUMS as a map if we need it
        const DRUMS_MAP = {};
        for (let i=0; i<DRUMS.length; i++) {
            DRUMS_MAP[DRUMS[i].id] = DRUMS[i];
        } 

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
                        const dotWidth = lastGroupInstr.dots * 5;
                        let rhythmWidth;
                        if (lastGroupInstr.broken_beams < 0) {  // Are broken beams on left?
                            const brokenBeamWidth = 5;
                            rhythmWidth = Math.max(dotWidth, brokenBeamWidth);
                        } else if (lastGroupInstr.broken_beams > 0) {  // Are broken beams on right?
                            const brokenBeamWidth = 5;  
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
                        const headWith = maxLastInstrRight + maxInstrLeft;

                        // Figure out the actual width
                        const width = Math.max(rhythmWidth, headWith);
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
                        const dotWidth = 5 * instr.dots - 5 * instr.ticks - 5;
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
                const dotWidth = instr.dots * 5;
                x += Math.max(flagWidth, dotWidth);
            } else if (type === RenderInstruction.REST) {
                // Does not take up space afterwards
            } else if (type === RenderInstruction.GROUP_END) {
                // Account for dots
                const dotWidth = (instr.dots * 5);
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
                const maxBeams = instr.full_beams + Math.abs(instr.broken_beams);
                const dotHeight = (instr.dots === 0) ? 0 : 5;
                const height = maxBeams * 5 + dotHeight;
                tallestRhythm = Math.max(tallestRhythm, height);
            } else if (instr.type === RenderInstruction.FLAG) {
                const flagHeight = 5 * instr.flags;
                const dotHeight = (instr.dots === 0) ? 0 : 5;
                const height = flagHeight + dotHeight;
                tallestRhythm = Math.max(tallestRhythm, height);
            } else if (instr.type === RenderInstruction.GROUP_END) {
                const dotHeight = (instr.dots === 0) ? 0 : 5;
                const height = dotHeight;
                tallestRhythm = Math.max(tallestRhythm, height);
            }
        }
        console.log("4. TRh:", tallestRhythm);

        // Fifth, calculate the tallest rest
        let tallestRest = 0;
        for (let i=0; i<instructions.length; i++) {
            const instr = instructions[i];
            if (instr.type === RenderInstruction.REST) {
                if (instr.ticks === 0) {  // Is crotchet rest?
                    tallestRest = Math.max(tallestRest, 10);
                } else {
                    tallestRest = Math.max(tallestRest, 5 * instr.ticks);
                }
            }
        }
        console.log("5. TRe", tallestRest);
        
        // Sixth, combind height information and return
        const headHeight = parseInt(USED_DRUMS[0].dataset.sizeUp) + drumYs[drumYs.length - 1] + parseInt(USED_DRUMS[USED_DRUMS.length - 1].dataset.sizeDown);  // Distance from top of top drum to bottom of last drum
        const underRhythmHeight = Math.max(tallestRest, headHeight);  // Height of stuff under beams
            
        const restCenterY = tallestRhythm + (underRhythmHeight / 2);
        const height = tallestRhythm + underRhythmHeight;
        
         // Center heads in underRhythmHeight and move to be under beams and make it so drumID points to y-coord
        const drumYsMap = {};
        for (let i=0; i<drumYs.length; i++) {
            drumYsMap[USED_DRUMS[i].id] = drumYs[i] + (underRhythmHeight - headHeight) / 2 + parseInt(USED_DRUMS[0].dataset.sizeUp) + tallestRhythm;            
        }

        let ret = {
            instructionXs,
            drumYs: drumYsMap,
            restCenterY,
            width,
            height
        };
        console.log("6. RE:", ret);
        return ret;
    });
}

function renderScoreComponent(componentID) {
    // Renders a score component. This returns a svg node.
    // This does not attach the event handling stuff.
    let instructions = preRenderScoreComponent(componentID);
    let spacing = calculateSpacing(instructions);
    //draw(instructions, spacing);
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
    //svg.setAttribute("id", componentType + "_" + componentID);
    //document.getElementById("component-container").appendChild(svg);
}
