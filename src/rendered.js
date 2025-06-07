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
        
        Object.freeze(this);  // So is immutable
    }
}

function calculateFinalSubdivisionIndex(finalSubdivisions, componentID, base, further) {
    // Convert a base and further subdivision index to an index in a subdivision length of finalSubdivisions.
    // This is relative to the start of the bar.
    const furtherCount = getScoreComponentFurtherSubdivisionCount(componentID, base);
    const baseSubdivisions = getScoreComponentBaseSubdivisions(componentID);
    return (finalSubdivisions / baseSubdivisions * base) + (finalSubdivisions / baseSubdivisions / furtherCount * further);
}

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


        /*
        const currentIndex = nonEmptySubdivisionIndexes[i];
        const currentFinalIndex = calculateFinalSubdivisionIndex(finalSubdivisions, componentID, currentIndex.base, currentIndex.further);
        
        // If currentFinal != lastFinal then we need to have a rest
        if (currentFinalIndex != lastFinalIndex) {
            if (lastIndex.further != 0 && (lastIndex.base % baseSubdivisions == 0)) throw "Last did not end at the end of a beat but has requested a rest.";  // We can only have a rest at the start of a beat if it actually is the start of a beat
            // A rest cannot be longer than a crotchet, so split it up if necessary
            while (currentFinalIndex - lastFinalIndex > finalSubdivisions) {
                groups.push(lastIndex, finalSubdivisions);
                lastFinalIndex += finalSubdivisions;
                lastIndex = SubdivisionIndex(lastIndex.base + baseSubdivisions, 0);
            }
            // Now draw the smaller rest if necessary
            if (currentFinalIndex != lastFinalIndex) {
                groups.push(lastIndex, currentFinalIndex - lastFinalIndex);
                lastFinalIndex = currentFinalIndex;
                lastIndex = 
            }
        }
        */

        /*const isFirstNonEmpty = i == 0;
        const isLastNonEmpty = i == nonEmptySubdivisionIndexes.length - 1;
        const currentIndex = nonEmptySubdivisionIndexes[i];
        let lastIndex = nonEmptySubdivisionIndexes[i-1];

        // Beams cannot go over beat boundaries, so neither can groups.
        if (isFirstNonEmpty || (Math.floor(currentIndex.base / baseSubdivisions) != Math.floor(lastIndex / baseSubdivisions))) {
            if (isFirstNonEmpty) {  // Set it to (0,0) so we can calculate the distance from it
                lastIndex = SubdivisionIndex(0, 0);
            }

            // We need to get the rest length
            const last = calculateActualSubdivisionIndex(finalSubdivisions, componentID, lastIndex.base, lastIndex.further);
            const current = calculateActualSubdivisionIndex(finalSubdivisions, componentID, currentIndex.base, currentIndex.further);
            let length = current - last;

            // Now that is the length of rest that we need
            // However if the rest is over the length of a crotchet then we need to split it up into multiple
            while (length > finalSubdivisions) {
                length -= finalSubdivisions;
                groups.
            }
        }*/
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
        while (val > 0) {
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

    // We will work on the array in-place because then any rests we add that are illegal will be fixed in further iterations
    for (let i=0; i < sGroups.length; i++) {
        let group = sGroups[i];

        // Does group cross a beat boundary?
        if (group.index != null) {  // If index is null then we created it so it shouldn't be over a boundary
            let groupStartFinal = calculateFinalSubdivisionIndex(finalSubdivisions, componentID, group.index.base, group.index.further);
            let groupEndFinal = groupStartFinal + group.length - 1;  // We want the last final subdivision of this group, not the first of the next
            if (Math.floor(groupStartFinal / finalSubdivisions) != Math.floor(groupEndFinal / finalSubdivisions)) {
                // It does so we need to split it on the beat boundary.
                const amountOver = groupEndFinal % finalSubdivisions + 1;  // Because the first in the next beat is 1 over, not 0 over.
                let newLength = group.length - amountOver;

                // Check if we need to add crotchet rests
                let crotchetRestCount = 0;
                while (newLength >= finalSubdivisions) {
                    crotchetRestCount += 1;
                    newLength -= finalSubdivisions;
                }
                // Incase my logic is wrong
                if (newLength == 0) throw "newLength = 0"
                if (newLength < 0) throw "newLength < 0"

                // Split the group
                sGroups.splice(i, 1, new SubdivisionGroup(group.index, newLength));  // Replace the old group
                for (let n=0; n<crotchetRestCount; n++) { // Add crotchet rests
                    sGroups.splice(i + n + 1, 0, new SubdivisionGroup(null, finalSubdivisions));  // We can put null in because it is a rest.
                }
                sGroups.splice(i + crotchetRestCount + 1, 0, new SubdivisionGroup(null, amountOver));  // Add the smaller rest. We can put null because it is a rest.
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
        //const current = sGroups[i];

        /*// If current is empty then current is a rest
        if (current.drums().length == 0) {
            const rhythmInfo = current.rhythmInfo();
            renderInstructions.push(new RenderInstruction(RenderInstruction.REST, rhythmInfo.bars, rhythmInfo.dots));
            i++;
        } else {  // Group some groups together for beaming (or if there's only one then it's a FLAG)
        */    // We can just beam all the notes till the end of the bar. The groups already account for any necessary rests
        
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
            /*if (nonEmptySGroups.length == 0) {
                throw "nonEmptySGroups.length is 0, how did we even get here?";
            } else */if (nonEmptySGroups.length == 0 || nonEmptySGroups.length == 1) {  // It's only RESTs or it's RESTs and a FLAG
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
                while (i < j) {
                    if (sGroups[i].drums().length == 0) {  
                        // This is a rest, so it doesn't affect the beams (they go over it (unless this is at the start or end of the beat but it still doesn't matter)).
                        renderInstructions.push(new RenderInstruction(RenderInstruction.REST, sGroups[i].rhythmInfo().beams, sGroups[i].rhythmInfo().dots));
                        finalIndex += sGroups[i].length;
                        i++;
                    } else {
                        // This is not a rest, so calculate
                        //last = nonEmptySGroups[nonEmptyI - 1];  // If index is out of bounds then this will be null.
                        //current = nonEmptySGroups[nonEmptyI];
                        //next = nonEmptySGroups[nonEmptyI + 1];
                        //nextNext = nonEmptySGroups[nonEmptyI + 2];
                        //i++;
                        //nonEmptyI++;
                        
                        if (nonEmptyI < nonEmptySGroups.length - 1) { // Are there more non-empty groups to beam to?
                            // We need to figure out what combination of (full) beams and broken-beams we need to draw for this current GROUP
                            const c = nonEmptySGroups[nonEmptyI].rhythmInfo().beams;  // How many beams it wants connected to it
                            const n = nonEmptySGroups[nonEmptyI + 1].rhythmInfo().beams;
                            const nn = ((nonEmptyI < nonEmptySGroups.length - 2) ? nonEmptySGroups[nonEmptyI + 2].rhythmInfo().beams : 0);  // If a sGroup doesn't exist then it will supply no beams, so just say 0
                            const l = ((nonEmptyI > 0) ? nonEmptySGroups[nonEmptyI - 1].rhythmInfo().beams : 0);  
                            
                            // Remember, beams go from c to n!
                            if (c == n) {  // Both want the same number of beams. So draw that.
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[nonEmptyI].drums(), [], c, 0, sGroups[nonEmptyI].rhythmInfo().dots));
                            } else if (c < n && nn >= n) {  // Next wants more beams than current will give it, but nextnext is able to supply what it needs. So we only need to draw current (full) beams
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[nonEmptyI].drums(), [], c, 0, sGroups[nonEmptyI].rhythmInfo().dots));
                            } else if (c < n && nn < n) {  // Next wants more beams than current will give it, and nextnext also won't supply enough. So draw c full (beams) and n-c half-beams on the right
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[nonEmptyI].drums(), [], c, n - c, sGroups[nonEmptyI].rhythmInfo().dots)); 
                            } else if (c > n && l >= c) {  // If current wants more beams than next will supply, but last can supply enough. So draw n (full) beams
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[nonEmptyI].drums(), [], n, 0, sGroups[nonEmptyI].rhythmInfo().dots));
                            } else if (c > n && l < c/* && !(l < c && n < c)*/) {  // If current wants more beams than next will supply, and last can't supply enough beams, and we didn't draw right-broken-beams on the last nonEmptySGroup. So draw n (full) beams and c - n broken beams on the left
                                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, sGroups[nonEmptyI].drums(), [], n, -(c - n), sGroups[nonEmptyI].rhythmInfo().dots));  // Negative broken-beams means draw on left
                            } else {
                                throw "None of the beam logic cases worked, this shouldn't be possible, here are the values " + l + " " + c + " " + n + " " + nn;
                            }
                            

                        } else { // This is the last non-empty sGroup so this is a GROUP-END
                            renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP_END, sGroups[i].drums, [], sGroups[i].rhythmInfo().dots));
                        }

                        finalIndex += sGroups[i].length;
                        i++;
                        nonEmptyI++;
                    }
                }
            }
    

                /*const last = sGroups[i - 1];
                const current = sGroups[i];
                const next = sGroups[i + 1];
                const nextNext = sGroups[i + 2];
                
                const fullBeams = Math.min(current.rhythmInfo().beams, next.rhythmInfo().beams);
                if (fullBeams < current.rhythmInfo().beams && (last == null || last.rhythmInfo().beams < current.rhythmInfo().beams)) {  // fullBeams is not enough beams for current and last also doesn't supply enough. If last is null then it cannot supply any beams
                    brokenBeams = fullBeams - current.rhythmInfo().beams;  // Negative as draw on left
                } else if (fullBeams < next.rhythmInfo().beams && (nextNext == null || nextNext.rhythmInfo().beams < next.rhythmInfo().beams)) {  // fullBeams is not enough beams for next and nextNext also doesn't supply enough. If nextNext is null then it cannot supply any beams. Next cannot be null due to the loop condition
                    brokenBeams = current.rhythmInfo().beams - fullBeams;  // Positive as draw on right
                }
                renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP, current.drums(), [], fullBeams, brokenBeams, current.dots));

                i++;*/
            /*}
            // Create GROUP-End
            renderInstructions.push(new RenderInstruction(RenderInstruction.GROUP_END, sGroups[i].drums(), [], sGroups[i].dots));
            i++;*/
        //}
    }

    return renderInstructions;
}


function renderScoreComponent(componentID) {
    // Renders a score component. This returns a svg node.
    // This does not attach the event handling stuff.
    let instructions = preRenderScoreComponent(componentID);
    console.log(instructions);
    // TODO: Process sizing first?
    // Then draw.
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
