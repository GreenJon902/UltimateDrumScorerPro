import {ComponentManager} from "../componentManager.js";

export class RenderInstruction {
    // Render instructions are produced from data in the ComponentManager, and dictate exactly what needs to be drawn. 
    // They allow the actual drawing function to ignore the calculations required for beams, etc.
    //
    // There are a couple types of render-instructions (and what they store):
    //     BEAM: 
    //         - drums
    //         - full-beams
    //         - broken-beams
    //         - dots
    //         - length
    //     BEAM-END:
    //         - drums
    //         - dots
    //         - length
    //     FLAG:
    //         - drums
    //         - flags
    //         - dots
    //         - length
    //     REST:
    //         - ticks
    //         - dots
    //         - length
    //     CONTRACT-START:
    //         - ratio
    //         - hooks
    //     CONTRACT-END:
    //     DECORATION:
    //         - decoration
    //     TIME_SIGNATURE:
    //         - numerator
    //         - denomenator
    // 
    // drums: A string array of the (drum) symbolIDs to draw.
    // full-beams: The number (non-zero and positive) of full beams to draw between this instruction and the next instruction (with a stem, full beams go over rests).
    // broken-beams: The same full-beams except for broken-beams. This can be signed, where negative means to draw on the left, and positive to the right. It can also be zero - no broken-beams.
    // dots: The number (zero or positive) of dots that should be drawn after the stem.
    // flags: The number (zero or positive) of flags to draw after the stem.
    // ticks: The number (zero or positive) of ticks to draw on a rest. Zero means it's a crotchet rest.
    // ratio: The length (positive integer) of notes to contracted into one beat. This is the number to be drawn between the start and end.
    // hooks: Should hooks (the lines that show where a contraction has effect) be drawn. This is true or false.
    // length: The fraction of a beat that this group inhabits (e.g. a semiquaver is 0.25). This is used as metadata for stylised spacing when drawing, so need not be technically accurate. It should be non-negative though.
    // decoration:  The (decoration) symbolID of the decoration to draw. 
    // numerator/denomenator: The top and bottom numbers of the time-signature to draw.
    // 
    // BEAMs connect to the next BEAM or BEAM-END, so must be followed by at least one of these.
    // A BEAM-END must follow a BEAM.
    // FLAGs stand alone so should not follow an un-ended BEAM. This means crotchets should be represented using a FLAG with flags=0.
    // Each CONTRACT-START must be closed by a CONTRACT-END, and must be closed before another CONTRACT can start.
    // RESTS and CONTRACTING-START/END can come anywhere between BEAMs and FLAGs.
    // DECORATIONs and TIME_SIGNATUREs cannot come within unended beams.
    // 
    // CONTRACT beams are for contracting-ratios, they say notes inside this beam (of the length given inside ratio) should be contracted so that they last the length of a single beat.
    // 
    //
    // We refer to instructions with a length - BEAMs, BEAM_ENDs, FLAGs, and RESTs - as groups as they are groups of subdivisions.
    
    // Instruction Types
    static get BEAM() {return "BEAM";}  // Declare like this so are immutable.
    static get BEAM_END() {return "BEAM_END";}
    static get FLAG() {return "FLAG";}
    static get REST() {return "REST";}
    static get CONTRACT_START() {return "CONTRACT_START";}
    static get CONTRACT_END() {return "CONTRACT_END";}
    static get DECORATION() {return "DECORATION";}
    static get TIME_SIGNATURE() {return "TIME_SIGNATURE";}

    constructor(type, ...args) {
        // Type should be the value in BEAM, BEAM_END...
        // Args should be passed in the order they are documented in.
        
        this.type = type;
        if (type === RenderInstruction.BEAM) {
            this.drums = Object.freeze(args[0]);
            this.fullBeams = args[1];
            this.brokenBeams = args[2];
            this.dots = args[3];
            this.length = args[4];
        } else if (type === RenderInstruction.BEAM_END) {
            this.drums =Object.freeze(args[0]);
            this.dots = args[1];
            this.length = args[2];
        } else if (type === RenderInstruction.FLAG) {
            this.drums = Object.freeze(args[0]);
            this.flags = args[1];
            this.dots = args[2];
            this.length = args[3];
        } else if (type === RenderInstruction.REST) {
            this.ticks = args[0];
            this.dots = args[1];
            this.length = args[2];
        } else if (type === RenderInstruction.CONTRACT_START) {
            this.ratio = args[0];
            this.hooks = args[1];
        } else if (type === RenderInstruction.CONTRACT_END) {
            // No args taken
        } else if (type === RenderInstruction.DECORATION) {
            this.decoration = args[0];
        } else if (type === RenderInstruction.TIME_SIGNATURE) {
            this.numerator = args[0];
            this.denomenator = args[1];
        } else {
            throw "Unkown type " + type;
        }

        Object.freeze(this);  // So is immutable
    }

    get isGroup() {return [RenderInstruction.BEAM, RenderInstruction.BEAM_END, RenderInstruction.FLAG, RenderInstruction.REST].includes(this.type);}

    get hasDrums() {return [RenderInstruction.BEAM, RenderInstruction.BEAM_END, RenderInstruction.FLAG].includes(this.type);}

    get isContract() {return [RenderInstruction.CONTRACT_START, RenderInstruction.CONTRACT_END].includes(this.type);}
    
    get hasLength() {return [RenderInstruction.BEAM, RenderInstruction.BEAM_END, RenderInstruction.FLAG, RenderInstruction.REST].includes(this.type);}
}

function makeGroupLengthsLegal(length) {
    // For a group length to be legal (i.e. it possible to be notated without the use of (more) rests), we need it to be able to be written as the sum of consecutive powers of 2.
    // E.g. 4 = 4               just a beam or flag or nothing,
    //      3 = 2 + 1           one dot,
    //      6 = 4 + 2           one dot,
    //      7 = 4 + 2 + 1       two dots,
    //      but 9 = 8 + 1       does not work; this would need to be followed by a rest.
    //      And 21 = 16 + 4 + 1 needs two rests.
    
    const legalLengths = new Array();
    
    while (length != 0) {
        // Each iteration, find the largest series `2^k + 2^(k+1) + ... + 2^n` that fits into length
        
        // 2^n is the largest power of two in `length`, so we can floor the log of `length` to find `n`
        const n = Math.floor(Math.log2(length));
        
        // Our series simplifies to `2^(n+1) - 2^k`, we can use this to find `k` by equating it to length
        const k = Math.ceil(Math.log2(Math.pow(2, n+1) - length))
        
        // Then evaluate the series (the legal length of the group we are added (the missing part will be handled in later iterations))
        const series = Math.pow(2, n+1) - Math.pow(2, k)
        legalLengths.push(series);
        // Subtract the series from length as we have accounted for it
        length -= series;
    }
    
    return Object.freeze(legalLengths);
}

function groupSubdivisions(componentId, beatI) {
    // Returns the number of subdivisions that each group (an instruction with length) will take for the given component and beat.
    // This will determine how many groups are required, and split lengths to ensure they can be legally beamed/notated (i.e. this calculates where extra rests are needed).
    // 
    // It returns a frozen array of integers which are the lengths. Each corresponds to a subdivision, but not each subdivision has a length:
    //      The first length - let this be `a` - corresponds to the 0th subdivision.
    //      The second length - `b` - corresponds to the `a`th subdivison.
    //      The third to the `a+b`th subdivison and so on.
    // If a subdivison is empty then it should have a rest, otherwise it should be a group.
    // The lengths will be such that all subdivisions with drums have a length assigned.
    
    const groupLengths = new Array();
    
    let subdivI = 0;
    const subdivCount = ComponentManager.getComponentBeatSubdivisionCount(componentId, beatI);
    while (subdivI < subdivCount) {
        
        // In each iteration we find the length of the group starting at subdivI

        const groupStartSubdivI = subdivI;
        subdivI++;
        
        // Loop until subdivI is at the start of the next group, or at the end of the beat
        while (subdivI < subdivCount && ComponentManager.getComponentSubdivisionDrums(componentId, beatI, subdivI).size == 0) {
            subdivI++;
        }
        
        // So we have a group starting at groupStartSubdivI and ending on (subdivI-1)
        
        const groupLength = subdivI - groupStartSubdivI
        const legalGroupLengths = makeGroupLengthsLegal(groupLength)
        
        groupLengths.push(...legalGroupLengths);
    }
    
    return Object.freeze(groupLengths);
}

function calculateRyhthmInfo(groupLength, subdivisionCount) {
    // Calculates the rhythm information for a group of the given length inside a beat with the given number of subdivisions.
    // This returns {
    //                  beams: int,  // The number of beams/ticks/flags this groups requires attached to its stem
    //                  dots: int    // The number of dots that follow the stem
    //              }
    // 
    // This expects the group length to be a legal length, i.e. it can be written as the sum of consecutive powers of two.
    
    // If we have a non-standard number of subdivisions (not a power of 2) then we notate as if the subdivisions was the highest power of two below what it actually is
    const pretendSubdivisionsCount = Math.pow(2, Math.floor(Math.log2(subdivisionCount)));
    const logPsc = Math.log2(pretendSubdivisionsCount)

    // If `groupLength = 2^n + 2^(n-1) + ... + 2^k`, then `logPsc - n` is the number of beams, and `(n - k)` is the number of dots
    const n = Math.floor(Math.log2(groupLength))  // `2^n` is the highest power so this works
    const k = Math.ceil(Math.log2(Math.pow(2, n+1) - groupLength))  // As the series evaluates to `2^(n+1) - 2^k`
    
    return Object.freeze({beams: logPsc - n, dots: n - k});
}

function getNonEmptySubdivisions(componentId, beatI) {
    // Gets the subdivision-indexes of non-empty (have drums) subdivisions in a given beat and component.
    
    const subdivCount = ComponentManager.getComponentBeatSubdivisionCount(componentId, beatI);
    const nonEmpties = new Array();
    for (let subdivI = 0; subdivI<subdivCount; subdivI++) {
        if (ComponentManager.getComponentSubdivisionDrums(componentId, beatI, subdivI).size != 0) {
            nonEmpties.push(subdivI);
        }
    }
    
    return Object.freeze(nonEmpties);
}


function calculateBeamInfo(l, c, n, nn) {
    // Calculates how many full and broken beams are needed between `c` and `n`. Where `l`, `c`, `n`, and `nn` are the beams required connected to the stems.
    // Returns {fullBeams: int, brokenBeams: int}.
    
    let fullBeams, brokenBeams;
    if (c == n) {  // Both want the same number of beams
        fullBeams = c;
        brokenBeams = 0;
    } else if (c > n && l >= c) {  // c needs more beams than n, but l supplies at least that many to c
        fullBeams = n;
        brokenBeams = 0;
    } else if (c > n && l < c) {  // c needs more beams than n, and l does not supply enough to c
        fullBeams = n;
        // Supply broken beams if there will be more total beams between l and c than between c and n
        if (l < n) {
            brokenBeams = n - c;  // Will be negative (as beams on left side)
        } else { 
            brokenBeams = 0;
        }
    } else if (c < n && nn >= n) {  // c needs less beams than n, but nn supplies at least that many to n
        fullBeams = c;
        brokenBeams = 0;
    } else if (c < n && nn < n) {  // c needs less beams than n, but nn does not supply enough beams to n
        fullBeams = c;
        // Supply broken beams if there will be more total beams between c and n than between n and nn
        if (c > nn) {
            brokenBeams = n - c;  // Will be positive (as beams on right side)
        } else {
            brokenBeams = 0;
        }
    } else {
         throw "None of the beam logic cases worked, this shouldn't be possible, here are the values " + l + " " + c + " " + n + " " + nn;
    }
    
    return {fullBeams: fullBeams, brokenBeams: brokenBeams};
}

function getGcd(...n) {
    // Gets the greatest common denomenator from the given numbers.
    // This expects there to be at least one number given.
    return n.reduce((a, b) => {
        // Euclidean algorithm
        while (b !== 0) {
            [a, b] = [b, a % b];
        }
        return a;
    });
}

function createGroupInstructions(componentId, beatI) {
    // Creates the group instructions for a given beat for a given component.
    // Returns {beatInstructions: Object.freeze(Array<RenderInstruction>), subdivDivisor: int} where the subdivDivisor is the factor by which lengths were reduced.
    
    // Get some preliminary data
    let groupLengths = groupSubdivisions(componentId, beatI);
    let nonEmptySubdivisions = getNonEmptySubdivisions(componentId, beatI);
    const nonEmptyCount = nonEmptySubdivisions.length;
    let subdivCount = ComponentManager.getComponentBeatSubdivisionCount(componentId, beatI);
    
    // Simplify groupLengths and subdivCount by removing common factors
    // This means a beat with 3 subdivsions, but only the first subdivision is non-empty, will not be notated as a dotted-crotchet with a triplet contraction
    const gcd = getGcd(...groupLengths);  // If x|(some group length) then x|subdivCount, so we only need to run for groupLengths
    subdivCount = subdivCount / gcd;
    groupLengths = groupLengths.map(x => x/gcd);
    nonEmptySubdivisions = nonEmptySubdivisions.map(x => x/gcd);
    
    // Do this on the simplified data
    const expandedGroupLengths = groupLengths.map(l => new Array(l).fill(l)).reduce((a, b) => a.concat(b));  // Has an item for each subdivision containing the length of its group
    
    
    // Create the instructions. We need one for each group length
    const instructions = new Array();
    let subdivI = 0;
    let countedNonEmpty = 0;  // Number of non-empties we have processed so far
    let inBeamFlag = false;  // Is there no BEAM instruction || Was a BEAM_END more recent than a BEAM
    for (let groupI = 0; groupI < groupLengths.length; groupI++) {
        const drums = ComponentManager.getComponentSubdivisionDrums(componentId, beatI, subdivI * gcd);  // We are counting simplified subdivisions, we need to scale back up for the component manager
        const groupLength = groupLengths[groupI];
        const rhythmInfo = calculateRyhthmInfo(groupLength, subdivCount);
        
        // Process groupLength to be comparible to other beats (which may have different subdivisionCounts)
        // The easiest way to do this is make the length be a fraction of the beat length
        const processedGroupLength = groupLength / subdivCount;
        
        if (drums.size == 0) {
            // We have a REST
            instructions.push(new RenderInstruction(RenderInstruction.REST, rhythmInfo.beams, rhythmInfo.dots, processedGroupLength));
            
        } else if (countedNonEmpty < nonEmptyCount - 1 && (rhythmInfo.beams > 0 && calculateRyhthmInfo(expandedGroupLengths[nonEmptySubdivisions[countedNonEmpty + 1]], subdivCount).beams > 0)) {  // If at least one more nonEmpty after this, and both require beams
            // We have a BEAM
            
            // How many beams do the adjacent groups each supply / need:
            const l = ((countedNonEmpty == 0) ? 0 : calculateRyhthmInfo(expandedGroupLengths[nonEmptySubdivisions[countedNonEmpty - 1]], subdivCount).beams);
            const c = rhythmInfo.beams;
            const n = (calculateRyhthmInfo(expandedGroupLengths[nonEmptySubdivisions[countedNonEmpty + 1]], subdivCount).beams);  // We can always have the  + 1 as otherwise it won't get into this case
            const nn = ((countedNonEmpty == nonEmptyCount - 2) ? 0 : calculateRyhthmInfo(expandedGroupLengths[nonEmptySubdivisions[countedNonEmpty + 2]], subdivCount).beams);
            
            // Calculate the beam info
            const {fullBeams: fullBeams, brokenBeams: brokenBeams} = calculateBeamInfo(l, c, n, nn);
            
            instructions.push(new RenderInstruction(RenderInstruction.BEAM, drums, fullBeams, brokenBeams, rhythmInfo.dots, processedGroupLength));
            countedNonEmpty++;
            inBeamFlag = true;
            
        } else if (inBeamFlag) {
            // We have a BEAM_END
            instructions.push(new RenderInstruction(RenderInstruction.BEAM_END, drums, rhythmInfo.dots, processedGroupLength))
            countedNonEmpty++;
            inBeamFlag = false;
            
        } else {
            // We have a FLAG
            instructions.push(new RenderInstruction(RenderInstruction.FLAG, drums, rhythmInfo.beams, rhythmInfo.dots, processedGroupLength));
            countedNonEmpty++;
        }
        
        subdivI += groupLength;
    }
    
    return {beatInstructions: Object.freeze(instructions), subdivDivisor: gcd};
}

export function compileScoreComponent(componentId) {
    // Converts the given score-component into a frozen array of RenderInstructions.
    // This implementation will take each beat on its own, so will not beam between beats.
    
    const instructions = new Array();
    
    // Left-Decoration
    const leftDeco = ComponentManager.getComponentLeftDecoration(componentId);
    if (leftDeco !== null) instructions.push(new RenderInstruction(RenderInstruction.DECORATION, leftDeco));
    
    // TIme-signature
    instructions.push(new RenderInstruction(RenderInstruction.TIME_SIGNATURE, 
                                            ComponentManager.getComponentBeatCount(componentId),
                                            ComponentManager.getComponentTimeSignatureDenomenator(componentId)));

    // Convert actual note information to instructions
    const beatCount = ComponentManager.getComponentBeatCount(componentId)
    for (let beatI=0; beatI<beatCount; beatI++) {
        
        // Get instructions for beat
        const {beatInstructions, subdivDivisor} = createGroupInstructions(componentId, beatI);
        
        // Get adjusted subdivisonCount
        const initialSubdivCount = ComponentManager.getComponentBeatSubdivisionCount(componentId, beatI);
        const subdivCount = initialSubdivCount / subdivDivisor;
        
        // Do we need a contract
        const needsContract = Math.log2(subdivCount) % 1 !== 0;
        const needsHooks = beatInstructions.filter(instr => instr.type === RenderInstruction.FLAG).length !== 0 ||
            beatInstructions[0].type === RenderInstruction.REST ||
            beatInstructions[beatInstructions.length - 1].type === RenderInstruction.REST;
        
        // Add instructions to list
        if (needsContract) instructions.push(new RenderInstruction(RenderInstruction.CONTRACT_START, subdivCount, needsHooks));
        instructions.push(...beatInstructions);
        if (needsContract) instructions.push(new RenderInstruction(RenderInstruction.CONTRACT_END));
    }
    
    // Right-Decoration
    const rightDeco = ComponentManager.getComponentRightDecoration(componentId);
    if (rightDeco !== null) instructions.push(new RenderInstruction(RenderInstruction.DECORATION, rightDeco));
    
    return instructions;
}
