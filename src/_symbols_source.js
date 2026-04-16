export const SYMBOLS_SOURCE = [
    // Debug
    "new,drum,debug,0,0,0,0,0,0",

    // Kicks
    "new,drum,kick,5.15,0.35,0.15,2.85,1,path,M0 0 A2.5 1 157.5 0 0 -5 2.5 A2.5 1 157.5 0 0 0 0 M-3.5 1.75 A1 1 157.5 0 0 -1.5 0.75 A1 1 157.5 0 0 -3.5 1.75,2,feet,g-drums",  // The angle is derived from: 180-arctan(2.5/5)=157.5
    "new,drum,hi-hat-kick,5,0,0,5,1,path,M0 0 l-5 5 m5 0 l-5 -5,2,feet,g-drums",
    "modifier,drum,explicit,hi-hat-kick_splash,6,0,1,5,2,path,M0 0 a3.54 3.54 0 0 1 0 5 m-5 0 a3.54 3.54 0 0 1 0 -5,use,hi-hat-kick,2,feet,g-drums",  // The radius is 5*sqrt(2)/2=3.54

    // Snares
    "new,drum,snare,5,0,0,2.5,1,path,M0 0 l-5 2.5,2,g-snares,g-drums",
    "modifier,drum,explicit,snare_off,5.15,0.35,0.15,2.85,1,path,M0 0 A2.5 1 157.5 0 0 -5 2.5 A2.5 1 157.5 0 0 0 0,2,g-snares,g-drums",  // The angle is derived from: 180-arctan(2.5/5)=157.5

    // Toms
    "new,part,p-tom-circle,1,path,M0 0 A1.5 1 157.5 0 0 -5 2.5 A1.5 1 157.5 0 0 0 0",  // The angle is derived from: 180-arctan(2.5/5)=157.5
    "new,drum,high-rack-tom,5.15,1,0.15,3.5,2,path,M0 0 l-2.5 1.25,use,p-tom-circle,2,g-high-rack-toms,g-drums",
    "new,drum,low-rack-tom,5.15,1,0.15,3.5,2,path,M0 0 l-3 1.5,use,p-tom-circle,2,g-low-rack-toms,g-drums",
    "new,drum,high-floor-tom,5.15,1,0.15,3.5,2,path,M0 0 l-4 2,use,p-tom-circle,2,g-high-floor-toms,g-drums",
    "new,drum,low-floor-tom,5.15,1,0.15,3.5,2,path,M0 0 l-4.5 2.25,use,p-tom-circle,2,g-low-floor-toms,g-drums",

    // Hi-Hats
    "new,drum,hi-hat,5,0,0,5,1,path,M0 0 l-5 5 m5 0 l-5 -5,2,g-hi-hats,g-cymbals",  // Base hi-hat is closed
    "modifier,drum,explicit,hi-hat_trashy,6,0,1,5,2,path,M0 0 a3.54 3.54 0 0 1 0 5 m-5 0 a3.54 3.54 0 0 1 0 -5,use,hi-hat,2,g-hi-hats,g-cymbals",  // The radius is 5*sqrt(2)/2=3.54
    "modifier,drum,explicit,hi-hat_open,6,1,1,6,2,path,M 0 0 l -5 5 m 5 0 l -5 -5 M 0 0 a 2.5 2.5 0 0 0 -5 5 a 2.5 2.5 0 0 0 5 -5,use,hi-hat,2,g-hi-hats,g-cymbals",

    // Crashes
    "new,drum,crash,9,2.25,1.5,3.75,1,path,M1.5 0 l-10.5 0 l9 3.75 l-3.75 -6 l-3.75 6 l9 -3.75,3,g-crashes,g-first-crashes,g-cymbals",
    "new,drum,crash-second,9,2.25,1.5,3.75,1,use,crash,3,g-crashes,g-second-crashes,g-cymbals",
    "new,drum,crash-third,9,2.25,1.5,3.75,1,use,crash,3,g-crashes,g-third-crashes,g-cymbals",

    // Effects
    "new,drum,trash,9,2.25,1.5,3.75,1,path,M1.5 0 l-10.5 0 l9 3.75 l-3.75 -6 l-3.75 6 l9 -3.75 A3 1.3 0 0 0 -9 0 A4.5 3 0 0 0 1.5 0,2,g-effects,g-cymbals",
    
    "new,drum,ride,5,0,0,3,1,path,M0 0 l-5 3 m0 -3 l5 3,2,g-effects,g-cymbals",
    
    "new,part,p-triangle,1,path,M0 0 l-5 0 l2.5 -4.33 l2.5 4.33",
    "modifier,drum,explicit,ride_bell,5,4.33,0,0,1,use,p-triangle,2,g-effects,g-cymbals",  // The height is derived from 5/2*tan(60)=4.33
    "new,drum,cow-bell,5,4.33,0,0,2,use,p-triangle,path,M0 0 l-3.46 -2 L-2.5 0 l0 -4.33,2,g-effects,g-cymbals",  // 4*cos(30)=-3.46, 4*sin(30)=-2

    // Flams
    "new,part,p-flam-sign,1,path,M-0.5 -1.5 A0.8 1 0 0 0 1 1",
    "modifier,drum,auto,flam,2,+*drums,-feet,+1,0,0,+1.5,0,0,3,push-transform,translate(${-parent_size_left} ${parent_size_down}),use,p-flam-sign,pop-transform,1,flamed",

    // Ghosts
    "modifier,drum,auto,ghost,1,+*drums,+2,+1,+2,+1,0,0,1,path,M${-parent_size_left - 1} ${-parent_size_up - 1} A10 10 0 0 0 ${-parent_size_left - 1} ${parent_size_down + 1} M${parent_size_right + 1} ${parent_size_down + 1} A10 10 0 0 0 ${parent_size_right + 1} ${-parent_size_up - 1},1,ghosted",

    // Accents
    "modifier,drum,auto,accent,2,+*drums,-ghosted,~1,+2,~1,0,0,0,1,path,M${-base_size_left - 1} ${-parent_size_up} L${(-base_size_left + base_size_right) / 2} ${-parent_size_up - 2} L${base_size_right + 1} ${0 - parent_size_up},1,accented",

    // Decorations
    "new,decoration,bar-end,0,1,1,,1,,right,1,path,M0 ${-height / 2} L0 ${+height / 2}",
    "new,decoration,end,3,10,0,,0,,right,3,path,M0 ${-5} L0 ${+5},circle,-2,-3,1,circle,-2,3,1",
    "new,decoration,repeat-end,6,16,2,,2,0,right,4,push-transform,translate(-2 0),use,end,pop-transform,path,M0 ${-height / 2 + 1.5} L0 ${+height / 2 - 1.5} M0 ${+height / 2 - 2} l-6 2 M0 ${-height / 2 + 2} l-6 -2",

    "new,decoration,start,3,10,0,,0,,left,3,push-transform,scale(-1 1) translate(3 0),use,end,pop-transform",
    "new,decoration,repeat-start,6,16,2,,2,0,left,3,push-transform,scale(-1 1) translate(6 0),use,repeat-end,pop-transform",

    // Constraints
    "constraint,drum,g-low-floor-toms,feet,0",
    "constraint,drum,g-high-floor-toms,g-low-floor-toms,2",
    "constraint,drum,g-snares,g-high-floor-toms,0",
    "constraint,drum,g-low-rack-toms,g-snares,2",
    "constraint,drum,g-high-rack-toms,g-low-rack-toms,2",
    "constraint,drum,g-hi-hats,g-high-rack-toms,0",
    "constraint,drum,g-effects,g-hi-hats,0",
    "constraint,drum,g-crashes,g-effects,0",

    "constraint,drum,g-snares,feet,5",
    "constraint,drum,g-low-rack-toms,g-high-floor-toms,2",

    "constraint,drum,g-first-crashes,g-effects,4",
    "constraint,drum,g-second-crashes,g-effects,2",
    "constraint,drum,g-first-crashes,g-hi-hats,4",
    "constraint,drum,g-second-crashes,g-hi-hats,2",

    "constraint,drum,g-first-crashes,g-second-crashes,2",
    "constraint,drum,g-second-crashes,g-third-crashes,2",

    "constraint,drum,g-cymbals,g-drums,4",


    


].join(",");
// TODO: We need a better selection system (better patterns). Some set-notation would probably do it
// TODO: Hi-Hat kick renders above kick. This is not correct
