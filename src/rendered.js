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
    const renderInstructions = [];
    for (let i=0; i<groups.length; i++) {
        const currentIndex = groups[i].index;
        const currentLength = groups[i].length;
        const currentIsEmpty = getScoreComponentFurtherSubdivisionDrums(componenetID, currentIndex.base, currentIndex.further).length == 0;

        // If i is empty then i must be a rest
        if (currentIsEmpty) {
            
        }
    }
}


function renderScoreComponent(componentID) {
    // Renders a score component. This returns a svg node.
    // This does not attach the event handling stuff.
    let instructions = preRenderScoreComponent(componentID);
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
