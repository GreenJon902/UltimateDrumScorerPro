import {ComponentManager} from "./componentManager.js";

class RenderInstruction {
    // Render instructions are produced by preRenderScoreComponent and are used to tell renderScoreComponent what to draw.
    //
    // There are a couple types of render-instructions (and what they store):
    //     GROUP: 
    //         - drumIDs
    //         - full-beams
    //         - broken-beams
    //         - dots
    //         - length
    //     GROUP-END:
    //         - drumIDs
    //         - dots
    //         - length
    //     FLAG:
    //         - drumIDs
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
    //         - decorationID
    // 
    // drumIDs: A string array of the (drum) symbolIDs to draw.
    // full-beams: The number (non-zero and positive) of full beams to draw between this instruction and the next instruction (with a stem, full beams go over rests).
    // broken-beams: The same full-beams except for broken-beams. This can be signed, where negative means to draw on the left, and positive to the right. It can also be zero - no broken-beams. If dots != 0 then this cannot be negative.
    // dots: The number (zero or positive) of dots that should be drawn after the stem. If broken-beams is negative (broken-beams on the left) then this must be 0 (no dots).
    // flags: The number (zero or positive) of flags to draw after the stem.
    // ticks: The number (zero or positive) of ticks to draw on a rest. Zero means it's a crotchet rest.
    // ratio: The length (positive integer) of notes to contracted into one beat. This is the number to be drawn between the start and end.
    // hooks: Should hooks (the lines that show where a contraction has effect) be drawn. This is true or false.
    // length: The relative duration of a note compared to the rest of the notes. If a note is twice as long then it should have double the duration.
    // decoration:  The (decoration) symbolID of the decoration to draw. 
    // 
    // GROUPs connect to the next GROUP or GROUP-END, so must be followed by at least one of these.
    // A GROUP-END must follow a GROUP.
    // FLAGs stand alone so should not follow an un-ended GROUP. This means crotchets should be represented using a FLAG with flags=0.
    // Each CONTRACT-START must be closed by a CONTRACT-END, and must be closed before another CONTRACT can start.
    // RESTS and CONTRACTING-START/END can come anywhere between GROUPs and FLAGs.
    // DECORATIONs cannot come within unended groups.
    // 
    // CONTRACT groups are for contracting-ratios, they say notes inside this group (of the length given inside ratio) should be contracted so that they last the length of a single beat.
    
    // Instruction Types
    static get GROUP() {return "GROUP";}  // Declare like this so are immutable.
    static get GROUP_END() {return "GROUP_END";}
    static get FLAG() {return "FLAG";}
    static get REST() {return "REST";}
    static get CONTRACT_START() {return "CONTRACT_START";}
    static get CONTRACT_END() {return "CONTRACT_END";}
    static get DECORATION() {return "DECORATION";}

    constructor(type, ...args) {
        // Type should be the value in GROUP, GROUP_END...
        // Args should be passed in the order they are documented in.
        
        this.type = type;
        if (type === RenderInstruction.GROUP) {
            this.drums = args[0];
            this.full_beams = args[1];
            this.broken_beams = args[2];
            this.dots = args[3];
            this.length = args[4];
        } else if (type === RenderInstruction.GROUP_END) {
            this.drums = args[0];
            this.dots = args[1];
            this.length = args[2];
        } else if (type === RenderInstruction.FLAG) {
            this.drums = args[0];
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
        } else if (type === RenderInstruction.DECORATION) {
            this.decoration = args[0];
        } else {
            throw "Unkown type " + type;
        }

        Object.freeze(this);  // So is immutable
    }
}

