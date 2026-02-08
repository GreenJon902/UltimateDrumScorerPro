export const SYMBOLS_SOURCE = [
    // Kicks
    "new,drum,kick,5.15,0.35,0.15,2.85,1,path,M0 0 A2.5 1 157.5 0 0 -5 2.5 A2.5 1 157.5 0 0 0 0 M-3.5 1.75 A1 1 157.5 0 0 -1.5 0.75 A1 1 157.5 0 0 -3.5 1.75,1,feet",  // The angle is derived from: 180-arctan(2.5/5)=157.5
    "new,drum,hi-hat-kick,5,0,0,5,1,path,M0 0 l-5 5 m5 0 l-5 -5,1,feet",
    "modifier,drum,explicit,hi-hat-kick_splash,6,0,1,5,2,path,M0 0 a3.54 3.54 0 0 1 0 5 m-5 0 a3.54 3.54 0 0 1 0 -5,use,hi-hat-kick,1,feet",  // The radius is 5*sqrt(2)/2=3.54

    // Snares
    "new,drum,snare,5,0,0,2.5,1,path,M0 0 l-5 2.5,0",
    "modifier,drum,explicit,snare_off,5.15,0.35,0.15,2.85,1,path,M0 0 A2.5 1 157.5 0 0 -5 2.5 A2.5 1 157.5 0 0 0 0,0",  // The angle is derived from: 180-arctan(2.5/5)=157.5

    // Toms
    "new,part,p-tom-circle,1,path,M0 0 A1.5 1 157.5 0 0 -5 2.5 A1.5 1 157.5 0 0 0 0",  // The angle is derived from: 180-arctan(2.5/5)=157.5
    "new,drum,high-rack-tom,5.15,1,0.15,3.5,2,path,M0 0 l-2.5 1.25,use,p-tom-circle,0",
    "new,drum,low-rack-tom,5.15,1,0.15,3.5,2,path,M0 0 l-3 1.5,use,p-tom-circle,0",
    "new,drum,high-floor-tom,5.15,1,0.15,3.5,2,path,M0 0 l-4 2,use,p-tom-circle,0",
    "new,drum,low-floor-tom,5.15,1,0.15,3.5,2,path,M0 0 l-4.5 2.25,use,p-tom-circle,0",

    // Hi-Hats
    "new,drum,hi-hat,5,0,0,5,1,path,M0 0 l-5 5 m5 0 l-5 -5,0",  // Base hi-hat is closed
    "modifier,drum,explicit,hi-hat_trashy,6,0,1,5,2,path,M0 0 a3.54 3.54 0 0 1 0 5 m-5 0 a3.54 3.54 0 0 1 0 -5,use,hi-hat,0",  // The radius is 5*sqrt(2)/2=3.54
    "modifier,drum,explicit,hi-hat_open,6,1,1,6,2,path,M 0 0 l -5 5 m 5 0 l -5 -5 M 0 0 a 2.5 2.5 0 0 0 -5 5 a 2.5 2.5 0 0 0 5 -5,use,hi-hat,0",

    // Crashes
    "new,drum,crash,9,2.25,1.5,3.75,1,path,M1.5 0 l-10.5 0 l9 3.75 l-3.75 -6 l-3.75 6 l9 -3.75,0",
    "new,drum,crash-second,9,2.25,1.5,3.75,1,use,crash,0",
    "new,drum,crash-third,9,2.25,1.5,3.75,1,use,crash,0",

    // Effects
    "new,drum,trash,9,2.25,1.5,3.75,1,path,M1.5 0 l-10.5 0 l9 3.75 l-3.75 -6 l-3.75 6 l9 -3.75 A3 1.3 0 0 0 -9 0 A4.5 3 0 0 0 1.5 0,0",
    
    "new,drum,ride,5,0,0,3,1,path,M0 0 l-5 3 m0 -3 l5 3,0",
    
    "new,part,p-triangle,1,path,M0 0 l-5 0 l2.5 -4.33 l2.5 4.33",
    "modifier,drum,explicit,ride_bell,5,4.33,0,0,1,use,p-triangle,0",  // The height is derived from 5/2*tan(60)=4.33
    "new,drum,cow-bell,5,4.33,0,0,2,use,p-triangle,path,M0 0 l-3.46 -2 L-2.5 0 l0 -4.33,0",  // 4*cos(30)=-3.46, 4*sin(30)=-2

    // Flams
    "new,part,p-flam-sign,1,path,M-0.5 -1.5 A0.8 1 0 0 0 1 1",
    "modifier,drum,auto,flam,2,+*drums,-feet,+1,0,0,+1.5,0,0,3,push-transform,translate(${0 - parent_size_left} ${parent_size_down}),use,p-flam-sign,pop-transform,1,flamed",

    // Ghosts
    "modifier,drum,auto,ghost,1,+*drums,+2,+1,+2,+1,0,0,1,path,M${0 - parent_size_left - 1} ${0 - parent_size_up - 1} A10 10 0 0 0 ${0 - parent_size_left - 1} ${parent_size_down + 1} M${parent_size_right + 1} ${parent_size_down + 1} A10 10 0 0 0 ${parent_size_right + 1} ${0 - parent_size_up - 1},1,ghosted",

    // Accents
    "modifier,drum,auto,accent,2,+*drums,-ghosted,+1,+2,+1,0,0,0,1,path,M${0 - parent_size_left - 1} ${0 - parent_size_up} L${0 - parent_size_left + parent_size_right / 2} ${0 - parent_size_up - 2} L${parent_size_right + 1} ${0 - parent_size_up},1,accented",  // TODO: Don't take width from flam into account

    // Decorations
    "new,decoration,bar-end,1,10,,,,right,1,path,M-0.5 ${drum_center_y - height / 2} L-0.5 ${drum_center_y + height / 2}"


].join(",");
// TODO: "modifier,drum,auto,ghost,*,0,0,0,0,0,0,1,path,,0" does not crash
// TODO: In the expression parser, add support for unary operations + and -
// TODO: SVG Instructions with brackets (in the format things) cause a recursion depth error
// TODO: SVG Instruction format thing parsing does not work - seems to parse `a + b / 2` as `(a + b) / 2`)
// TODO: We need a better selection system (better patterns). Some set-notation would probably do it



